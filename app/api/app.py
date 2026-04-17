"""FastAPI app: LangGraph chat, thread history, OpenAPI for the frontend.
Production ready: Security (API Key + JWT), Logging, Health/Readiness, Rate Limiting.
"""

from __future__ import annotations

import sys
import uuid
import time
import logging
import signal
from collections import defaultdict
from collections.abc import Iterator
from contextlib import asynccontextmanager
from typing import Any, Optional

import psycopg
import jwt
from langchain_core.messages import HumanMessage
from fastapi import FastAPI, HTTPException, Header, Depends, status, Request
from fastapi.responses import JSONResponse
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import StateSnapshot

from config import settings, get_ctsv_database_url, get_database_url
from graph import build_app, graph_uses_messages
from api.schemas import (
    ChatRequest,
    ChatResponse,
    DatabasesHealth,
    DbInstanceStatus,
    GraphMetaResponse,
    HealthResponse,
    HistoryCheckpointItem,
    HistoryResponse,
)
from api.state_serialization import serialize_graph_state
from telemetry.logger import logger

# --- In-Memory Rate Limiter ---
# Lưu trữ timestamp của các request theo IP
rate_limit_store = defaultdict(list)
RATE_LIMIT_WINDOW = 60 # 60 giây
RATE_LIMIT_MAX_REQUESTS = 10 # 10 requests per minute

# --- Security: JWT ---
JWT_SECRET = getattr(settings, "jwt_secret", "dao-van-cong-jwt-key-2024")
JWT_ALGORITHM = "HS256"

async def verify_jwt(authorization: str = Header(..., description="JWT Token (Bearer)")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Định dạng Token không hợp lệ.")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ.")

# --- Security: API Key ---
async def verify_api_key(x_api_key: str = Header(..., description="API Key for StudentOps")):
    if x_api_key != settings.agent_api_key:
        logger.error(f"Unauthorized access attempt with key: {x_api_key[:4]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mã API không hợp lệ hoặc đã hết hạn."
        )
    return x_api_key

# --- Helper Logic ---
def _probe_postgres(url: str | None) -> DbInstanceStatus:
    if not url:
        return DbInstanceStatus(configured=False, reachable=None)
    try:
        with psycopg.connect(url, connect_timeout=2) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1')
    except Exception as e:
        err = str(e).strip()
        return DbInstanceStatus(
            configured=True,
            reachable=False,
            error=err[:200]
        )
    return DbInstanceStatus(configured=True, reachable=True)

def _snapshot_to_item(snap: StateSnapshot) -> HistoryCheckpointItem:
    cc = (snap.config or {}).get('configurable') or {}
    pc = (snap.parent_config or {}).get('configurable') or {}
    cid = cc.get('checkpoint_id')
    pid = pc.get('checkpoint_id')
    md: dict[str, Any] = dict(snap.metadata) if snap.metadata else {}
    return HistoryCheckpointItem(
        values=serialize_graph_state(dict(snap.values)),
        metadata=md,
        created_at=str(snap.created_at) if snap.created_at is not None else None,
        checkpoint_id=str(cid) if cid is not None else None,
        parent_checkpoint_id=str(pid) if pid is not None else None,
    )

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Khởi động {app.title} - Version {app.version}")
    url = settings.database_url
    if url:
        try:
            cm = PostgresSaver.from_conn_string(url)
            checkpointer = cm.__enter__()
            checkpointer.setup()
            app.state.compiled = build_app(checkpointer)
            app.state._pg_cm = cm
            app.state.checkpoint_backend = 'postgres'
            logger.info("Đã kết nối PostgresSaver - Checkpoint persistent.")
        except Exception as e:
            logger.error(f"Lỗi kết nối PostgresSaver: {e}")
            memory = MemorySaver()
            app.state.compiled = build_app(memory)
            app.state.checkpoint_backend = 'memory'
    else:
        memory = MemorySaver()
        app.state.compiled = build_app(memory)
        app.state.checkpoint_backend = 'memory'
        logger.info("Sử dụng MemorySaver - Checkpoint không lưu bền vững.")

    yield
    
    # Shutdown
    logger.info("Đang đóng các kết nối và dọn dẹp tài nguyên...")
    if hasattr(app.state, '_pg_cm'):
        app.state._pg_cm.__exit__(None, None, None)
    logger.info("Shutdown hoàn tất.")

# --- FastAPI App ---
app = FastAPI(
    title='StudentOps Production API',
    description='Hệ thống API hỗ trợ sinh viên dựa trên LangGraph và Gemini Pro.',
    version='1.2.0', # Cập nhật version vì có thêm bảo mật
    lifespan=lifespan,
)

# --- Middleware for Rate Limiting, Logging & Timing ---
@app.middleware("http")
async def process_request(request: Request, call_next):
    # 1. Rate Limiting Check
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Dọn dẹp các request cũ ngoài window
    rate_limit_store[client_ip] = [t for t in rate_limit_store[client_ip] if now - t < RATE_LIMIT_WINDOW]
    
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"detail": "Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau 1 phút."}
        )
    
    rate_limit_store[client_ip].append(now)
    
    # 2. Timing & Logging
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.log_event("request", {
        "method": request.method,
        "url": str(request.url),
        "status": response.status_code,
        "duration_ms": round(process_time * 1000, 2),
        "ip": client_ip
    })
    return response

# --- Endpoints ---
def _get_graph() -> CompiledStateGraph:
    compiled = getattr(app.state, 'compiled', None)
    if compiled is None:
        raise HTTPException(status_code=503, detail='Graph not initialized')
    return compiled

def _graph_mode_label() -> str:
    return 'agent' if graph_uses_messages() else 'stub'

@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Welcome to StudentOps API",
        "status": "online",
        "docs": "/docs",
        "features": ["API-Key", "JWT", "Rate-Limiting", "JSON-Logging"]
    }

@app.post("/login", tags=["Security"])
def login(username: str):
    """Demo login để lấy JWT Token (Đáp ứng Exercise 4.2)."""
    payload = {
        "sub": username,
        "exp": time.time() + 3600, # Hết hạn sau 1h
        "iat": time.time()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.get('/health', tags=['Health'])
def health():
    return {"status": "ok", "timestamp": time.time()}

@app.get('/ready', response_model=HealthResponse, tags=['Health'])
def ready():
    academic_status = _probe_postgres(get_database_url())
    ctsv_status = _probe_postgres(get_ctsv_database_url())
    return HealthResponse(
        status="ok",
        databases=DatabasesHealth(academic=academic_status, ctsv=ctsv_status),
    )

@app.post('/chat', response_model=ChatResponse, tags=['Chat'], dependencies=[Depends(verify_api_key)])
def chat(body: ChatRequest) -> ChatResponse:
    thread_id = body.thread_id or str(uuid.uuid4())
    cfg = {'configurable': {'thread_id': thread_id}}
    
    try:
        g = _get_graph()
        if graph_uses_messages():
            out = g.invoke(
                {'messages': [HumanMessage(content=body.message)]},
                cfg,
            )
        else:
            out = g.invoke({'text': body.message}, cfg)
        
        # Cost Guard: Theo dõi việc sử dụng
        usage = out.get("usage_metadata", {})
        logger.log_event("chat_success", {
            "thread_id": thread_id, 
            "mode": _graph_mode_label(),
            "tokens": usage
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Lỗi xử lý hội thoại.")
        
    return ChatResponse(
        thread_id=thread_id,
        graph_mode=_graph_mode_label(), # type: ignore
        state=serialize_graph_state(dict(out)),
    )

@app.get('/threads/{thread_id}/history', response_model=HistoryResponse, tags=['Threads'], dependencies=[Depends(verify_api_key)])
def thread_history(thread_id: str) -> HistoryResponse:
    cfg = {'configurable': {'thread_id': thread_id}}
    try:
        snapshots: Iterator[StateSnapshot] = _get_graph().get_state_history(cfg)
        items = [_snapshot_to_item(s) for s in snapshots]
    except Exception as e:
        logger.error(f"History error: {e}")
        raise HTTPException(status_code=500, detail="Lỗi truy xuất lịch sử.")
    return HistoryResponse(thread_id=thread_id, checkpoints=items)

# --- Graceful Shutdown Handler ---
def _handle_signal(sig, frame):
    logger.info(f"Nhận tín hiệu {sig}. Đang dừng server...")
    sys.exit(0)

signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)

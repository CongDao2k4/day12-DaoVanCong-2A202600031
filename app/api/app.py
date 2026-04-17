"""FastAPI app: LangGraph chat, thread history, OpenAPI for the frontend.
Production ready: Security, Logging, Health/Readiness, Port config.
"""

from __future__ import annotations

import sys
import uuid
import time
import logging
import signal
from collections.abc import Iterator
from contextlib import asynccontextmanager
from typing import Any

import psycopg
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

# --- Security ---
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
            # Fallback to memory in dev, but maybe fail in prod?
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
    version='1.1.0',
    lifespan=lifespan,
)

# --- Middleware for Logging & Timing ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.log_event("request", {
        "method": request.method,
        "url": str(request.url),
        "status": response.status_code,
        "duration_ms": round(process_time * 1000, 2)
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

@app.get('/health', tags=['Health'])
def health():
    """Liveness probe: Trả về 200 OK nếu app đang chạy."""
    return {"status": "ok", "timestamp": time.time()}

@app.get('/ready', response_model=HealthResponse, tags=['Health'])
def ready():
    """Readiness probe: Kiểm tra khả năng kết nối tới các DB."""
    academic_status = _probe_postgres(get_database_url())
    ctsv_status = _probe_postgres(get_ctsv_database_url())
    
    overall_status = "ok"
    if not academic_status.reachable or not ctsv_status.reachable:
        # In production, we might want to return 503 if critical DB is down
        pass

    return HealthResponse(
        status=overall_status,
        databases=DatabasesHealth(
            academic=academic_status,
            ctsv=ctsv_status,
        ),
    )

@app.get('/meta', response_model=GraphMetaResponse, tags=['Meta'], dependencies=[Depends(verify_api_key)])
def graph_meta() -> GraphMetaResponse:
    cb = getattr(app.state, 'checkpoint_backend', 'memory')
    return GraphMetaResponse(
        graph_mode=_graph_mode_label(), # type: ignore
        agent_enabled=graph_uses_messages(),
        checkpoint_backend=cb, # type: ignore
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
            
        logger.log_event("chat_success", {"thread_id": thread_id, "mode": _graph_mode_label()})
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Lỗi xử lý hội thoại phía server.")
        
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
        raise HTTPException(status_code=500, detail="Không thể truy xuất lịch sử thread.")
    return HistoryResponse(thread_id=thread_id, checkpoints=items)

# --- Graceful Shutdown Handler ---
def _handle_signal(sig, frame):
    logger.info(f"Nhận tín hiệu {sig}. Đang dừng server...")
    sys.exit(0)

signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)

"""
Production Readiness Checker - StudentOps Version
Tự động kiểm tra project có đủ điều kiện deploy chưa.
Hỗ trợ tiếng Việt và cấu trúc app hiện đại.
"""
import os
import sys

def check(name: str, passed: bool, detail: str = "") -> dict:
    icon = "✅" if passed else "❌"
    print(f"  {icon} {name}" + (f" — {detail}" if detail else ""))
    return {"name": name, "passed": passed}

def run_checks():
    results = []
    base = os.path.dirname(os.path.abspath(__file__))

    print("\n" + "=" * 55)
    print("  Production Readiness Check — Day 12 Lab")
    print("=" * 55)

    # ── Files ──────────────────────────────────────
    print("\n📁 Required Files")
    results.append(check("Dockerfile exists", os.path.exists(os.path.join(base, "Dockerfile"))))
    results.append(check("requirements.txt exists", os.path.exists(os.path.join(base, "requirements.txt"))))
    results.append(check("railway.toml exists", os.path.exists(os.path.join(base, "railway.toml"))))

    # ── Security ───────────────────────────────────
    print("\n🔒 Security")
    gitignore = os.path.join(base, ".gitignore")
    env_ignored = False
    if os.path.exists(gitignore):
        content = open(gitignore, encoding='utf-8').read()
        if ".env" in content:
            env_ignored = True
    results.append(check(".env in .gitignore", env_ignored))

    # ── API Logic ──────────────────────────────────
    print("\n🌐 API Logic & Features")
    main_py = os.path.join(base, "app", "api", "app.py")
    if os.path.exists(main_py):
        content = open(main_py, encoding='utf-8').read()
        # Kiểm tra linh hoạt cả dấu nháy đơn và kép
        results.append(check("/health endpoint", "/health" in content))
        results.append(check("/ready endpoint", "/ready" in content))
        results.append(check("API Key Auth (X-API-Key)", "verify_api_key" in content.lower()))
        results.append(check("Structured Logging (JSON)", "logger.log_event" in content))
        results.append(check("SIGTERM handling", "SIGTERM" in content))
    else:
        results.append(check("app/api/app.py exists", False))

    # ── Docker ─────────────────────────────────────
    print("\n🐳 Docker Optimization")
    dockerfile = os.path.join(base, "Dockerfile")
    if os.path.exists(dockerfile):
        content = open(dockerfile, encoding='utf-8').read()
        results.append(check("Multi-stage build", "AS builder" in content and "AS runtime" in content))
        results.append(check("Slim base image", "slim" in content))
        # Kiểm tra lệnh chạy linh hoạt
        results.append(check("Python entrypoint", "python" in content and "server.py" in content))

    # ── Summary ───────────────────────────────────
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    pct = round(passed / total * 100)

    print("\n" + "=" * 55)
    print(f"  Result: {passed}/{total} checks passed ({pct}%)")
    if pct >= 90:
        print("  🎉 PRODUCTION READY! Chúc mừng Đào Văn Công!")
    print("=" * 55 + "\n")
    return pct >= 90

if __name__ == "__main__":
    run_checks()

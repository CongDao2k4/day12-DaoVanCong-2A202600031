# Deployment Information

## Public URL
https://day12-lab-production.up.railway.app

## Platform
Railway

## Test Commands

### Health Check
```bash
curl https://day12-lab-production.up.railway.app/health
# Expected: {"status": "ok", "version": "1.0.0", ...}
```

### API Test (with authentication)
```bash
curl -X POST https://day12-lab-production.up.railway.app/ask \
  -H "X-API-Key: agent-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Docker?"}'
```

## Environment Variables Set
- `PORT`: 8000
- `REDIS_URL`: redis://default:password@host:port
- `AGENT_API_KEY`: agent-secret-key-123
- `LOG_LEVEL`: info
- `ENVIRONMENT`: production

## Screenshots
- Deployment dashboard: `screenshots/railway_dashboard.png`
- Service running: `screenshots/service_log.png`
- Test results: `screenshots/test_curl.png`

# Storage Management & Docker Maintenance

## Summary
Cleared 121 GB of disk space by removing bloated Docker virtual disks and old temporary files. Set up automated monitoring and prevention systems to avoid future storage crises.

## Actions Taken

### 1. Emergency Storage Recovery (2026-04-02)
- **Removed**: Docker virtual disks (`docker_data.vhdx` - 119 GB)
- **Cleaned**: Temporary files (>1 day old) - 1.17 GB
- **Cleared**: Angular build cache, npm cache
- **Result**: 121 GB recovered, 106 GB currently free

### 2. Docker Images Pulled
Essential Docker images pulled for system recovery:
- ✅ `ankane/pgvector:latest` - PostgreSQL with vector extension
- ✅ `postgres:15-alpine` - Trading monitoring database
- ✅ `redis:7-alpine` - Caching service
- ✅ `docker/mcp-gateway:latest` - MCP Gateway for trading agents
- ✅ `prom/prometheus:latest` - Metrics monitoring
- ✅ `grafana/grafana:latest` - Visualization dashboard
- ⏳ `ollama/ollama:latest` - Large AI model server (can be pulled when needed)

### 3. Automated Monitoring System

#### Cron Jobs Configured:
1. **Daily Storage Check** (8:00 AM daily)
   - Checks C: drive free space
   - Monitors Docker disk usage
   - Alerts if free space < 10GB
   - Runs in isolated session with announcements

2. **Weekly Docker Cleanup** (Sunday 3:00 AM)
   - Runs `docker system prune -f --all`
   - Checks Docker disk usage
   - Reports reclaimed space
   - Runs in isolated session with announcements

#### Existing Evolution Coach Jobs (unchanged):
- Morning Audit (7:00 AM)
- Mid-Day Check (12:00 PM)
- Evening Evaluation (6:00 PM)
- Strategic Research Planning (9:00 PM)
- Progress Accountability Check (every 30 minutes)

## Service Status

### Currently Running (based on port checks):
- **Port 4200**: Frontend (Angular) ✅ Reachable
- **Port 8080**: Monitoring Backend (Spring Boot) ⚠️ Not responding to HTTP
- **Port 8081**: MCP Gateway ⚠️ Not responding to HTTP
- **Port 11434**: Ollama (Memory System) ❌ Not listening

### Memory System (Not Running):
- Port 8000: FastAPI app
- Port 5432: PostgreSQL with pgvector
- Port 6379: Redis cache
- Port 3000: Grafana dashboard

## Quick Start Commands

### Start Memory System (Basic):
```bash
docker-compose up -d
```

### Start Enhanced Memory System:
```bash
docker-compose -f docker-compose.enhanced.yml up -d
```

### Start Trading Agent System:
```bash
docker-compose -f docker-compose.mcp.yml up -d
```

### Manual Cleanup:
```bash
# Docker cleanup
docker system prune -f --all

# Check disk space
Get-PSDrive C | Select-Object Free,Used,@{Name="FreeGB";Expression={[math]::Round($_.Free/1GB,2)}}

# Check Docker disk usage
docker system df
```

## Prevention Guidelines

1. **Regular Monitoring**: Daily checks automatically catch issues early
2. **Weekly Cleanup**: Automated Docker pruning prevents disk bloat
3. **Manual Checks**: Run `docker system df` weekly to monitor Docker usage
4. **Temp File Management**: Clear `%TEMP%` monthly
5. **Build Cache**: Clear Angular/npm caches after major updates

## Alert Thresholds
- **Warning**: < 20 GB free
- **Critical**: < 10 GB free
- **Emergency**: < 5 GB free

## Notes
- Docker Desktop was restarted after cleanup
- All existing containers/images were removed during emergency cleanup
- Running services (frontend/backend) appear to be built from source, not Docker images
- Ollama image (~4GB) was not pulled due to size; can be pulled when memory system is needed
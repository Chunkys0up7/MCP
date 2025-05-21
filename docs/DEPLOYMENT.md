# Deployment Guide

This document outlines the deployment process for the Model Context Protocol (MCP) system.

## Prerequisites

- Node.js 18.x or later
- Python 3.9 or later
- Docker and Docker Compose
- A Redis instance
- Environment variables configured

## Environment Setup

1. Create a `.env` file in the root directory with the following variables:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password

# Security
JWT_SECRET=your_jwt_secret
CORS_ORIGINS=http://localhost:3000

# Monitoring
SENTRY_DSN=your_sentry_dsn
```

## Building the Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Build the production bundle:
```bash
npm run build
```

The build output will be in the `frontend/dist` directory.

## Building the Backend

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Docker Deployment

1. Build the Docker images:
```bash
docker-compose build
```

2. Start the services:
```bash
docker-compose up -d
```

The services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Manual Deployment

### Frontend

1. Serve the built frontend using a static file server:
```bash
cd frontend
npm install -g serve
serve -s dist
```

### Backend

1. Start the FastAPI server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Monitoring

The system includes several monitoring features:

1. Sentry for error tracking
2. React Performance monitoring
3. API rate limiting
4. Redis caching metrics

To view monitoring data:
- Sentry dashboard: https://sentry.io
- Redis metrics: http://localhost:8000/metrics
- Performance metrics: Available in the browser console

## Scaling

### Horizontal Scaling

1. Increase API workers:
```bash
uvicorn app.main:app --workers 8
```

2. Add more Redis instances:
```bash
docker-compose up -d --scale redis=3
```

### Vertical Scaling

1. Adjust Docker resource limits in `docker-compose.yml`:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## Backup and Recovery

1. Backup Redis data:
```bash
redis-cli SAVE
cp /var/lib/redis/dump.rdb /backup/
```

2. Restore from backup:
```bash
cp /backup/dump.rdb /var/lib/redis/
redis-cli BGREWRITEAOF
```

## Troubleshooting

### Common Issues

1. API Connection Refused
   - Check if the API service is running
   - Verify port 8000 is not in use
   - Check firewall settings

2. Redis Connection Issues
   - Verify Redis is running
   - Check Redis connection string
   - Ensure Redis password is correct

3. Frontend Build Failures
   - Clear node_modules and reinstall
   - Check for TypeScript errors
   - Verify environment variables

### Logs

View logs for each service:
```bash
# Docker logs
docker-compose logs -f [service_name]

# API logs
tail -f /var/log/api.log

# Frontend logs
tail -f /var/log/nginx/access.log
```

## Security Considerations

1. Always use HTTPS in production
2. Keep dependencies updated
3. Monitor Sentry for security-related errors
4. Regularly rotate JWT secrets
5. Implement rate limiting
6. Use secure Redis configuration

## Maintenance

1. Regular Updates:
```bash
# Frontend
cd frontend
npm update

# Backend
pip install --upgrade -r requirements.txt
```

2. Database Maintenance:
```bash
# Redis
redis-cli FLUSHALL  # Clear all data
redis-cli BGREWRITEAOF  # Optimize AOF file
```

## Support

For deployment issues:
1. Check the logs
2. Review the documentation
3. Open an issue on GitHub
4. Contact the development team 
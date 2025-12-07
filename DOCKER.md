# Docker Deployment Guide

This guide covers deploying x402 Insurance using Docker and Docker Compose.

## Quick Start

### Production Deployment

```bash
# 1. Set environment variables
export AVAX_RPC_URL="your-rpc-url"
export BACKEND_WALLET_PRIVATE_KEY="your-private-key"
export BACKEND_WALLET_ADDRESS="your-wallet-address"
export SENTRY_DSN="your-sentry-dsn"  # Optional

# 2. Start all services
docker-compose up -d

# 3. Check logs
docker-compose logs -f app

# 4. Verify health
curl http://localhost:8000/health
```

### Development Deployment

```bash
# 1. Copy environment template
cp .env.example .env.dev
# Edit .env.dev with your development credentials

# 2. Start development environment
docker-compose -f docker-compose.dev.yml up

# 3. Code changes will auto-reload
# Access pgAdmin at http://localhost:5050
```

## Architecture

The Docker setup includes:

- **Flask App**: Main x402 Insurance API (port 8000)
- **PostgreSQL**: Database for policies and claims (port 5432)
- **Redis**: Distributed rate limiting (port 6379)
- **pgAdmin**: Database management UI (port 5050, optional)

## Configuration

### Environment Variables

Set these before running `docker-compose up`:

```bash
# Required
export AVAX_RPC_URL="https://avax-mainnet.g.alchemy.com/v2/YOUR_KEY"
export BACKEND_WALLET_PRIVATE_KEY="0x..."
export BACKEND_WALLET_ADDRESS="0x..."

# Optional (have sensible defaults)
export CHAIN_ID=43114
export PREMIUM_PERCENTAGE=0.01
export MAX_COVERAGE_USDC=0.1
export CORS_ORIGINS="https://yourdomain.com"
export SENTRY_DSN="your-sentry-dsn"
```

### Using .env File

Alternatively, create a `.env` file (NOT committed to git):

```bash
# .env
AVAX_RPC_URL=https://avax-mainnet.g.alchemy.com/v2/YOUR_KEY
BACKEND_WALLET_PRIVATE_KEY=0x...
BACKEND_WALLET_ADDRESS=0x...
CHAIN_ID=43114
SENTRY_DSN=your-sentry-dsn
```

Then run:
```bash
docker-compose --env-file .env up -d
```

## Commands

### Production

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f app

# Restart app only
docker-compose restart app

# Rebuild after code changes
docker-compose up -d --build

# Start with pgAdmin
docker-compose --profile tools up -d
```

### Development

```bash
# Start dev environment
docker-compose -f docker-compose.dev.yml up

# Run in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop dev environment
docker-compose -f docker-compose.dev.yml down

# Reset databases (WARNING: deletes data)
docker-compose -f docker-compose.dev.yml down -v
```

### Database Management

```bash
# Access PostgreSQL directly
docker exec -it x402-postgres psql -U x402user -d x402insurance

# Backup database
docker exec x402-postgres pg_dump -U x402user x402insurance > backup.sql

# Restore database
cat backup.sql | docker exec -i x402-postgres psql -U x402user -d x402insurance

# Access via pgAdmin
# 1. Start with: docker-compose --profile tools up -d
# 2. Open http://localhost:5050
# 3. Login: admin@x402insurance.local / admin
# 4. Add server: postgres:5432, user: x402user, password: x402pass
```

### Monitoring

```bash
# Check container health
docker-compose ps

# View resource usage
docker stats

# Check app health endpoint
curl http://localhost:8000/health

# View all logs
docker-compose logs -f

# Follow specific service logs
docker-compose logs -f app
docker-compose logs -f postgres
docker-compose logs -f redis
```

## Data Persistence

Data is persisted in Docker volumes:

- `postgres-data`: PostgreSQL database files
- `redis-data`: Redis data (rate limiting cache)
- `pgadmin-data`: pgAdmin configuration

### Backup Volumes

```bash
# Backup PostgreSQL volume
docker run --rm \
  -v x402insurance_postgres-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz /data

# Restore PostgreSQL volume
docker run --rm \
  -v x402insurance_postgres-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/postgres-backup.tar.gz -C /
```

## Networking

All services run in a private `x402-network` bridge network. Only the Flask app (port 8000) is exposed to the host by default.

To expose other services:
```yaml
# In docker-compose.yml
postgres:
  ports:
    - "5432:5432"  # Expose PostgreSQL
```

## Security Best Practices

1. **Never commit .env files** - Use environment variables
2. **Use secrets management** - For production, use Docker secrets or external secrets managers
3. **Run as non-root** - The Dockerfile creates and uses `x402user`
4. **Update images regularly** - `docker-compose pull && docker-compose up -d`
5. **Monitor logs** - Set up log aggregation (ELK, Datadog, etc.)
6. **Enable HTTPS** - Use nginx or Traefik as reverse proxy

## Troubleshooting

### App won't start

```bash
# Check logs
docker-compose logs app

# Common issues:
# 1. Missing environment variables
docker-compose config  # Verify configuration

# 2. Port already in use
sudo lsof -i :8000  # Check what's using port 8000

# 3. Database connection issues
docker-compose logs postgres
```

### Database connection errors

```bash
# Ensure PostgreSQL is healthy
docker-compose ps postgres

# Test connection manually
docker exec -it x402-postgres psql -U x402user -d x402insurance
```

### Redis connection errors

```bash
# Check Redis is running
docker exec -it x402-redis redis-cli ping
# Should return: PONG
```

### Permission errors

```bash
# Fix data directory permissions
sudo chown -R 1000:1000 data/ logs/
```

## Production Deployment

### Using Docker Compose (Simple)

```bash
# 1. SSH to your server
ssh user@your-server

# 2. Clone repository
git clone https://github.com/yourusername/x402insurance.git
cd x402insurance

# 3. Set environment variables
export AVAX_RPC_URL="..."
export BACKEND_WALLET_PRIVATE_KEY="..."
export BACKEND_WALLET_ADDRESS="..."

# 4. Start services
docker-compose up -d

# 5. Set up reverse proxy (nginx example)
# See docs/guides/DEPLOYMENT.md
```

### Using Docker Swarm (Advanced)

```bash
# Initialize swarm
docker swarm init

# Create secrets
echo "your-private-key" | docker secret create wallet_key -
echo "your-rpc-url" | docker secret create rpc_url -

# Deploy stack
docker stack deploy -c docker-compose.yml x402
```

### Using Kubernetes

See `k8s/` directory for Kubernetes manifests (if you create them).

## Resource Limits

Default resource limits in docker-compose.yml:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

Adjust based on your needs and server capacity.

## Health Checks

All services have health checks:

- **App**: `curl http://localhost:8000/health`
- **PostgreSQL**: `pg_isready`
- **Redis**: `redis-cli ping`

Docker Compose waits for dependencies to be healthy before starting dependent services.

## Updates and Migrations

### Updating Application Code

```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild and restart
docker-compose up -d --build

# 3. Verify
docker-compose logs -f app
```

### Database Migrations

```bash
# If you add database migrations in the future:
docker-compose exec app python migrate.py
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Redis Docker Image](https://hub.docker.com/_/redis)

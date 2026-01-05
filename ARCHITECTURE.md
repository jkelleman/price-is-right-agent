# Price Tracker - Architecture & Design Decisions

> **Note:** For detailed rationale behind each technology choice, see [TECH_STACK_RATIONALE.md](TECH_STACK_RATIONALE.md)

## System Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│  React Frontend │◄────────│  FastAPI Backend │────────►│  PostgreSQL/    │
│  (Vite + TS)   │  HTTP   │  (Python)        │  SQL    │  SQLite         │
│                 │         │                  │         │                 │
└─────────────────┘         └────────┬─────────┘         └─────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
            ┌───────▼─────┐  ┌──────▼──────┐  ┌─────▼──────┐
            │  APScheduler│  │   OpenAI    │  │   SMTP     │
            │  (Every 6h) │  │  Embeddings │  │  Notifier  │
            │             │  │             │  │            │
            └─────────────┘  └─────────────┘  └────────────┘
```

# Price Tracker - Architecture & Design Decisions

> **Note:** For detailed rationale behind each technology choice, see [TECH_STACK_RATIONALE.md](TECH_STACK_RATIONALE.md)

## System Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│  React Frontend │◄────────│  FastAPI Backend │────────►│  PostgreSQL/    │
│  (Vite + TS)   │  HTTP   │  (Python)        │  SQL    │  SQLite         │
│                 │         │                  │         │                 │
└─────────────────┘         └────────┬─────────┘         └─────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
            ┌───────▼─────┐  ┌──────▼──────┐  ┌─────▼──────┐
            │  APScheduler│  │   OpenAI    │  │   SMTP     │
            │  (Every 6h) │  │  Embeddings │  │  Notifier  │
            │             │  │             │  │            │
            └─────────────┘  └─────────────┘  └────────────┘
```

## Technology Stack Summary

For detailed rationale behind each choice, see [TECH_STACK_RATIONALE.md](TECH_STACK_RATIONALE.md).

| Component | Technology | Why |
|-----------|-----------|-----|
| Backend Framework | FastAPI | Modern, fast, auto-docs |
| Background Tasks | APScheduler | In-process, no infrastructure |
| AI Similarity | OpenAI Embeddings | Best semantic understanding |
| Frontend Framework | Vite + React | 10x faster dev experience |
| State Management | React Query | Perfect for server state |
| Styling | TailwindCSS | Rapid dev, no runtime cost |
| Email | SMTP | Universal, flexible |
| Database | SQLite→PostgreSQL | Easy dev, robust prod |


| Email | SMTP | Universal, flexible |
| Database | SQLite→PostgreSQL | Easy dev, robust prod |

## Performance Considerations

### 1. Price Checking Frequency: 6 Hours

**Why not more frequent?**
- Most price changes happen daily, not hourly
- Reduces server load and API rate limiting
- Balances responsiveness with resource usage

**Configurable via:**
```python
scheduler.add_job(
    check_prices,
    'interval',
    hours=6,  # Change this
)
```

### 2. React Query Caching: 30 seconds

```typescript
staleTime: 30000, // Data fresh for 30s
```

**Rationale:**
- Prices don't change that often
- Reduces unnecessary API calls
- Still feels responsive to user

### 3. API Pagination

All list endpoints support `skip` and `limit`:
```
GET /items?skip=0&limit=100
GET /alerts?skip=0&limit=50
```

**Benefits:**
- Faster initial load
- Less memory usage
- Better mobile experience

## Security Considerations

### 1. Environment Variables
- Never commit `.env` files
- Use `.env.example` as template
- Separate configs for dev/prod

### 2. API Keys
- OpenAI key in server-side only
- SMTP credentials not exposed to frontend
- Rate limiting on API endpoints (future)

### 3. CORS
- Currently allows all origins (`*`)
- Production should restrict to frontend domain:
```python
allow_origins=["https://your-domain.com"]
```

### 4. Input Validation
- Pydantic schemas validate all inputs
- SQL injection prevented by SQLAlchemy ORM
- XSS protection via React's default escaping

## Scalability Path

### Current Capacity
- **Items**: 1,000-10,000 tracked items
- **Users**: Single user or small team
- **Requests**: 100-1000 req/day

### Scale to 100K items:
1. Move to PostgreSQL
2. Add database indexes on frequently queried columns
3. Implement Redis caching for frequent queries
4. Split price checker into separate service

### Scale to Multiple Users:
1. Add authentication (FastAPI + JWT)
2. Multi-tenancy in database (user_id foreign key)
3. Per-user rate limiting
4. Separate background workers per user

### Scale to 1M items:
1. Microservices architecture:
   - API service
   - Price checker service (Celery)
   - Notification service
2. Message queue (RabbitMQ/AWS SQS)
3. Distributed caching (Redis cluster)
4. CDN for frontend
5. Load balancer for API

## Cost Analysis

### Current Stack (0-1000 items)
- **Hosting**: $0 (local) or $5-10/month (VPS)
- **Database**: $0 (SQLite)
- **OpenAI API**: $0.02-0.10/month (1000 similarity checks)
- **Email**: $0 (Gmail) or $0.10/1000 emails (SES)
- **Total**: ~$5-10/month

### Production Scale (10K items, 100 users)
- **Server**: $20-50/month (DigitalOcean, AWS t3.medium)
- **Database**: $15-25/month (Managed PostgreSQL)
- **OpenAI**: $1-5/month
- **Email**: $15/month (SendGrid)
- **Total**: ~$50-95/month

## Monitoring & Observability

### Current Logging
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Production Additions:
1. **Application Performance Monitoring (APM)**
   - Sentry for error tracking
   - DataDog/New Relic for performance

2. **Structured Logging**
   - JSON logs for easy parsing
   - Correlation IDs for request tracing

3. **Metrics**
   - Price check success rate
   - API response times
   - Email delivery rate
   - Alert accuracy

4. **Alerting**
   - Price checker failures
   - API downtime
   - High error rates

## Development Workflow

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Testing Strategy (Future)
- **Backend**: pytest with FastAPI TestClient
- **Frontend**: Vitest + React Testing Library
- **E2E**: Playwright
- **Integration**: Test with real OpenAI API in staging

## Deployment Options

### Option 1: Single VPS (Simplest)
- Deploy backend and frontend on same server
- Nginx reverse proxy
- systemd for process management
- Cost: $5-10/month

### Option 2: Separate Services
- Backend: Railway, Render, Fly.io
- Frontend: Vercel, Netlify, Cloudflare Pages
- Database: Supabase, Railway, AWS RDS
- Cost: $10-30/month

### Option 3: Containerized (Docker)
- `docker-compose.yml` for local development
- Deploy to AWS ECS, Google Cloud Run, or DigitalOcean App Platform
- Auto-scaling based on load
- Cost: $20-50/month

## Future Architecture Improvements

1. **Caching Layer**: Redis for frequently accessed data
2. **Message Queue**: RabbitMQ for async tasks
3. **Microservices**: Separate scraper, notifier, API
4. **GraphQL**: More flexible API queries
5. **WebSockets**: Real-time price updates
6. **Mobile App**: React Native with shared logic
7. **Analytics**: Track user behavior, popular items

## Conclusion

This architecture prioritizes:
- **Developer Experience**: Fast iteration, minimal boilerplate
- **Cost Efficiency**: Leverage free/cheap services
- **Scalability**: Clear path to handle growth
- **Flexibility**: Easy to swap components
- **Reliability**: Graceful degradation, error handling

Every decision was made with these principles in mind, balancing current needs with future flexibility.

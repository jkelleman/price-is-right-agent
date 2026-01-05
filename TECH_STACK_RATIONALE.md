# Tech Stack Rationale - Price Tracker

This document explains the reasoning behind every major technology choice in the Price Tracker application, including the benefits, tradeoffs, and alternatives considered.

## Table of Contents
1. [Backend Scheduler](#backend-scheduler)
2. [AI Similarity Engine](#ai-similarity-engine)
3. [Frontend Framework](#frontend-framework)
4. [State Management](#state-management)
5. [Styling Solution](#styling-solution)
6. [Email Service](#email-service)
7. [Database Choice](#database-choice)

---

## Backend Scheduler

### Decision: APScheduler vs Celery

**Chosen: APScheduler**

**Rationale:**
- **Simplicity**: Runs in-process with FastAPI, no external infrastructure needed
- **Use Case Fit**: Our price checking is periodic (every 6 hours), not event-driven
- **Resource Efficiency**: No Redis/RabbitMQ broker to maintain
- **Development Speed**: 10 lines of code vs 100+ for Celery setup

**Tradeoffs:**

✅ **Pros:**
- Zero infrastructure overhead
- Perfect for time-based jobs
- Integrated logging and monitoring
- Easy to debug (single process)
- Lower memory footprint

❌ **Cons:**
- Single-server limitation (can't distribute across workers)
- No built-in retry mechanisms (we handle this manually)
- Process restart loses scheduled state (acceptable for our use case)

**When to Switch to Celery:**
- Need to process thousands of items per minute
- Require distributed task processing
- Need advanced retry/failure handling
- Want to scale horizontally with multiple workers

**Code Example:**
```python
# APScheduler - Simple
scheduler = BackgroundScheduler()
scheduler.add_job(check_prices, 'interval', hours=6)
scheduler.start()

# vs Celery - Complex
# Requires: Redis, broker config, worker processes,
# task definitions, result backends, etc.
```

---

## AI Similarity Engine

### Decision: OpenAI text-embedding-3-small

**Rationale:**
- **Cost Effective**: $0.02 per 1M tokens (vs $0.10 for ada-002)
- **Quality**: 1536 dimensions, excellent for product descriptions
- **Speed**: Fast inference, <100ms per request
- **Semantic Understanding**: Captures meaning, not just keywords

### Alternative Approaches Considered:

#### 1. Manual Rule-Based Matching
```python
# Example
if "sony" in name.lower() and "headphones" in name.lower():
    match = True
```

❌ **Rejected Because:**
- Brittle: "Sony headphones" vs "Sony audio gear" miss match
- Maintenance: Requires constant tuning for edge cases
- Language: Doesn't handle synonyms ("headphones" vs "headsets")
- No semantic understanding: Can't match "wireless earbuds" to "bluetooth headphones"

✅ **Good For:**
- Exact SKU/model number matching
- Simple category filters

#### 2. TF-IDF / BM25
```python
from sklearn.feature_extraction.text import TfidfVectorizer
```

❌ **Rejected Because:**
- Keyword-based: Misses semantic similarity
- Vocabulary limited to training data
- Poor with short text (product names)

✅ **Good For:**
- Document search
- Free (no API costs)

#### 3. Self-Hosted Embeddings (Sentence Transformers)
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

❌ **Rejected Because:**
- Requires GPU infrastructure ($50+/month)
- Model updates require retraining
- Deployment complexity
- Maintenance burden

✅ **Good For:**
- High-volume production (>1M requests/month)
- Dedicated infrastructure already exists
- Privacy requirements (data can't leave premises)

#### 4. Azure OpenAI / AWS Bedrock

❌ **Rejected Because:**
- More expensive than OpenAI direct
- Additional setup complexity
- Vendor lock-in to cloud provider

✅ **Good For:**
- Enterprise deployments with existing Azure/AWS
- Compliance requirements (HIPAA, SOC2)
- Private endpoints needed

### Similarity Threshold: 0.75

**Why 0.75?**
- Empirically determined sweet spot
- <0.70: Too many false positives (unrelated products)
- >0.80: Too strict, miss good alternatives

**Configurable per request:**
```python
GET /items/{id}/similar?min_similarity=0.8
```

### Cost Analysis:
- 1000 similarity checks/month: $0.02
- 10,000 checks/month: $0.20
- 100,000 checks/month: $2.00

---

## Frontend Framework

### Decision: Vite vs Create React App vs Next.js

**Chosen: Vite**

**Comparison:**

| Feature | Vite | CRA | Next.js |
|---------|------|-----|---------|
| Dev Server Start | <1s | 10-30s | 3-5s |
| Hot Reload | Instant | 2-5s | 1-2s |
| Build Tool | Rollup | Webpack | Webpack/Turbopack |
| Bundle Size | Smaller | Larger | Medium |
| SSR/SSG | No | No | Yes |
| Complexity | Low | Low | Medium-High |
| TypeScript | Native | Config needed | Native |
| Learning Curve | Easy | Easy | Medium |

**Why Vite:**

✅ **Pros:**
- ⚡ **10x faster dev experience**: Native ESM, no bundling in dev
- 📦 **Smaller bundles**: Better tree-shaking with Rollup
- 🔧 **Modern by default**: ESM, dynamic imports, native TypeScript
- 🎯 **Perfect for SPA**: We don't need SSR (no SEO requirement)
- 💨 **Instant HMR**: See changes in milliseconds

❌ **Cons:**
- No SSR/SSG (we don't need it)
- Smaller ecosystem vs CRA/Next

**Why Not Create React App:**
- Slow dev server (10-30s startup)
- Webpack overhead
- Ejecting is painful
- Maintenance mode (not actively developed)

**Why Not Next.js:**
- Price tracker doesn't need SEO (not a public marketplace)
- SSR adds complexity we don't use
- API routes redundant (we have FastAPI)
- Slower dev server vs Vite
- More opinionated architecture

**Use Next.js When:**
- Need SEO for public pages
- Require static site generation
- Want API routes without separate backend
- Building a blog, e-commerce site, marketing pages

---

## State Management

### Decision: React Query vs Redux

**Chosen: React Query (TanStack Query)**

**Rationale:**
- **Server State**: 90% of our state is server data (items, alerts, history)
- **Built-in Features**: Caching, deduplication, background refresh, stale-while-revalidate
- **Less Code**: No actions, reducers, or selectors needed
- **Developer Experience**: DevTools show exact query state
- **Automatic**: Background refetching, retry logic, loading states

**Code Comparison:**

**React Query (10 lines):**
```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['items'],
  queryFn: getItems,
  staleTime: 30000,
});

// That's it! Handles caching, loading, errors automatically
```

**Redux (50+ lines):**
```typescript
// 1. Action types
const FETCH_ITEMS_REQUEST = 'FETCH_ITEMS_REQUEST';
const FETCH_ITEMS_SUCCESS = 'FETCH_ITEMS_SUCCESS';
const FETCH_ITEMS_FAILURE = 'FETCH_ITEMS_FAILURE';

// 2. Action creators
const fetchItemsRequest = () => ({ type: FETCH_ITEMS_REQUEST });
const fetchItemsSuccess = (items) => ({ type: FETCH_ITEMS_SUCCESS, items });
const fetchItemsFailure = (error) => ({ type: FETCH_ITEMS_FAILURE, error });

// 3. Thunk
const fetchItems = () => async (dispatch) => {
  dispatch(fetchItemsRequest());
  try {
    const items = await getItems();
    dispatch(fetchItemsSuccess(items));
  } catch (error) {
    dispatch(fetchItemsFailure(error));
  }
};

// 4. Reducer
const itemsReducer = (state = initialState, action) => {
  switch (action.type) {
    case FETCH_ITEMS_REQUEST:
      return { ...state, loading: true };
    case FETCH_ITEMS_SUCCESS:
      return { ...state, loading: false, items: action.items };
    case FETCH_ITEMS_FAILURE:
      return { ...state, loading: false, error: action.error };
    default:
      return state;
  }
};

// 5. Selectors
const selectItems = (state) => state.items.items;
const selectLoading = (state) => state.items.loading;

// 6. Store setup
// 7. Provider setup
// 8. Component usage with useSelector/useDispatch
```

**Why Redux Would Be Overkill:**
- No complex client-side state
- No need for time-travel debugging
- Minimal cross-component state sharing
- React Query handles all async needs
- No complex state transformations

**Use Redux When:**
- Complex client-side state logic
- Need time-travel debugging
- Many interconnected state updates
- Offline-first applications
- Heavy state synchronization needs

---

## Styling Solution

### Decision: TailwindCSS vs CSS-in-JS vs CSS Modules

**Chosen: TailwindCSS**

**Rationale:**
- **Rapid Development**: Utility classes = instant styling
- **Consistency**: Design system built-in (spacing, colors)
- **Performance**: Purges unused CSS, tiny production bundle
- **No Runtime Cost**: Unlike styled-components/emotion
- **Team Velocity**: Everyone writes styles the same way

**Comparison:**

| Aspect | Tailwind | Styled Components | CSS Modules | Plain CSS |
|--------|----------|-------------------|-------------|-----------|
| Bundle Size | 10-20KB | 15-30KB + runtime | Variable | Variable |
| Runtime Cost | ✅ None | ❌ JS execution | ✅ None | ✅ None |
| Type Safety | ❌ | ✅ | ❌ | ❌ |
| Dynamic Styles | Limited | ✅ Excellent | Limited | ✅ |
| Dev Speed | ⚡⚡⚡ | ⚡ | ⚡⚡ | ⚡ |
| Learning Curve | Medium | Low | Low | Low |
| Refactoring | Easy | Medium | Easy | Hard |

**Why Not styled-components:**
- Runtime cost (styles computed at runtime)
- Larger bundle size
- SSR complexity
- We don't need dynamic theming
- Harder to share styles

**Why Not CSS Modules:**
- More boilerplate (separate .css files)
- No design system enforcement
- Global namespace issues
- Harder to maintain consistency

**Example:**

**Tailwind:**
```tsx
<button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
  Click me
</button>
```

**Styled Components:**
```tsx
const Button = styled.button`
  background: #2563eb;
  &:hover { background: #1d4ed8; }
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
`;
<Button>Click me</Button>
```

**CSS Modules:**
```tsx
// button.module.css
.button { background: #2563eb; padding: 0.5rem 1rem; }
.button:hover { background: #1d4ed8; }

// Component
<button className={styles.button}>Click me</button>
```

---

## Email Service

### Decision: SMTP vs Dedicated Services

**Chosen: SMTP (aiosmtplib)**

**Rationale:**
- **Universal**: Works with Gmail, Outlook, SendGrid, AWS SES, Mailgun
- **No Vendor Lock-in**: Easy to switch providers
- **Cost**: Use existing email account, no per-email charges
- **Async**: Non-blocking with aiosmtplib
- **Simple**: Standard protocol, well-documented

**Alternative Services:**

### 1. SendGrid API

✅ **Pros:**
- Faster delivery
- Better deliverability (99%+)
- Advanced features (templates, analytics, A/B testing)
- Webhooks for events

❌ **Cons:**
- Vendor lock-in
- Costs money ($15/month minimum)
- API-specific code (not portable)

**Cost:** $15/month (40K emails) → $90/month (200K emails)

### 2. AWS SES

✅ **Pros:**
- Cheap ($0.10 per 1000 emails)
- High deliverability
- Scales infinitely
- Integrates with AWS ecosystem

❌ **Cons:**
- AWS account required
- Complex setup (IAM, verification, DKIM)
- Out of sandbox requires support ticket

**Cost:** $0.10/1000 emails + $0.12/GB attachments

### 3. Twilio SendGrid

✅ **Pros:**
- Rich API features
- Excellent documentation
- Reliable infrastructure

❌ **Cons:**
- Expensive for high volume
- Another service to maintain
- Requires API key management

**Cost:** $15-$90/month depending on volume

### 4. Mailgun

✅ **Pros:**
- Developer-friendly API
- Good deliverability
- Flexible pricing

❌ **Cons:**
- Not as feature-rich as SendGrid
- Smaller company (reliability concerns)

**Cost:** $15/month (1000 emails/day)

**Our Choice:**
- ✅ Start with SMTP (Gmail, Outlook) - $0
- ✅ Easy migration path to dedicated service
- ✅ Keep SMTP code as fallback
- ✅ Test with real provider before committing

**Migration Path:**
```python
# Easy to swap implementations
if os.getenv("USE_SENDGRID"):
    from sendgrid_notifier import SendGridNotifier
    notifier = SendGridNotifier()
else:
    from notifications import EmailNotifier
    notifier = EmailNotifier()
```

---

## Database Choice

### Decision: SQLite (dev) + PostgreSQL (prod)

**Chosen: Both - SQLite for development, PostgreSQL for production**

**Rationale:**
- **Development**: SQLite = zero setup, file-based, perfect for local dev
- **Production**: PostgreSQL = robust, concurrent writes, ACID guarantees
- **SQLAlchemy**: Abstracts differences, same code works for both
- **Easy Migration**: Change one environment variable

**SQLite Perfect for:**
- ✅ Local development (no server setup)
- ✅ Small deployments (<100 items)
- ✅ Single-user scenarios
- ✅ Testing and CI/CD
- ✅ Prototyping

**PostgreSQL Better for:**
- ✅ Production with multiple users
- ✅ High write concurrency
- ✅ Advanced features (full-text search, JSON queries)
- ✅ Reliable backups and replication
- ✅ Better performance at scale

**Comparison:**

| Feature | SQLite | PostgreSQL | MySQL |
|---------|--------|------------|-------|
| Setup | None | Medium | Medium |
| Concurrent Writes | Poor | Excellent | Good |
| Max DB Size | 281 TB | Unlimited | Large |
| ACID | ✅ | ✅ | ✅ |
| Full-text Search | Basic | Advanced | Good |
| JSON Support | ✅ | ✅ Excellent | ✅ |
| Cost | Free | Free (self-host) | Free |
| Managed Options | No | Many | Many |

**Why Not MongoDB:**
- Our data is relational (items → price_history → alerts)
- Strong consistency requirements
- SQL is more familiar to most devs
- SQLAlchemy ORM works great

**Why Not MySQL:**
- PostgreSQL has better JSON support
- More advanced features (window functions, CTEs)
- Better standards compliance
- Personal preference (both are fine)

**Migration:**
```python
# .env
# Dev
DATABASE_URL=sqlite:///./price_tracker.db

# Prod
DATABASE_URL=postgresql://user:pass@host/dbname

# Code doesn't change!
engine = create_engine(DATABASE_URL)
```

---

## Summary Table

| Decision | Chosen | Why | Cost |
|----------|--------|-----|------|
| **Scheduler** | APScheduler | No infrastructure, simple | $0 |
| **AI** | OpenAI | Best semantic understanding | $0.02-0.10/mo |
| **Frontend** | Vite | 10x faster dev | $0 |
| **State** | React Query | Perfect for server state | $0 |
| **Styling** | TailwindCSS | Rapid dev, no runtime cost | $0 |
| **Email** | SMTP | Universal, flexible | $0 |
| **Database** | SQLite→PostgreSQL | Easy dev, robust prod | $0-25/mo |

**Total Monthly Cost:**
- Development: $0
- Small Production: $5-10 (VPS only)
- Medium Production: $50-95 (managed services)

---

## When to Reconsider These Choices

### Switch to Celery when:
- Processing >1000 items/hour
- Need distributed task processing
- Require complex retry logic

### Switch to Self-Hosted Embeddings when:
- >1M similarity checks/month ($20 in API costs)
- Privacy requirements
- Have GPU infrastructure

### Add Redux when:
- Complex client state emerges
- Need offline-first functionality
- Time-travel debugging required

### Switch to Next.js when:
- Need SEO for public pages
- Want static site generation
- Building marketing pages

### Upgrade Email Service when:
- Sending >10K emails/month
- Need advanced analytics
- Deliverability becomes issue

### Switch to MongoDB when:
- Data becomes truly document-oriented
- Need horizontal scaling
- Flexible schema required

---

## Conclusion

Every technology choice was made with these priorities:

1. **Developer Experience** - Fast iteration, minimal boilerplate
2. **Cost Efficiency** - Leverage free/cheap services where possible
3. **Scalability** - Clear path to handle growth
4. **Flexibility** - Easy to swap components as needs change
5. **Reliability** - Proven technologies with good support

The stack is optimized for:
- Solo developer or small team
- Rapid prototyping and iteration
- Cost-effective scaling
- Production-ready with minimal changes
- Clear upgrade paths as requirements grow

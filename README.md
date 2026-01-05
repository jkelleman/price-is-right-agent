# Price Tracker

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A smart shopping assistant that tracks items you want to buy, alerts you when prices drop, and finds similar alternatives using AI.

## 🌟 Features

- **Wishlist Management** - Keep track of items you want to purchase
- **Automated Price Monitoring** - Background service checks prices every 6 hours
- **Price Alerts** - Get notified via email when prices drop below your target
- **AI-Powered Similarity Detection** - Find comparable products and better deals using OpenAI embeddings
- **Price History Charts** - Visualize price trends over time
- **Email Notifications** - Beautiful HTML emails for price drops and alternatives

## 🏗️ Tech Stack & Design Decisions

### Backend
- **FastAPI**: Modern, fast Python web framework with automatic API documentation
- **SQLAlchemy**: Powerful ORM for database operations
- **PostgreSQL/SQLite**: PostgreSQL for production, SQLite for development
- **APScheduler**: Lightweight background task scheduler (vs Celery - no Redis needed)
- **OpenAI API**: text-embedding-3-small for cost-effective product similarity ($0.02/1M tokens)
- **aiosmtplib**: Async email sending without blocking

### Frontend
- **React 18 + TypeScript**: Type-safe component development
- **Vite**: Lightning-fast dev server and build tool (vs CRA - 10x faster)
- **TailwindCSS**: Utility-first CSS for rapid UI development
- **React Query**: Best-in-class data fetching and caching
- **React Router**: Standard routing solution
- **Recharts**: Responsive price history charts
- **Lucide React**: Modern, tree-shakeable icons

### Key Tradeoffs

**APScheduler vs Celery**
- ✅ APScheduler: In-process, no infrastructure, perfect for periodic tasks
- ❌ Celery: Requires Redis/RabbitMQ, overkill for simple price checking

**Vite vs Next.js**
- ✅ Vite: Simpler SPA architecture, faster dev experience
- ❌ Next.js: SSR/SSG capabilities we don't need here

**OpenAI Embeddings vs Manual Rules**
- ✅ Embeddings: Semantic understanding, better matching
- ❌ Manual Rules: Brittle, requires constant tuning

**SMTP vs Dedicated Email Service**
- ✅ SMTP: Universal, works with any provider
- ❌ Dedicated APIs: Faster but vendor lock-in

## 📦 Project Structure

```
price-tracker/
├── backend/
│   ├── main.py              # FastAPI application & routes
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── scraper.py           # Web scraping logic
│   ├── price_monitor.py     # Background price checking
│   ├── similarity.py        # AI similarity engine
│   ├── notifications.py     # Email notifications
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
└── frontend/
    ├── src/
    │   ├── components/      # React components
    │   ├── pages/           # Page components
    │   ├── api.ts           # API client
    │   ├── types.ts         # TypeScript types
    │   └── App.tsx          # Main app component
    ├── package.json
    └── vite.config.ts
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API key (for similarity features)
- SMTP credentials (for email notifications)

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration:
# - OPENAI_API_KEY (for AI features)
# - SMTP credentials (for email notifications)
# - DATABASE_URL (optional, defaults to SQLite)
```

5. **Run the server:**
```bash
python main.py
# Or using uvicorn directly:
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`
Interactive API docs at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

4. **Build for production:**
```bash
npm run build
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=sqlite:///./price_tracker.db

# OpenAI (for similarity features)
OPENAI_API_KEY=sk-...

# Email Notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAIL=recipient@example.com
```

### Gmail Setup for Notifications
1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the app password in `SMTP_PASSWORD`

## 📚 API Documentation

### Items
- `GET /items` - List all tracked items
- `POST /items` - Add new item to track
- `GET /items/{id}` - Get specific item
- `DELETE /items/{id}` - Remove item from tracking
- `GET /items/{id}/history` - Get price history

### Alerts
- `GET /alerts` - List all alerts (supports `unread_only` filter)
- `GET /alerts/{id}` - Get specific alert
- `PATCH /alerts/{id}/read` - Mark alert as read
- `PATCH /alerts/read-all` - Mark all alerts as read
- `DELETE /alerts/{id}` - Delete alert

### AI Features
- `GET /items/{id}/similar` - Find similar items
- `GET /items/{id}/better-deals` - Find similar items with better prices
- `POST /items/{id}/find-alternatives` - Trigger similarity check and create alerts

## 🎯 Features in Detail

### 1. Automated Price Monitoring
- Background scheduler runs every 6 hours
- Scrapes current prices from product URLs
- Records price history for trend analysis
- Creates alerts when prices drop below target

### 2. AI-Powered Similarity
- Uses OpenAI embeddings to understand product descriptions
- Cosine similarity for matching (0.75 threshold)
- Finds alternatives that are at least 10% cheaper
- Automatic alert creation for better deals

### 3. Email Notifications
- Beautiful HTML email templates
- Batch notifications to avoid spam
- Supports any SMTP provider
- Graceful degradation if email fails

### 4. Price History Visualization
- Interactive charts using Recharts
- Track price trends over time
- Identify best time to buy

## 🐛 Troubleshooting

### Price scraping fails
- Websites have different HTML structures
- Add custom selectors in `scraper.py`
- Consider using Playwright for JavaScript-heavy sites

### Email not sending
- Check SMTP credentials
- Ensure "Less secure app access" or app passwords enabled
- Check logs for detailed error messages

### OpenAI features not working
- Verify `OPENAI_API_KEY` is set correctly
- Check API quota and billing
- Features gracefully degrade if API unavailable

## 📈 Future Enhancements

- [ ] User authentication and multi-user support
- [ ] Mobile app (React Native)
- [ ] Browser extension for quick adds
- [ ] More e-commerce site support
- [ ] Push notifications
- [ ] Price drop predictions using ML
- [ ] Social sharing of deals
- [ ] Wishlist sharing and gifting

## 📄 License

MIT

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

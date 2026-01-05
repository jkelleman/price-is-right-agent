# Quick Start Guide

Get your Price Tracker up and running in 5 minutes!

## 🚀 Quick Setup

### 1. Backend (2 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate
# Or on Mac/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env
# Or on Mac/Linux: cp .env.example .env

# Start the server
python main.py
```

✅ Backend running at http://localhost:8000

### 2. Frontend (2 minutes)

Open a NEW terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

✅ Frontend running at http://localhost:3000

### 3. Test It Out! (1 minute)

1. Open http://localhost:3000 in your browser
2. Click "Add Item"
3. Fill in:
   - Name: "Test Product"
   - URL: "https://www.amazon.com/test"
   - Current Price: 100
   - Target Price: 80
4. Click "Add Item"
5. View your dashboard!

## 🔑 Optional Features

### Enable AI Similarity (Optional)

1. Get OpenAI API key: https://platform.openai.com/api-keys
2. Edit `backend/.env`:
   ```env
   OPENAI_API_KEY=sk-your-key-here
   ```
3. Restart backend
4. Try "Find Similar Items" on any product!

### Enable Email Notifications (Optional)

#### Gmail Setup:
1. Enable 2FA on your Gmail account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Edit `backend/.env`:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-16-digit-app-password
   NOTIFICATION_EMAIL=where-to-send@example.com
   ```
4. Restart backend
5. Get notified when prices drop!

## 📱 Using the App

### Add Items to Track
1. Click "Add Item" in navigation
2. Paste product URL
3. Set target price (optional)
4. Submit

### View Price History
1. Click any item card
2. See price trends over time
3. Find similar items

### Check Alerts
1. Click "Alerts" in navigation
2. See price drop notifications
3. Mark as read or delete

## 🔧 Configuration

### Change Price Check Frequency

Edit `backend/price_monitor.py`:
```python
self.scheduler.add_job(
    self.check_all_prices,
    'interval',
    hours=6,  # Change to 1, 12, 24, etc.
)
```

### Change Similarity Threshold

When calling the API:
```
GET /items/{id}/similar?min_similarity=0.8
```

Or edit `backend/similarity.py`:
```python
self.similarity_threshold = 0.75  # Change to 0.6-0.9
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.10+)
python --version

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend won't start
```bash
# Check Node version (need 18+)
node --version

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database errors
```bash
# Delete and recreate database
cd backend
rm price_tracker.db
python main.py  # Will auto-create tables
```

### Price scraping not working
- Many websites block scrapers
- Try with Amazon, eBay, or Walmart URLs
- Check `backend/scraper.py` logs for errors

## 📖 Next Steps

- Read [README.md](README.md) for full documentation
- Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Check API docs at http://localhost:8000/docs
- Star the repo if you find it useful! ⭐

## 💡 Tips

1. **Start Simple**: Use without OpenAI/email first
2. **Test Locally**: Add a few items before deploying
3. **Check Logs**: Both terminals show helpful debug info
4. **Use API Docs**: http://localhost:8000/docs for testing endpoints

## 🎉 You're Ready!

Your price tracker is now running. Add items, set target prices, and let it monitor deals for you!

Need help? Check the main README or open an issue on GitHub.

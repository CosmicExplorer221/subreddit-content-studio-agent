# LinkedIn Content Automation Tool

Complete automation tool for creating LinkedIn content from Reddit posts.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd subreddit-content-studio-agent
```

2. Run the application:

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

The script will:
- Create Python virtual environment (if needed)
- Install backend dependencies
- Install frontend dependencies
- Start both backend and frontend servers

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs

### Configuration

1. Copy backend environment file:
```bash
cp backend/.env.example backend/.env
```

2. Edit `backend/.env` with your API credentials:

```env
# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password

# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Notion API (optional)
NOTION_API_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_database_id
```

### API Key Setup

**Reddit API:**
1. Go to https://www.reddit.com/prefs/apps
2. Create an app (script type)
3. Copy client ID and secret

**Gemini API:**
1. Go to https://makersuite.google.com/app/apikey
2. Create an API key
3. Copy the key

**Notion API:**
1. Go to https://www.notion.so/my-integrations
2. Create a new integration
3. Copy the token
4. Create a database and share it with your integration
5. Copy the database ID from the URL

## Features

### 1. Reddit Content Fetching
- Fetch posts from multiple subreddits by category
- Filter by time period, score, comments
- Automatic media downloads (images and videos)
- Top comments extraction

### 2. Content Generation
- AI-powered LinkedIn post generation using Gemini
- Template-based writing styles
- Quality scoring (0-100)
- Multiple variations with best selection

### 3. Notion Integration
- Batch sync posts to Notion database
- Duplicate detection by Reddit post ID
- Rich page content with metadata
- Status tracking

### 4. Post Management
- List and filter posts
- Edit generated content
- Manage post status workflow
- Media preview and downloads

## Project Structure

```
subreddit-content-studio-agent/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── models/            # Data models
│   │   └── storage/           # JSON storage
│   ├── data/                  # JSON database
│   ├── downloads/             # Media files
│   └── requirements.txt
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── pages/             # Page components
│   │   ├── store/             # State management
│   │   ├── api/               # API client
│   │   └── types/             # TypeScript types
│   └── package.json
│
├── .claude/                    # Agent documentation
│   └── agents/                # Specialized agents
│
├── start.bat                   # Windows launcher
├── start.sh                    # Unix launcher
└── README.md
```

## Workflow

1. **Fetch Reddit Posts**
   - Select category (e.g., Railway)
   - Choose time filter (day/week/month)
   - Set limits and filters
   - Download media automatically

2. **Generate LinkedIn Content**
   - Select posts to generate content for
   - Choose writing template
   - Generate with AI (Gemini)
   - Review quality scores

3. **Edit and Refine**
   - Edit generated content
   - Adjust hashtags
   - Update status

4. **Sync to Notion**
   - Select posts to sync
   - Batch sync to database
   - Automatic duplicate detection
   - Track in Notion workflow

## Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m app.main
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Testing

**Backend:**
```bash
cd backend
python test_reddit_media.py
python test_complete_pipeline.py
```

**Frontend:**
```bash
cd frontend
npm run build
```

## Architecture

### Backend (FastAPI + Python)
- RESTful API with OpenAPI/Swagger docs
- JSON file-based storage (thread-safe)
- Background job processing
- Service-oriented architecture
- Reddit API integration (PRAW)
- Google Gemini AI integration
- Notion API integration

### Frontend (React + TypeScript)
- Vite for fast development
- Tailwind CSS for styling
- Zustand for state management
- React Router for navigation
- Axios for API calls

## Stopping the Application

**Windows:**
```bash
stop.bat
```

**Linux/Mac:**
Press `Ctrl+C` in the terminal running the app

## Troubleshooting

### Port Already in Use

**Backend (8000):**
```bash
# Find and kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

**Frontend (3000):**
```bash
# Find and kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <pid> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

### Dependencies Issues

**Backend:**
```bash
cd backend
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
rm -rf node_modules
npm install
```

### API Connection Issues

1. Ensure backend is running on port 8000
2. Check backend logs for errors
3. Verify API credentials in `.env`
4. Test endpoints at http://localhost:8000/api/docs

## Documentation

- **Backend API**: http://localhost:8000/api/docs
- **Backend README**: [backend/README.md](backend/README.md)
- **Frontend README**: [frontend/README.md](frontend/README.md)
- **Agent Docs**: [.claude/agents/README.md](.claude/agents/README.md)

## License

MIT

## Support

For issues or questions, please check the documentation or create an issue in the repository.

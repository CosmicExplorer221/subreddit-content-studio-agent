# LinkedIn Content Studio - Railway Edition

**Production-ready LinkedIn content automation tool built following comprehensive agent documentation.**

Generate professional LinkedIn posts from curated Railway/Transit content using AI, with automatic Notion sync.

## ✨ Features

- 📱 **20+ Pre-loaded Railway Posts** - Work immediately with realistic sample content
- 🎨 **AI Content Generation** - Google Gemini creates professional LinkedIn posts
- 📝 **Template System** - Railway-optimized templates with custom options
- 🔄 **Notion Integration** - Batch sync to Notion database
- 🖼️ **Media Management** - Handle images and videos
- ⚙️ **Full Settings** - Manage templates, categories, and API keys
- 💻 **Windows-Ready** - Simple .bat scripts to run everything

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git

### 1. Clone & Setup
```bash
git clone <repository-url>
cd subreddit-content-studio-agent
setup.bat
```

### 2. Configure API Keys
1. Get a [Google Gemini API key](https://makersuite.google.com/app/apikey)
2. Get a [Notion API key](https://www.notion.so/my-integrations)
3. Create Notion database and get database ID
4. Copy `backend\.env.example` to `backend\.env`
5. Add your API keys to `.env`

### 3. Run Application
```bash
run_app.bat
```

The app will open at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## 📚 Workflow

1. **Browse Content** - 20+ Railway posts pre-loaded
2. **Select Posts** - Use checkboxes to select posts
3. **Generate** - Click "Generate Posts" to create LinkedIn content
4. **Review** - Edit generated posts as needed
5. **Sync** - Send to Notion with one click

## 🏗️ Architecture

Built following 9 specialized agent guidelines:
- **Backend**: FastAPI + JSON storage
- **Frontend**: React + TypeScript + Tailwind + Zustand
- **AI**: Google Gemini 1.5 Flash
- **Storage**: JSON files (zero database installation)
- **State**: Zustand for React state management

```
/
├── .claude/agents/         # 9 agent .md files (architecture docs)
├── backend/                # FastAPI backend
│   ├── api/               # REST endpoints
│   ├── services/          # Business logic
│   ├── models/            # Pydantic schemas
│   ├── data/              # JSON storage
│   └── main.py            # Entry point
├── frontend/              # React + TypeScript
│   ├── src/
│   │   ├── pages/        # Main pages
│   │   ├── components/   # Reusable components
│   │   ├── store/        # Zustand stores
│   │   └── api/          # API client
│   └── package.json
├── downloads/             # Sample media files
│   └── railway/          # Railway category media
├── setup.bat             # Install dependencies
├── run_app.bat           # Launch both servers
└── README.md             # This file
```

## 📦 Sample Data

Includes **20+ realistic Railway posts**:
- New train models and technology
- Infrastructure projects
- Transit news and updates
- Engineering innovations
- Mix of text, image, and video posts
- Realistic scores (100-5000) and comments

## 🎯 API Keys Setup

### Google Gemini
1. Go to https://makersuite.google.com/app/apikey
2. Create new API key
3. Add to `.env`: `GEMINI_API_KEY=your_key_here`

### Notion
1. Go to https://www.notion.so/my-integrations
2. Create new integration
3. Get API key
4. Create a database in Notion
5. Share database with your integration
6. Get database ID from URL
7. Add to `.env`:
   ```
   NOTION_API_KEY=your_key_here
   NOTION_DATABASE_ID=your_database_id_here
   ```

## 🛠️ Windows Scripts

- **setup.bat** - Install all dependencies (run once)
- **run_app.bat** - Start both backend and frontend
- **run_backend.bat** - Start only backend server
- **run_frontend.bat** - Start only frontend server

## 🧪 Testing

The app works immediately with sample data:
```bash
run_app.bat
```

1. Open http://localhost:5173
2. Browse 20+ pre-loaded Railway posts
3. Select a few posts
4. Click "Generate Posts" (requires Gemini API key)
5. Review generated content
6. Sync to Notion (requires Notion API key)

## 📁 Data Storage

All data stored as JSON files in `backend/data/`:
- `posts.json` - Content posts
- `generated_posts.json` - AI-generated LinkedIn posts
- `templates.json` - Style templates
- `categories.json` - Content categories
- `settings.json` - App settings

## 🔒 Security

- API keys in `.env` (never committed)
- Input validation on all endpoints
- Error handling throughout
- Secure API key handling

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.9+)
- Install dependencies: `cd backend && pip install -r requirements.txt`
- Check port 8000 is free

### Frontend won't start
- Check Node version: `node --version` (need 16+)
- Install dependencies: `cd frontend && npm install`
- Check port 5173 is free

### API calls fail
- Verify Gemini API key in `.env`
- Verify Notion API key and database ID
- Check backend is running
- Check browser console for errors

### No posts showing
- Sample data loads automatically on first run
- Check `backend/data/posts.json` exists
- Restart backend server

## 📝 Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🎨 Customization

### Add New Category
1. Edit `backend/data/categories.json`
2. Add category object with name, subreddits, hashtags
3. Restart backend

### Add New Template
1. Edit `backend/data/templates.json`
2. Add template with system_prompt, task_instruction, requirements
3. Restart backend

### Add More Sample Posts
1. Edit `backend/data/posts.json`
2. Follow existing post structure
3. Restart backend

## 📄 License

MIT

## 🙏 Acknowledgments

Built following comprehensive agent documentation:
- Backend Architecture Agent
- Configuration Manager Agent
- Reddit Integration Agent (adapted for sample data)
- Media Handler Agent
- LLM Integration Agent
- Notion Integration Agent
- Frontend Developer Agent
- Code Reviewer Agent
- Test Engineer Agent

---

**Ready to create professional LinkedIn content from Railway posts!** 🚂✨

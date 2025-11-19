# LinkedIn Content Automation - Frontend

React frontend for the LinkedIn Content Automation tool.

## Features

- **Dashboard**: Overview of posts and statistics
- **Reddit Browser**: Fetch and browse Reddit posts by category
- **Post Management**: Generate LinkedIn content, edit, and manage posts
- **Notion Sync**: Batch sync posts to Notion database
- **Settings**: Configure API keys, categories, and templates

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Zustand** for state management
- **React Router** for navigation
- **Axios** for API calls
- **Lucide React** for icons

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The frontend will start at `http://localhost:3000` with proxy to backend at `http://localhost:8000`.

### 3. Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/         # Layout components (Sidebar, Header)
│   │   ├── reddit/         # Reddit browser components
│   │   ├── posts/          # Post management components
│   │   ├── notion/         # Notion sync components
│   │   └── settings/       # Settings components
│   ├── pages/              # Page components
│   │   ├── Dashboard.tsx
│   │   ├── RedditPage.tsx
│   │   ├── PostsPage.tsx
│   │   ├── NotionPage.tsx
│   │   └── SettingsPage.tsx
│   ├── store/              # Zustand stores
│   │   ├── usePostStore.ts
│   │   ├── useCategoryStore.ts
│   │   ├── useTemplateStore.ts
│   │   └── useJobStore.ts
│   ├── api/                # API client
│   │   └── client.ts
│   ├── types/              # TypeScript types
│   │   └── index.ts
│   ├── App.tsx             # Main app component
│   └── main.tsx            # Entry point
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Features Overview

### Dashboard

- Post statistics by status
- Category and template overview
- Quick actions

### Reddit Browser

- Fetch posts from multiple subreddits
- Filter by category and time period
- Automatic media downloads
- View post details and stats

### Post Management

- List and filter posts
- Select multiple posts for bulk actions
- Generate LinkedIn content with Gemini
- Edit post content
- Quality scoring and validation

### Notion Sync

- Batch sync to Notion database
- Duplicate detection by Reddit post ID
- Update existing pages or skip duplicates
- Connection status monitoring

### Settings

- API configuration guide
- Category management
- Template configuration

## API Integration

The frontend connects to the FastAPI backend through a proxy configured in `vite.config.ts`:

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

All API calls go through `/api/*` which proxies to the backend.

## State Management

Zustand stores handle global state:

- **usePostStore**: Posts, filters, selection
- **useCategoryStore**: Categories
- **useTemplateStore**: Templates
- **useJobStore**: Background job tracking

## Development

### Hot Module Replacement

Vite provides instant HMR during development:

```bash
npm run dev
```

### Type Checking

TypeScript is configured for strict type checking:

```bash
npm run build  # Includes type checking
```

### Linting

```bash
npm run lint
```

## Production Deployment

### Build

```bash
npm run build
```

Output will be in `dist/` directory.

### Preview

```bash
npm run preview
```

### Deploy

Deploy the `dist/` directory to any static hosting:

- Vercel
- Netlify
- AWS S3 + CloudFront
- nginx

### Environment Configuration

The frontend proxies API calls during development. For production, configure your hosting to proxy `/api/*` to your backend server.

Example nginx configuration:

```nginx
server {
  listen 80;
  root /var/www/frontend/dist;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /api {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

## Troubleshooting

### Port Already in Use

Change port in `vite.config.ts`:

```typescript
server: {
  port: 3001,
  // ...
}
```

### API Connection Issues

Ensure backend is running at `http://localhost:8000`:

```bash
cd backend
python -m app.main
```

### Build Errors

Clear cache and reinstall:

```bash
rm -rf node_modules dist
npm install
npm run build
```

## License

MIT

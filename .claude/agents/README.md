# LinkedIn Content Automation - Agent System

## Overview
This directory contains specialized sub-agents for building and maintaining the LinkedIn Content Automation tool. Each agent is an expert in a specific domain and works together to create a comprehensive automation workflow.

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  LinkedIn Content Automation                 │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ Reddit  │          │   LLM   │          │ Notion  │
   │ Expert  │─────────▶│ Expert  │─────────▶│ Expert  │
   └────┬────┘          └─────────┘          └─────────┘
        │                     ▲
   ┌────▼────┐               │
   │  Media  │               │
   │ Handler │───────────────┘
   └─────────┘
        │
   ┌────▼────────┬──────────┬──────────┬──────────┐
   │   Backend   │ Frontend │  Config  │   Test   │
   │  Architect  │   Dev    │ Manager  │ Engineer │
   └─────────────┴──────────┴──────────┴──────────┘
                      │
                 ┌────▼────┐
                 │  Code   │
                 │Reviewer │
                 └─────────┘
```

## Available Agents

### 1. **reddit-integration-expert.md**
**Domain:** Reddit API, Post Fetching, Content Filtering

**Responsibilities:**
- Fetch posts from multiple subreddits
- Filter by score, engagement, recency
- Extract comments and metadata
- Handle rate limiting
- Categorize content

**Key Skills:**
- PRAW (Python Reddit API Wrapper)
- OAuth2 authentication
- Rate limiting strategies
- Content ranking algorithms

**When to Use:**
- Implementing Reddit API integration
- Building post fetching workflows
- Creating content filters
- Setting up category mappings

---

### 2. **media-handler.md**
**Domain:** Media Download, File Management, Storage

**Responsibilities:**
- Download videos and images
- Process and optimize media files
- Manage storage and organization
- Handle multiple file formats
- Extract thumbnails and metadata

**Key Skills:**
- Async file downloads
- FFmpeg video processing
- Image optimization (PIL/Pillow)
- Cloud storage (S3, GCS)
- File validation

**When to Use:**
- Implementing media downloads
- Setting up storage infrastructure
- Processing videos/images
- Optimizing file sizes

---

### 3. **llm-integration-expert.md**
**Domain:** Gemini API, Content Generation, Prompt Engineering

**Responsibilities:**
- Generate LinkedIn posts from Reddit content
- Manage style templates
- Optimize prompts for quality
- Validate generated content
- Handle API costs and quotas

**Key Skills:**
- Google Gemini API
- Prompt engineering
- Content transformation
- Quality validation
- Cost optimization

**When to Use:**
- Implementing AI content generation
- Creating style templates
- Optimizing prompts
- Building content quality checks

---

### 4. **notion-integration-expert.md**
**Domain:** Notion API, Database Operations, Content Management

**Responsibilities:**
- Sync content to Notion databases
- Manage content workflow states
- Batch upload operations
- Track content performance
- Generate analytics reports

**Key Skills:**
- Notion API v2022-06-28
- Database schema design
- Rich text formatting
- Pagination handling
- Workflow automation

**When to Use:**
- Setting up Notion integration
- Designing content databases
- Implementing batch operations
- Building analytics dashboards

---

### 5. **backend-architect.md**
**Domain:** REST API, Database Design, System Architecture

**Responsibilities:**
- Design REST API endpoints
- Architect database schema
- Implement business logic
- Manage data flow
- Handle background jobs

**Key Skills:**
- FastAPI/Flask frameworks
- SQLite/PostgreSQL
- RESTful API design
- Caching (Redis)
- Background processing (Celery)

**When to Use:**
- Designing system architecture
- Creating API endpoints
- Database schema design
- Setting up job queues
- Implementing caching

---

### 6. **frontend-developer.md**
**Domain:** React UI, State Management, User Experience

**Responsibilities:**
- Build React components
- Implement responsive layouts
- Manage application state
- Integrate with backend API
- Optimize performance

**Key Skills:**
- React 18+ with hooks
- Tailwind CSS
- React Query/Zustand
- TypeScript
- API integration

**When to Use:**
- Building UI components
- Implementing user flows
- Setting up state management
- Creating responsive designs
- API integration on frontend

---

### 7. **config-manager.md**
**Domain:** Configuration, API Keys, Environment Management

**Responsibilities:**
- Manage configuration files
- Secure API keys and secrets
- Handle environment variables
- Define category/template configs
- Validate configurations

**Key Skills:**
- YAML/JSON configuration
- Environment variables
- Secrets encryption
- Schema validation
- Multi-environment support

**When to Use:**
- Setting up configuration system
- Managing API credentials
- Creating category configs
- Defining style templates
- Environment setup

---

### 8. **code-reviewer.md**
**Domain:** Code Quality, Security, Performance

**Responsibilities:**
- Review code for quality
- Identify security vulnerabilities
- Suggest performance optimizations
- Enforce best practices
- Audit dependencies

**Key Skills:**
- Security auditing (OWASP)
- Performance optimization
- Code quality metrics
- Static analysis tools
- Best practices enforcement

**When to Use:**
- Reviewing pull requests
- Security audits
- Performance optimization
- Code refactoring
- Pre-deployment checks

---

### 9. **test-engineer.md**
**Domain:** Testing, Quality Assurance, Test Automation

**Responsibilities:**
- Write unit tests
- Create integration tests
- Build E2E test suites
- Maintain test coverage
- Set up CI/CD testing

**Key Skills:**
- pytest/Jest testing
- Mocking and fixtures
- E2E testing (Playwright)
- Test coverage analysis
- CI/CD integration

**When to Use:**
- Writing test suites
- Setting up test infrastructure
- Implementing TDD
- Creating test fixtures
- CI/CD pipeline setup

---

## Agent Coordination Workflows

### Workflow 1: Complete Content Pipeline
```
1. config-manager: Load configuration and API keys
2. reddit-integration-expert: Fetch posts from Reddit
3. media-handler: Download associated media files
4. llm-integration-expert: Generate LinkedIn posts
5. notion-integration-expert: Upload to Notion database
6. test-engineer: Verify workflow with integration tests
7. code-reviewer: Review implementation for security
```

### Workflow 2: New Feature Development
```
1. backend-architect: Design API endpoints and data flow
2. frontend-developer: Create UI components
3. config-manager: Add necessary configuration
4. test-engineer: Write tests for new feature
5. code-reviewer: Review code quality and security
```

### Workflow 3: System Setup
```
1. config-manager: Set up configuration files
2. backend-architect: Initialize database and API
3. reddit-integration-expert: Configure Reddit API
4. llm-integration-expert: Set up Gemini integration
5. notion-integration-expert: Configure Notion workspace
6. media-handler: Set up storage infrastructure
7. frontend-developer: Build admin interface
```

### Workflow 4: Quality Assurance
```
1. test-engineer: Run full test suite
2. code-reviewer: Perform security audit
3. backend-architect: Review system performance
4. frontend-developer: Check UI/UX quality
```

## How to Use This Agent System

### For New Features
1. **Plan**: Identify which agents are needed
2. **Design**: Consult backend-architect for system design
3. **Implement**: Use domain-specific agents for implementation
4. **Test**: Use test-engineer for comprehensive testing
5. **Review**: Use code-reviewer for quality check

### For Bug Fixes
1. **Identify**: Determine which agent's domain the bug is in
2. **Fix**: Apply fixes using relevant agent's expertise
3. **Test**: Use test-engineer to create regression tests
4. **Review**: Use code-reviewer to verify fix quality

### For Optimization
1. **Analyze**: Use code-reviewer to identify issues
2. **Optimize**: Apply domain-specific optimizations
3. **Test**: Verify improvements with test-engineer
4. **Validate**: Ensure no regressions

## Quick Reference

| Task | Primary Agent | Supporting Agents |
|------|---------------|-------------------|
| Fetch Reddit posts | reddit-integration-expert | config-manager |
| Download media | media-handler | backend-architect |
| Generate content | llm-integration-expert | config-manager |
| Sync to Notion | notion-integration-expert | backend-architect |
| Build API | backend-architect | config-manager, test-engineer |
| Create UI | frontend-developer | backend-architect |
| Manage config | config-manager | - |
| Review code | code-reviewer | - |
| Write tests | test-engineer | All agents |

## Agent Communication Patterns

### Data Flow Between Agents

```python
# Example: Complete content generation flow

# 1. Reddit Expert fetches posts
reddit_posts = reddit_expert.fetch_posts(category="tech")

# 2. Media Handler downloads media
for post in reddit_posts:
    if post.has_media:
        media_handler.download(post.media_urls, post.id)

# 3. LLM Expert generates LinkedIn content
template = config_manager.get_template("tech")
linkedin_content = llm_expert.generate(
    reddit_data=reddit_posts[0],
    template=template
)

# 4. Backend stores everything
backend.store_post(reddit_posts[0])
backend.store_linkedin_content(linkedin_content)

# 5. Notion Expert syncs to workspace
notion_expert.create_entry({
    **linkedin_content,
    "status": "draft"
})
```

## Configuration Files

Each agent may require specific configuration. See `config-manager.md` for details on:

- `config/default.yaml` - Default settings
- `config/categories.yaml` - Category definitions
- `config/templates/*.yaml` - Style templates
- `.env` - Environment variables and API keys

## Best Practices

### Agent Collaboration
1. **Clear Interfaces**: Each agent has well-defined inputs/outputs
2. **Loose Coupling**: Agents don't directly depend on each other
3. **Single Responsibility**: Each agent focuses on one domain
4. **Testability**: All agent code is unit testable

### Development Workflow
1. Always start with config-manager to set up environment
2. Use backend-architect for system-level decisions
3. Consult relevant domain experts for implementation
4. Use test-engineer for comprehensive testing
5. Use code-reviewer before committing changes

### Quality Gates
- **Pre-commit**: Run tests (test-engineer)
- **Pre-PR**: Run code review (code-reviewer)
- **Pre-deploy**: Full integration tests (test-engineer)
- **Post-deploy**: Monitor performance (backend-architect)

## Directory Structure

```
project/
├── .claude/
│   └── agents/              # This directory
│       ├── README.md        # This file
│       ├── reddit-integration-expert.md
│       ├── media-handler.md
│       ├── llm-integration-expert.md
│       ├── notion-integration-expert.md
│       ├── backend-architect.md
│       ├── frontend-developer.md
│       ├── config-manager.md
│       ├── code-reviewer.md
│       └── test-engineer.md
├── src/
│   ├── services/            # Implementation
│   │   ├── reddit_integration.py
│   │   ├── media_handler.py
│   │   ├── llm_integration.py
│   │   └── notion_integration.py
│   ├── api/                 # Backend API
│   ├── database/            # Database layer
│   └── utils/               # Utilities
├── frontend/
│   └── src/                 # React app
├── tests/                   # Test suites
├── config/                  # Configuration files
└── storage/                 # Media storage

## Getting Started

### 1. Initial Setup
```bash
# Read configuration guide
cat .claude/agents/config-manager.md

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Install dependencies
pip install -r requirements.txt
cd frontend && npm install
```

### 2. Development
```bash
# Consult relevant agents based on task
# Example: Adding Reddit integration
cat .claude/agents/reddit-integration-expert.md

# Implement feature
# Write tests
pytest tests/

# Review code
cat .claude/agents/code-reviewer.md
```

### 3. Testing
```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
```

### 4. Deployment
```bash
# Final review
cat .claude/agents/code-reviewer.md

# Run full test suite
pytest --cov=src --cov-fail-under=80

# Deploy
# (deployment steps depend on infrastructure)
```

## Troubleshooting

### "Which agent should I consult?"
- **API issues**: backend-architect
- **Reddit API**: reddit-integration-expert
- **Content generation**: llm-integration-expert
- **UI bugs**: frontend-developer
- **Configuration**: config-manager
- **Security concerns**: code-reviewer
- **Test failures**: test-engineer

### "How do agents work together?"
Agents represent expertise areas. When implementing a feature:
1. Identify which domains are involved
2. Consult relevant agent documentation
3. Follow best practices from each agent
4. Coordinate data flow between components

### "Can I modify agents?"
Yes! These agents are templates. Customize them as your project evolves while maintaining the separation of concerns.

## Contributing

When adding new functionality:
1. Determine which agent(s) are relevant
2. Update agent documentation if needed
3. Follow agent guidelines for implementation
4. Add tests (test-engineer)
5. Request review (code-reviewer)

## Support

For questions about:
- **Architecture**: See backend-architect.md
- **Specific integrations**: See relevant expert agent
- **General setup**: Start with config-manager.md
- **Testing**: See test-engineer.md

---

**Version**: 1.0.0
**Last Updated**: 2024-01-15
**Maintainer**: LinkedIn Content Automation Team

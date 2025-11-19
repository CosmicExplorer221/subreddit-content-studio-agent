# Config Manager Agent

## Role
You are a specialized agent focused on configuration management, API key handling, category/template management, environment variables, and secure settings storage for the LinkedIn Content Automation tool.

## Core Expertise
- Configuration architecture and best practices
- Environment variable management
- Secrets management and encryption
- YAML/JSON configuration parsing
- Dynamic configuration updates
- API key rotation and security
- Multi-environment support (dev, staging, prod)
- Configuration validation and schema enforcement

## Key Responsibilities

### 1. Configuration Architecture
```
config/
├── default.yaml           # Default configuration
├── development.yaml       # Development overrides
├── production.yaml        # Production overrides
├── categories.yaml        # Category definitions
├── templates/
│   ├── tech.yaml
│   ├── business.yaml
│   ├── productivity.yaml
│   ├── marketing.yaml
│   └── design.yaml
└── schemas/
    ├── config.schema.json
    └── template.schema.json

.env                       # Local environment variables (gitignored)
.env.example              # Example env file (committed)
```

### 2. Main Configuration Structure
```yaml
# config/default.yaml
app:
  name: "LinkedIn Content Automation"
  version: "1.0.0"
  environment: ${APP_ENV:-development}
  debug: ${DEBUG:-true}

server:
  host: ${HOST:-0.0.0.0}
  port: ${PORT:-8000}
  workers: ${WORKERS:-4}
  reload: ${RELOAD:-true}
  log_level: ${LOG_LEVEL:-info}

database:
  type: ${DB_TYPE:-sqlite}
  sqlite:
    path: ${SQLITE_PATH:-./data/linkedin_automation.db}
  postgresql:
    host: ${POSTGRES_HOST:-localhost}
    port: ${POSTGRES_PORT:-5432}
    database: ${POSTGRES_DB:-linkedin_automation}
    user: ${POSTGRES_USER}
    password: ${POSTGRES_PASSWORD}
  pool_size: ${DB_POOL_SIZE:-10}

redis:
  enabled: ${REDIS_ENABLED:-false}
  host: ${REDIS_HOST:-localhost}
  port: ${REDIS_PORT:-6379}
  db: ${REDIS_DB:-0}
  password: ${REDIS_PASSWORD}

reddit:
  client_id: ${REDDIT_CLIENT_ID}
  client_secret: ${REDDIT_CLIENT_SECRET}
  username: ${REDDIT_USERNAME}
  password: ${REDDIT_PASSWORD}
  user_agent: "LinkedInContentStudio/1.0"
  rate_limit:
    max_requests_per_minute: 60
    retry_attempts: 3
    retry_delay_seconds: 5

gemini:
  api_key: ${GEMINI_API_KEY}
  model: ${GEMINI_MODEL:-gemini-1.5-pro}
  temperature: ${GEMINI_TEMPERATURE:-0.7}
  max_output_tokens: ${GEMINI_MAX_TOKENS:-2048}
  rate_limit:
    max_requests_per_minute: 60

notion:
  api_token: ${NOTION_API_TOKEN}
  database_id: ${NOTION_DATABASE_ID}
  version: "2022-06-28"
  rate_limit:
    max_requests_per_second: 3

storage:
  type: ${STORAGE_TYPE:-local}  # local, s3, gcs
  local:
    path: ${STORAGE_PATH:-./storage}
    max_size_gb: ${STORAGE_MAX_SIZE:-50}
  s3:
    bucket: ${S3_BUCKET}
    region: ${S3_REGION:-us-east-1}
    access_key: ${AWS_ACCESS_KEY_ID}
    secret_key: ${AWS_SECRET_ACCESS_KEY}

security:
  secret_key: ${SECRET_KEY}
  encryption_key: ${ENCRYPTION_KEY}
  allowed_origins: ${ALLOWED_ORIGINS:-http://localhost:3000}
  api_key_rotation_days: 90

monitoring:
  enabled: ${MONITORING_ENABLED:-false}
  sentry_dsn: ${SENTRY_DSN}
  log_level: ${LOG_LEVEL:-info}
```

### 3. Category Configuration
```yaml
# config/categories.yaml
categories:
  tech:
    name: "Technology"
    description: "Technology and software development content"
    subreddits:
      - programming
      - technology
      - coding
      - MachineLearning
      - webdev
      - softwareengineering
    default_template: tech
    filters:
      min_score: 100
      min_comments: 10
      max_age_days: 7
      exclude_nsfw: true
    hashtags:
      - "#Tech"
      - "#Technology"
      - "#Programming"
      - "#SoftwareEngineering"
      - "#Innovation"

  business:
    name: "Business & Entrepreneurship"
    description: "Business strategy and entrepreneurship"
    subreddits:
      - Entrepreneur
      - startups
      - business
      - smallbusiness
      - investing
    default_template: business
    filters:
      min_score: 150
      min_comments: 15
      max_age_days: 7
    hashtags:
      - "#Business"
      - "#Entrepreneurship"
      - "#Startup"
      - "#Leadership"
      - "#Strategy"

  productivity:
    name: "Productivity & Personal Development"
    description: "Productivity tips and personal growth"
    subreddits:
      - productivity
      - getdisciplined
      - selfimprovement
      - lifehacks
    default_template: productivity
    filters:
      min_score: 80
      min_comments: 8
      max_age_days: 7
    hashtags:
      - "#Productivity"
      - "#PersonalDevelopment"
      - "#SelfImprovement"
      - "#TimeManagement"

  marketing:
    name: "Marketing & Growth"
    description: "Marketing strategies and growth tactics"
    subreddits:
      - marketing
      - socialmedia
      - SEO
      - content_marketing
      - digitalmarketing
    default_template: marketing
    filters:
      min_score: 100
      min_comments: 10
      max_age_days: 7
    hashtags:
      - "#Marketing"
      - "#DigitalMarketing"
      - "#GrowthHacking"
      - "#ContentMarketing"

  design:
    name: "Design & UX"
    description: "Design, UX, and creative content"
    subreddits:
      - web_design
      - graphic_design
      - UI_Design
      - UXDesign
      - design
    default_template: design
    filters:
      min_score: 75
      min_comments: 8
      max_age_days: 7
    hashtags:
      - "#Design"
      - "#UXDesign"
      - "#GraphicDesign"
      - "#WebDesign"
```

### 4. Template Configuration
```yaml
# config/templates/tech.yaml
name: "Tech Professional"
description: "Professional technology content for LinkedIn"

system_prompt: |
  You are a LinkedIn content creator specializing in technology.
  Transform Reddit posts into engaging LinkedIn content that:
  - Educates tech professionals
  - Uses industry-appropriate terminology
  - Maintains a professional yet approachable tone
  - Includes actionable insights
  - Avoids clickbait and sensationalism

task_instruction: |
  Create a LinkedIn post (1300-2000 characters) that:
  1. Opens with a compelling hook
  2. Presents the main insight or learning
  3. Adds professional context and analysis
  4. Includes 1-2 practical takeaways
  5. Ends with engagement question or CTA
  6. Uses 3-5 relevant hashtags
  7. Formats for readability (line breaks, emojis sparingly)

requirements:
  - Professional tone appropriate for tech leaders
  - Focus on insights, not just news
  - Add unique perspective or analysis
  - Include credible context
  - Use line breaks for readability
  - Maximum 5 hashtags at the end
  - No clickbait or sensational language

target_length:
  min: 1300
  max: 2000

hashtag_count:
  min: 3
  max: 5

style:
  tone: professional
  voice: authoritative
  emoji_usage: minimal
  formatting: structured

examples:
  - |
    The best code I've written this year?
    I deleted 10,000 lines.

    Here's what I learned about sustainable software development:

    [Main insight from Reddit post]

    This aligns with what we're seeing across the industry...

    What's your approach to managing technical debt?

    #SoftwareEngineering #TechLeadership #CleanCode
```

### 5. Configuration Manager Implementation
```python
import os
import yaml
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import jsonschema
from cryptography.fernet import Fernet

class ConfigManager:
    def __init__(self, config_dir: str = "config", env: str = None):
        self.config_dir = Path(config_dir)
        self.env = env or os.getenv("APP_ENV", "development")

        # Load environment variables
        load_dotenv()

        # Initialize encryption
        self.cipher = self._init_encryption()

        # Load configurations
        self.config = self._load_config()
        self.categories = self._load_categories()
        self.templates = self._load_templates()

        # Validate configurations
        self._validate_config()

    def _init_encryption(self) -> Optional[Fernet]:
        """Initialize encryption for sensitive data"""
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if encryption_key:
            return Fernet(encryption_key.encode())
        return None

    def _load_config(self) -> Dict[str, Any]:
        """Load and merge configuration files"""
        # Load default config
        default_config = self._load_yaml(self.config_dir / "default.yaml")

        # Load environment-specific config
        env_config_path = self.config_dir / f"{self.env}.yaml"
        env_config = {}
        if env_config_path.exists():
            env_config = self._load_yaml(env_config_path)

        # Merge configurations (env config overrides default)
        config = self._deep_merge(default_config, env_config)

        # Substitute environment variables
        config = self._substitute_env_vars(config)

        return config

    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file"""
        with open(file_path, 'r') as f:
            return yaml.safe_load(f) or {}

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _substitute_env_vars(self, config: Any) -> Any:
        """Recursively substitute environment variables"""
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Handle ${VAR} and ${VAR:-default} syntax
            import re
            pattern = r'\$\{([^}]+)\}'

            def replace_var(match):
                var_spec = match.group(1)
                if ':-' in var_spec:
                    var_name, default = var_spec.split(':-', 1)
                    return os.getenv(var_name, default)
                else:
                    return os.getenv(var_spec, '')

            return re.sub(pattern, replace_var, config)
        else:
            return config

    def _load_categories(self) -> Dict[str, Any]:
        """Load category configurations"""
        categories_path = self.config_dir / "categories.yaml"
        if categories_path.exists():
            return self._load_yaml(categories_path)
        return {}

    def _load_templates(self) -> Dict[str, Any]:
        """Load template configurations"""
        templates = {}
        templates_dir = self.config_dir / "templates"

        if templates_dir.exists():
            for template_file in templates_dir.glob("*.yaml"):
                template_name = template_file.stem
                templates[template_name] = self._load_yaml(template_file)

        return templates

    def _validate_config(self):
        """Validate configuration against schemas"""
        schema_path = self.config_dir / "schemas" / "config.schema.json"

        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema = json.load(f)

            try:
                jsonschema.validate(self.config, schema)
            except jsonschema.exceptions.ValidationError as e:
                raise ValueError(f"Configuration validation failed: {e}")

    # Getter methods
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation path
        Example: config.get('reddit.client_id')
        """
        keys = path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_category(self, category_name: str) -> Optional[Dict]:
        """Get category configuration"""
        return self.categories.get('categories', {}).get(category_name)

    def get_template(self, template_name: str) -> Optional[Dict]:
        """Get template configuration"""
        return self.templates.get(template_name)

    def get_all_categories(self) -> Dict[str, Any]:
        """Get all category configurations"""
        return self.categories.get('categories', {})

    def get_subreddits_for_category(self, category: str) -> list:
        """Get list of subreddits for a category"""
        cat_config = self.get_category(category)
        return cat_config.get('subreddits', []) if cat_config else []

    def get_filters_for_category(self, category: str) -> Dict:
        """Get filters for a category"""
        cat_config = self.get_category(category)
        return cat_config.get('filters', {}) if cat_config else {}

    # Setter methods
    def set(self, path: str, value: Any):
        """Set configuration value by dot-notation path"""
        keys = path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def save_config(self, output_path: Optional[Path] = None):
        """Save current configuration to file"""
        if output_path is None:
            output_path = self.config_dir / f"{self.env}.yaml"

        with open(output_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

    # Secret management
    def get_secret(self, key: str) -> Optional[str]:
        """Get decrypted secret"""
        encrypted_value = self.get(key)

        if encrypted_value and self.cipher:
            try:
                return self.cipher.decrypt(encrypted_value.encode()).decode()
            except Exception:
                return encrypted_value

        return encrypted_value

    def set_secret(self, key: str, value: str):
        """Set encrypted secret"""
        if self.cipher:
            encrypted_value = self.cipher.encrypt(value.encode()).decode()
            self.set(key, encrypted_value)
        else:
            self.set(key, value)

    # Validation
    def validate_required_keys(self):
        """Validate that all required configuration keys are present"""
        required_keys = [
            'reddit.client_id',
            'reddit.client_secret',
            'gemini.api_key',
            'notion.api_token',
            'notion.database_id'
        ]

        missing_keys = []

        for key in required_keys:
            if not self.get(key):
                missing_keys.append(key)

        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")

    def check_api_keys(self) -> Dict[str, bool]:
        """Check which API keys are configured"""
        return {
            'reddit': bool(self.get('reddit.client_id')),
            'gemini': bool(self.get('gemini.api_key')),
            'notion': bool(self.get('notion.api_token')),
            's3': bool(self.get('storage.s3.access_key'))
        }


# Singleton instance
_config_instance = None

def get_config() -> ConfigManager:
    """Get configuration singleton"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance
```

### 6. Environment File Template
```bash
# .env.example
# Copy this file to .env and fill in your values

# Application
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database
DB_TYPE=sqlite
SQLITE_PATH=./data/linkedin_automation.db

# PostgreSQL (if using)
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=linkedin_automation
# POSTGRES_USER=your-user
# POSTGRES_PASSWORD=your-password

# Redis (optional)
REDIS_ENABLED=false
REDIS_HOST=localhost
REDIS_PORT=6379

# Reddit API
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret
REDDIT_USERNAME=your-reddit-username
REDDIT_PASSWORD=your-reddit-password

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-pro

# Notion API
NOTION_API_TOKEN=your-notion-api-token
NOTION_DATABASE_ID=your-database-id

# Storage
STORAGE_TYPE=local
STORAGE_PATH=./storage

# AWS S3 (if using)
# S3_BUCKET=your-bucket-name
# S3_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key

# Monitoring (optional)
# SENTRY_DSN=your-sentry-dsn
```

### 7. Configuration CLI
```python
import click
from config_manager import ConfigManager

@click.group()
def cli():
    """Configuration management CLI"""
    pass

@cli.command()
def validate():
    """Validate configuration"""
    try:
        config = ConfigManager()
        config.validate_required_keys()
        click.echo("✓ Configuration is valid")
    except Exception as e:
        click.echo(f"✗ Configuration error: {e}", err=True)
        exit(1)

@cli.command()
@click.argument('key')
def get(key):
    """Get configuration value"""
    config = ConfigManager()
    value = config.get(key)
    click.echo(f"{key} = {value}")

@cli.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set configuration value"""
    config = ConfigManager()
    config.set(key, value)
    config.save_config()
    click.echo(f"✓ Set {key} = {value}")

@cli.command()
def check_keys():
    """Check API key status"""
    config = ConfigManager()
    status = config.check_api_keys()

    click.echo("API Key Status:")
    for service, configured in status.items():
        symbol = "✓" if configured else "✗"
        click.echo(f"  {symbol} {service}")

@cli.command()
def list_categories():
    """List all categories"""
    config = ConfigManager()
    categories = config.get_all_categories()

    click.echo("Categories:")
    for name, cat in categories.items():
        click.echo(f"\n{name}:")
        click.echo(f"  Subreddits: {', '.join(cat['subreddits'])}")
        click.echo(f"  Template: {cat['default_template']}")

if __name__ == '__main__':
    cli()
```

## Dependencies
```python
# requirements.txt
pyyaml==6.0.1
python-dotenv==1.0.0
jsonschema==4.20.0
cryptography==41.0.7
click==8.1.7
```

## Security Best Practices
- Never commit .env files
- Rotate API keys regularly
- Use encryption for sensitive values
- Implement key rotation mechanisms
- Use different keys per environment
- Audit configuration changes
- Restrict file permissions on config files

## Usage Example
```python
from config_manager import get_config

config = get_config()

# Get values
reddit_client_id = config.get('reddit.client_id')
gemini_model = config.get('gemini.model')

# Get category config
tech_category = config.get_category('tech')
subreddits = config.get_subreddits_for_category('tech')

# Get template
tech_template = config.get_template('tech')
```

"""
Initialize default data
Creates Railway category and professional default template
"""
from app.storage.json_storage import get_storage


def initialize_default_data():
    """Initialize Railway category and default template"""
    storage = get_storage()

    print("Initializing default data...")

    # Check if already initialized
    if storage.get_category("railway"):
        print("✓ Railway category already exists")
    else:
        # Create Railway category
        railway_category = {
            "id": "railway",
            "name": "Railway & Train Content",
            "description": "Railway enthusiast content, train photography, and rail industry news",
            "subreddits": [
                "trains",
                "railroading",
                "TrainPorn",
                "modeltrains",
                "transit"
            ],
            "default_template": "professional",
            "hashtags": [
                "#Railway",
                "#Trains",
                "#RailwayEngineering",
                "#Transportation",
                "#Infrastructure"
            ],
            "filters": {
                "min_score": 100,
                "min_comments": 10,
                "max_age_days": 7,
                "exclude_nsfw": True
            }
        }

        storage.create_category("railway", railway_category)
        print("✓ Created Railway category")

    # Check if default template exists
    if storage.get_template("professional"):
        print("✓ Professional template already exists")
    else:
        # Create professional template
        professional_template = {
            "id": "professional",
            "name": "Professional",
            "description": "Professional LinkedIn content style for general topics",
            "system_prompt": """You are a professional LinkedIn content creator.
Transform content into engaging LinkedIn posts that:
- Maintain a professional yet approachable tone
- Provide valuable insights and takeaways
- Encourage meaningful engagement
- Use industry-appropriate language
- Avoid clickbait and sensationalism""",
            "task_instruction": """Create a LinkedIn post (1300-2000 characters) that:
1. Opens with a compelling hook or question
2. Presents the main insight or story
3. Adds professional context and analysis
4. Includes 2-3 practical takeaways
5. Ends with an engaging question or call-to-action
6. Uses 3-5 relevant hashtags
7. Formats with line breaks for readability

Make it authentic, valuable, and engaging for a professional audience.""",
            "requirements": [
                "Professional tone appropriate for LinkedIn",
                "Focus on insights and value, not just information",
                "Add unique perspective or analysis",
                "Include credible context when relevant",
                "Use line breaks for readability",
                "3-5 hashtags at the end",
                "No clickbait or sensational language",
                "Authentic voice that builds trust"
            ],
            "target_length": {
                "min": 1300,
                "max": 2000
            },
            "hashtag_count": {
                "min": 3,
                "max": 5
            },
            "style": {
                "tone": "professional",
                "voice": "authentic",
                "emoji_usage": "minimal",
                "formatting": "structured"
            },
            "examples": [
                """I've been thinking about infrastructure lately.

Not the tech kind – the real, physical infrastructure that connects our world.

[Main insight or story from source content]

Here's what struck me about this...

[Professional analysis and context]

Three things we can learn:
→ [Insight 1]
→ [Insight 2]
→ [Insight 3]

The way we build and maintain our infrastructure says a lot about our priorities.

What's your take on this?

#Infrastructure #Engineering #Innovation #Leadership #Transportation""",

                """Something interesting happened this week.

[Compelling opening related to the content]

Let me share what I learned...

[Main content with professional framing]

This connects to a bigger trend:

[Professional analysis and broader implications]

Key takeaways:
• [Point 1]
• [Point 2]
• [Point 3]

[Thoughtful conclusion]

What has been your experience with this?

#Professional #Industry #Insights #Learning"""
            ]
        }

        storage.create_template("professional", professional_template)
        print("✓ Created Professional template")

    # Initialize settings if not exists
    settings = storage.get_settings()
    if not settings.get('initialized'):
        storage.update_settings({
            "initialized": True,
            "default_category": "railway",
            "default_template": "professional"
        })
        print("✓ Initialized application settings")

    print("\n✅ Default data initialization complete!")
    print(f"   - Category: Railway (subreddits: {len(railway_category['subreddits'])})")
    print(f"   - Template: Professional")


if __name__ == "__main__":
    initialize_default_data()

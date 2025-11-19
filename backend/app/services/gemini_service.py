"""
Gemini LLM Service
Handles content generation using Google Gemini API
"""
import google.generativeai as genai
from typing import Dict, List, Optional, Any
import logging
import re
from datetime import datetime

from app.core.config import settings
from app.storage.json_storage import get_storage
from app.models.schemas import LinkedInContent, Post

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for generating LinkedIn content using Gemini API"""

    def __init__(self):
        """Initialize Gemini client"""
        self.api_key = settings.gemini_api_key
        self.model_name = "gemini-1.5-pro"
        self.temperature = 0.7
        self.max_tokens = 2048
        self.storage = get_storage()

        # Configure Gemini
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini service initialized with model: {self.model_name}")
        else:
            self.model = None
            logger.warning("Gemini API key not configured")

    def is_configured(self) -> bool:
        """Check if Gemini is properly configured"""
        return self.api_key is not None and self.model is not None

    def get_template(self, template_id: str) -> Optional[Dict]:
        """Load template by ID"""
        try:
            template = self.storage.storage.read("templates", template_id)
            return template
        except Exception as e:
            logger.error(f"Error loading template {template_id}: {e}")
            return None

    def build_prompt(
        self,
        template: Dict,
        reddit_post: Dict,
        category_hashtags: List[str] = None
    ) -> str:
        """
        Build the complete prompt for content generation

        Args:
            template: Template configuration
            reddit_post: Reddit post data
            category_hashtags: Optional category-specific hashtags

        Returns:
            Formatted prompt string
        """
        # Extract Reddit data
        title = reddit_post.get('title', '')
        content = reddit_post.get('content', '')
        subreddit = reddit_post.get('subreddit', '')
        score = reddit_post.get('score', 0)
        num_comments = reddit_post.get('num_comments', 0)
        top_comments = reddit_post.get('top_comments', [])

        # Format top comments
        comments_text = ""
        if top_comments:
            comments_text = "\n\nTop Comments:\n"
            for i, comment in enumerate(top_comments[:5], 1):
                comments_text += f"{i}. \"{comment['body'][:200]}...\" (Score: {comment['score']})\n"

        # Build prompt
        prompt = f"""
{template.get('system_prompt', '')}

{template.get('task_instruction', '')}

Source Material:
- Subreddit: r/{subreddit}
- Title: {title}
- Content: {content or 'N/A'}
- Engagement: {score} upvotes, {num_comments} comments
- Upvote Ratio: {reddit_post.get('upvote_ratio', 0):.0%}
{comments_text}

Requirements:
"""

        # Add template requirements
        for req in template.get('requirements', []):
            prompt += f"- {req}\n"

        # Add length requirements
        target_length = template.get('target_length', {})
        min_length = target_length.get('min', 1300)
        max_length = target_length.get('max', 2000)
        prompt += f"\nLength: {min_length}-{max_length} characters\n"

        # Add hashtag requirements
        hashtag_count = template.get('hashtag_count', {})
        min_tags = hashtag_count.get('min', 3)
        max_tags = hashtag_count.get('max', 5)

        if category_hashtags:
            prompt += f"\nHashtags ({min_tags}-{max_tags} tags, include these: {', '.join(category_hashtags[:3])}):\n"
        else:
            prompt += f"\nHashtags ({min_tags}-{max_tags} relevant tags):\n"

        # Add style guidelines
        style = template.get('style', {})
        prompt += f"\nStyle:\n"
        prompt += f"- Tone: {style.get('tone', 'professional')}\n"
        prompt += f"- Voice: {style.get('voice', 'authoritative')}\n"
        prompt += f"- Emoji Usage: {style.get('emoji_usage', 'minimal')}\n"

        # Add examples if available
        examples = template.get('examples', [])
        if examples:
            prompt += f"\nExample Posts:\n"
            for i, example in enumerate(examples[:2], 1):
                prompt += f"\nExample {i}:\n{example}\n"

        prompt += "\nGenerate the LinkedIn post now. Return ONLY the post content, no explanations or meta-commentary."

        return prompt

    async def generate_content(
        self,
        post_id: str,
        template_id: Optional[str] = None,
        variations: int = 1
    ) -> Dict[str, Any]:
        """
        Generate LinkedIn content for a post

        Args:
            post_id: ID of the post to generate content for
            template_id: Optional template ID (uses category default if not provided)
            variations: Number of variations to generate (1-3)

        Returns:
            Dictionary with generated content and metadata
        """
        if not self.is_configured():
            raise ValueError("Gemini API is not configured. Set GEMINI_API_KEY in .env")

        # Load post
        try:
            post_data = self.storage.storage.read("posts", post_id)
        except Exception as e:
            raise ValueError(f"Post {post_id} not found: {e}")

        # Get category
        category = post_data.get('category')

        # Get template
        if not template_id:
            # Use category default
            try:
                category_data = self.storage.storage.read("categories", category)
                template_id = category_data.get('default_template', 'professional')
            except Exception:
                template_id = 'professional'

        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Get category hashtags
        try:
            category_data = self.storage.storage.read("categories", category)
            category_hashtags = category_data.get('hashtags', [])
        except Exception:
            category_hashtags = []

        # Build prompt
        reddit_data = post_data.get('reddit_data', {})
        prompt = self.build_prompt(template, reddit_data, category_hashtags)

        # Generate variations
        generated_content = []
        errors = []

        for i in range(min(variations, 3)):
            try:
                logger.info(f"Generating variation {i+1}/{variations} for post {post_id}")

                # Generate content
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=self.temperature + (i * 0.1),  # Slight variation
                        max_output_tokens=self.max_tokens,
                    )
                )

                # Extract content
                content_text = response.text.strip()

                # Validate and extract metadata
                linkedin_content = self.validate_and_parse(
                    content_text,
                    template,
                    category_hashtags
                )

                generated_content.append({
                    'variation': i + 1,
                    'content': linkedin_content,
                    'quality_score': linkedin_content.get('quality_score', 0)
                })

            except Exception as e:
                logger.error(f"Error generating variation {i+1}: {e}")
                errors.append(f"Variation {i+1}: {str(e)}")

        if not generated_content:
            raise ValueError(f"Failed to generate any content. Errors: {errors}")

        # Sort by quality score and pick the best
        generated_content.sort(key=lambda x: x['content'].get('quality_score', 0), reverse=True)
        best_content = generated_content[0]['content']

        # Update post with generated content
        post_data['linkedin_content'] = best_content
        post_data['template_id'] = template_id
        post_data['status'] = 'review'
        post_data['updated_at'] = datetime.utcnow().isoformat()

        self.storage.storage.write("posts", post_id, post_data)

        return {
            'post_id': post_id,
            'template_id': template_id,
            'variations_generated': len(generated_content),
            'best_content': best_content,
            'all_variations': generated_content,
            'errors': errors
        }

    def validate_and_parse(
        self,
        content: str,
        template: Dict,
        category_hashtags: List[str] = None
    ) -> Dict[str, Any]:
        """
        Validate generated content and extract metadata

        Args:
            content: Generated content string
            template: Template used for generation
            category_hashtags: Category-specific hashtags

        Returns:
            LinkedInContent dictionary with metadata
        """
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', content)

        # Calculate character count
        char_count = len(content)

        # Calculate quality score (0-100)
        quality_score = 0

        # Check length requirements
        target_length = template.get('target_length', {})
        min_length = target_length.get('min', 1300)
        max_length = target_length.get('max', 2000)

        if min_length <= char_count <= max_length:
            quality_score += 30
        elif char_count < min_length:
            # Penalty for being too short
            ratio = char_count / min_length
            quality_score += int(30 * ratio)
        else:
            # Penalty for being too long
            quality_score += 20

        # Check hashtag count
        hashtag_count = template.get('hashtag_count', {})
        min_tags = hashtag_count.get('min', 3)
        max_tags = hashtag_count.get('max', 5)

        if min_tags <= len(hashtags) <= max_tags:
            quality_score += 20
        elif len(hashtags) > 0:
            quality_score += 10

        # Check if category hashtags are included
        if category_hashtags:
            included_category_tags = sum(
                1 for tag in category_hashtags
                if tag.lower() in [h.lower() for h in hashtags]
            )
            quality_score += min(20, included_category_tags * 10)
        else:
            quality_score += 10

        # Check for paragraph structure (multiple paragraphs)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) >= 3:
            quality_score += 15
        elif len(paragraphs) >= 2:
            quality_score += 10

        # Check for emoji usage based on template style
        style = template.get('style', {})
        emoji_usage = style.get('emoji_usage', 'minimal')
        emoji_count = len(re.findall(r'[\U0001F300-\U0001F9FF]', content))

        if emoji_usage == 'minimal' and emoji_count <= 3:
            quality_score += 10
        elif emoji_usage == 'moderate' and 3 <= emoji_count <= 8:
            quality_score += 10
        elif emoji_usage == 'heavy' and emoji_count >= 8:
            quality_score += 10

        # Check for call-to-action
        cta_patterns = [
            r'what do you think',
            r'share your',
            r'let me know',
            r'comment below',
            r'thoughts?',
            r'agree?'
        ]
        if any(re.search(pattern, content.lower()) for pattern in cta_patterns):
            quality_score += 5

        return {
            'content': content,
            'quality_score': min(100, quality_score),
            'hashtags': hashtags,
            'char_count': char_count
        }

    async def batch_generate(
        self,
        post_ids: List[str],
        template_id: Optional[str] = None,
        variations: int = 1
    ) -> Dict[str, Any]:
        """
        Generate content for multiple posts

        Args:
            post_ids: List of post IDs
            template_id: Optional template ID
            variations: Number of variations per post

        Returns:
            Batch generation results
        """
        results = []
        errors = []

        for post_id in post_ids:
            try:
                result = await self.generate_content(
                    post_id=post_id,
                    template_id=template_id,
                    variations=variations
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error generating content for post {post_id}: {e}")
                errors.append({
                    'post_id': post_id,
                    'error': str(e)
                })

        return {
            'total_posts': len(post_ids),
            'successful': len(results),
            'failed': len(errors),
            'results': results,
            'errors': errors
        }


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service singleton"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service

"""
Gemini AI Service - Following llm-integration-expert.md
Content generation using Google Gemini API
"""
import os
import logging
from typing import Dict, List, Optional
import google.generativeai as genai
from datetime import datetime
import uuid
import re

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for generating LinkedIn content using Gemini AI"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini service"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-1.5-flash"

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

    def build_prompt(self, post: Dict, template: Dict) -> str:
        """
        Build prompt from post and template
        Following llm-integration-expert.md prompt engineering patterns
        """
        system_prompt = template.get("system_prompt", "")
        task_instruction = template.get("task_instruction", "")
        requirements = template.get("requirements", {})

        # Extract post details
        title = post.get("title", "")
        content = post.get("content", "")
        score = post.get("score", 0)
        comments_count = post.get("num_comments", 0)
        top_comments = post.get("top_comments", [])

        # Build comments section
        comments_text = ""
        if top_comments:
            comments_text = "\n\nTop Community Comments:\n"
            for i, comment in enumerate(top_comments[:3], 1):
                comments_text += f"{i}. {comment.get('body', '')} ({comment.get('score', 0)} upvotes)\n"

        # Build comprehensive prompt
        prompt = f"""{system_prompt}

{task_instruction}

SOURCE CONTENT:
Title: {title}
Content: {content}
Community Engagement: {score} upvotes, {comments_count} comments{comments_text}

REQUIREMENTS:
- Length: {requirements.get('target_length', {}).get('min', 1300)}-{requirements.get('target_length', {}).get('max', 2000)} characters
- Tone: {requirements.get('tone', 'professional')}
- Structure: {requirements.get('structure', 'hook + context + key points + conclusion')}
- Hashtags: {requirements.get('hashtag_count', {}).get('min', 3)}-{requirements.get('hashtag_count', {}).get('max', 5)} relevant hashtags
- Include call-to-action: {requirements.get('include_call_to_action', True)}

Example hashtags for this category: {', '.join(template.get('example_hashtags', [])[:7])}

Generate a compelling LinkedIn post that transforms this railway content into professional, engaging content for industry professionals and enthusiasts.

Format the output with the hashtags at the end, separated from the main content by a blank line.
"""

        return prompt

    def calculate_quality_score(self, content: str, requirements: Dict) -> int:
        """
        Calculate quality score for generated content
        Following llm-integration-expert.md quality assessment patterns
        """
        score = 0

        # Length check (30 points)
        target_min = requirements.get('target_length', {}).get('min', 1300)
        target_max = requirements.get('target_length', {}).get('max', 2000)
        content_length = len(content)

        if target_min <= content_length <= target_max:
            score += 30
        elif target_min * 0.9 <= content_length <= target_max * 1.1:
            score += 20
        else:
            score += 10

        # Hashtag count (20 points)
        hashtags = re.findall(r'#\w+', content)
        expected_min = requirements.get('hashtag_count', {}).get('min', 3)
        expected_max = requirements.get('hashtag_count', {}).get('max', 5)

        if expected_min <= len(hashtags) <= expected_max:
            score += 20
        elif len(hashtags) > 0:
            score += 10

        # Structure elements (30 points)
        has_hook = any(char in content[:200] for char in ['!', '?', ':'])
        has_paragraphs = content.count('\n\n') >= 2
        has_conclusion = len(content) > 500  # Assuming substantial content

        if has_hook:
            score += 10
        if has_paragraphs:
            score += 10
        if has_conclusion:
            score += 10

        # Call to action (20 points)
        cta_words = ['what do you think', 'share your', 'let me know', 'comment below',
                     'thoughts?', 'agree?', 'interested in']
        has_cta = any(phrase in content.lower() for phrase in cta_words)

        if has_cta:
            score += 20

        return min(score, 100)

    def extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        hashtags = re.findall(r'#\w+', content)
        # Remove duplicates while preserving order
        seen = set()
        unique_hashtags = []
        for tag in hashtags:
            if tag.lower() not in seen:
                seen.add(tag.lower())
                unique_hashtags.append(tag)

        return unique_hashtags

    async def generate_content(
        self,
        post: Dict,
        template: Dict,
        variation_number: int = 1
    ) -> Dict:
        """
        Generate LinkedIn content for a post
        Returns generated content with metadata
        """
        if not self.is_configured():
            raise ValueError("Gemini API key not configured")

        try:
            # Build prompt
            prompt = self.build_prompt(post, template)

            # Generate content
            logger.info(f"Generating content for post {post.get('id')} with template {template.get('id')}")

            generation_config = {
                "temperature": 0.7,
                "max_output_tokens": 2000,
                "top_p": 0.9,
                "top_k": 40,
            }

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            content = response.text.strip()

            # Extract hashtags
            hashtags = self.extract_hashtags(content)

            # Calculate quality score
            quality_score = self.calculate_quality_score(
                content,
                template.get('requirements', {})
            )

            # Create generated content object
            generated_content = {
                "id": str(uuid.uuid4()),
                "source_post_id": post.get("id"),
                "content": content,
                "template_id": template.get("id"),
                "quality_score": quality_score,
                "hashtags": hashtags,
                "generated_at": datetime.utcnow().isoformat(),
                "variation_number": variation_number
            }

            logger.info(f"Successfully generated content (quality score: {quality_score})")

            return {
                "success": True,
                "generated_content": generated_content
            }

        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_multiple(
        self,
        posts: List[Dict],
        template: Dict,
        variations: int = 1
    ) -> Dict:
        """
        Generate content for multiple posts
        Returns batch results
        """
        results = {
            "success": [],
            "failed": []
        }

        for post in posts:
            for var_num in range(1, variations + 1):
                result = await self.generate_content(post, template, var_num)

                if result.get("success"):
                    results["success"].append(result["generated_content"])
                else:
                    results["failed"].append({
                        "post_id": post.get("id"),
                        "variation": var_num,
                        "error": result.get("error", "Unknown error")
                    })

        return results


# Singleton instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get Gemini service singleton"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service

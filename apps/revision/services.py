import json
import openai
import logging
from django.conf import settings
from apps.content.models import Topic
from .models import Flashcard

logger = logging.getLogger(__name__)

class FlashcardService:
    """Service to handle flashcard generation using AI."""
    
    @staticmethod
    def generate_for_topic(topic_id):
        """Generate flashcards for a specific topic using AI."""
        topic = Topic.objects.get(id=topic_id)
        
        system_prompt = (
            "You are an expert CPA tutor. Create 5-8 high-quality flashcards for the following topic. "
            "Return the flashcards in a valid JSON array of objects, where each object has 'front' and 'back' keys. "
            "The 'front' should be a question or term, and the 'back' should be a concise answer or definition."
        )
        
        user_prompt = f"Topic: {topic.title}\nContent:\n{topic.content[:3000]}"
        
        try:
            if settings.AI_PROVIDER == "openai":
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"} if "0125" in "gpt-3.5-turbo-0125" else None
                )
                content = response.choices[0].message.content
                # Sometimes models wrap JSON in markdown blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                
                data = json.loads(content)
                # Some models might return {"flashcards": [...]}
                flashcards_data = data.get("flashcards", data) if isinstance(data, dict) else data
                
                created_count = 0
                for item in flashcards_data:
                    Flashcard.objects.create(
                        topic=topic,
                        front=item.get("front"),
                        back=item.get("back")
                    )
                    created_count += 1
                return created_count, None
                
            # Add other providers as needed
            return 0, "AI Provider not fully supported for flashcard generation yet."
            
        except Exception as e:
            logger.error(f"Flashcard generation error: {str(e)}")
            return 0, str(e)

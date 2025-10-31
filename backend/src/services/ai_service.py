"""
AI Service using Lightning AI API for conversational responses.
"""
import requests
import json
from typing import List, Dict, Optional
from src.config.settings import settings
from src.utils.logger import logger


class AIService:
    """
    Handles interactions with Lightning AI (GPT-4).
    """
    
    def __init__(self):
        self.api_url = settings.lightning_ai_url
        self.api_key = settings.lightning_ai_api_key
        self.model = settings.lightning_ai_model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Optional[str]:
        """
        Generate AI response using Lightning AI.
        
        Args:
            messages: List of conversation messages
            temperature: Creativity (0-1)
            max_tokens: Max response length
        
        Returns:
            AI response text or None if failed
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                url=self.api_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            logger.info(f"AI response generated successfully")
            return ai_response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"AI API request failed: {str(e)}")
            return None
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            return None
    
    def check_if_needs_help(
        self, 
        question: str, 
        knowledge_base: List[Dict]
    ) -> tuple[bool, Optional[str]]:
        """
        Determine if AI can answer the question or needs help.
        
        Returns:
            (needs_help, answer_or_none)
        """
        # Build knowledge context
        knowledge_context = self._build_knowledge_context(knowledge_base)
        
        system_prompt = f"""You are an AI assistant for a salon. 
You have the following knowledge:

{knowledge_context}

If you can confidently answer the question using your knowledge, provide the answer.
If you cannot answer confidently, respond with exactly: "NEEDS_HELP"
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        
        response = self.generate_response(messages, temperature=0.3)
        
        if response and "NEEDS_HELP" in response:
            logger.info(f"AI needs help with: {question}")
            return True, None
        
        logger.info(f"AI can answer: {question}")
        return False, response
    
    def _build_knowledge_context(self, knowledge_base: List[Dict]) -> str:
        """Format knowledge base for prompt context."""
        if not knowledge_base:
            return "No additional knowledge available."
        
        context_parts = []
        for entry in knowledge_base[:10]:  # Limit to prevent token overflow
            q = entry.get('question', '')
            a = entry.get('answer', '')
            context_parts.append(f"Q: {q}\nA: {a}")
        
        return "\n\n".join(context_parts)
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text for knowledge base categorization.
        """
        messages = [
            {
                "role": "system", 
                "content": "Extract 3-5 keywords from the following text. Return only keywords separated by commas."
            },
            {"role": "user", "content": text}
        ]
        
        response = self.generate_response(messages, temperature=0.3, max_tokens=50)
        
        if response:
            keywords = [k.strip() for k in response.split(',')]
            return keywords[:5]
        
        return []


# Global AI service instance
ai_service = AIService()
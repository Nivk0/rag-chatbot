# app/services/openai_service.py
from openai import AsyncOpenAI  # Changed to AsyncOpenAI
from typing import List
import logging
import asyncio
from ..core.config import settings

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)  # Using AsyncOpenAI
        self.primary_model = "gpt-3.5-turbo"
        self.fallback_model = "gpt-3.5-turbo"
        self.max_retries = 3
        self.base_delay = 1
        
    async def generate_response(self, query: str, context: List[str]) -> str:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
            
        for attempt in range(self.max_retries):
            try:
                model = self.primary_model if attempt == 0 else self.fallback_model
                
                system_message = """You are a helpful AI assistant that answers questions based on the provided document context. 
                Use the context to provide accurate and relevant answers. If the answer cannot be found in the context, 
                say so clearly."""
                
                context_text = "\n\n".join(context)
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"}
                ]
                
                # Using await with the async client
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                error_msg = str(e)
                
                if "insufficient_quota" in error_msg:
                    if attempt == 0:
                        continue
                    else:
                        raise Exception("OpenAI API quota exceeded for all models")
                        
                if "rate_limit" in error_msg or "429" in error_msg:
                    if attempt < self.max_retries - 1:
                        delay = self.base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                
                raise Exception(f"Failed to generate response: {error_msg}")
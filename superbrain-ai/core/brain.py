"""
SuperBrain LLM Core — Connects to local Ollama models.
Handles model selection, fallback, streaming, and retry logic.
"""

import requests
import logging
import time
from typing import Optional, Generator, List, Dict, Any
from config import (
    OLLAMA_BASE_URL, PRIMARY_MODEL, FALLBACK_MODELS,
    REQUEST_TIMEOUT, MAX_RETRIES, TEMPERATURE, MAX_TOKENS
)

logger = logging.getLogger("brain")


class LLMBrain:
    """
    Core LLM interface. Handles:
    - Model selection and fallback
    - Streaming and non-streaming responses
    - Retry logic with exponential backoff
    - Token estimation
    """
    
    def __init__(self, model: Optional[str] = None):
        self.base_url = OLLAMA_BASE_URL
        self.model = model or PRIMARY_MODEL
        self.fallback_models = FALLBACK_MODELS
        self.temperature = TEMPERATURE
        self.max_tokens = MAX_TOKENS
        self.active_model = self.model
        self._model_health = {}  # cache model health status
    
    def ask(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        stream: bool = False,
    ) -> str:
        """
        Send a prompt to the LLM and get a response.
        Automatically falls back to alternative models on failure.
        """
        target_model = model or self.active_model
        temp = temperature or self.temperature
        max_tok = max_tokens or self.max_tokens
        
        # Build full prompt with system message
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{prompt}\n<|assistant|>"
        
        # Try primary model first, then fallbacks
        models_to_try = [target_model] + [m for m in self.fallback_models if m != target_model]
        
        for attempt in range(MAX_RETRIES):
            for model_name in models_to_try:
                try:
                    response = self._call_ollama(
                        model=model_name,
                        prompt=full_prompt,
                        temperature=temp,
                        max_tokens=max_tok,
                        stream=stream,
                    )
                    
                    if response:
                        self.active_model = model_name
                        self._model_health[model_name] = {"status": "healthy", "last_used": time.time()}
                        return response
                    
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}")
                    self._model_health[model_name] = {"status": "unhealthy", "error": str(e)}
                    continue
            
            # Exponential backoff before retry
            if attempt < MAX_RETRIES - 1:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time}s... (attempt {attempt + 2}/{MAX_RETRIES})")
                time.sleep(wait_time)
        
        raise RuntimeError("All models failed after retries and fallbacks")
    
    def _call_ollama(
        self,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        stream: bool = False,
    ) -> Optional[str]:
        """Make direct API call to Ollama."""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        if stream:
            return self._parse_stream(response)
        else:
            return response.json().get("response", "")
    
    def _parse_stream(self, response) -> Generator[str, None, None]:
        """Parse streaming response from Ollama."""
        for line in response.iter_lines():
            if line:
                data = line.decode('utf-8')
                if data.startswith('{'):
                    import json
                    chunk = json.loads(data)
                    yield chunk.get("response", "")
    
    def ask_with_context(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        stream: bool = False,
    ) -> str:
        """
        Send a conversation history to the LLM.
        Messages format: [{"role": "user|assistant|system", "content": "..."}]
        """
        target_model = model or self.active_model
        temp = temperature or self.temperature
        max_tok = max_tokens or self.max_tokens
        
        # Add system prompt if provided
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": target_model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temp,
                "num_predict": max_tok,
            }
        }
        
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        if stream:
            return self._parse_stream(response)
        else:
            return response.json().get("message", {}).get("content", "")
    
    def is_model_available(self, model: str) -> bool:
        """Check if a specific model is available in Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [m["name"] for m in response.json().get("models", [])]
                return any(model in m for m in models)
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
        return False
    
    def list_available_models(self) -> List[str]:
        """List all models available in Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return [m["name"] for m in response.json().get("models", [])]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
        return []
    
    def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama registry."""
        try:
            url = f"{self.base_url}/api/pull"
            payload = {"name": model}
            response = requests.post(url, json=payload, timeout=300)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error pulling model {model}: {e}")
            return False
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        try:
            url = f"{self.base_url}/api/show"
            payload = {"name": model}
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
        return {}
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars ≈ 1 token for English)."""
        return len(text) // 4
    
    def truncate_to_token_limit(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit."""
        estimated_tokens = self.estimate_tokens(text)
        if estimated_tokens <= max_tokens:
            return text
        
        # Truncate proportionally
        ratio = max_tokens / estimated_tokens
        truncate_length = int(len(text) * ratio * 0.9)  # 10% safety margin
        return text[:truncate_length]

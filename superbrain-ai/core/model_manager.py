"""
Model Manager — Manages LLM model selection, health checks, and fallback.
"""

import logging
from typing import List, Optional, Dict
from config import OLLAMA_BASE_URL, PRIMARY_MODEL, FALLBACK_MODELS

logger = logging.getLogger("model_manager")


class ModelManager:
    """
    Manages LLM models including:
    - Health checking
    - Model selection
    - Fallback logic
    - Performance tracking
    """
    
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.primary_model = PRIMARY_MODEL
        self.fallback_models = FALLBACK_MODELS
        self.model_performance = {}  # Track response times and success rates
        self._available_models = []
        self._refresh_models()
    
    def _refresh_models(self):
        """Refresh the list of available models."""
        import requests
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self._available_models = [m["name"] for m in response.json().get("models", [])]
                logger.info(f"Available models: {self._available_models}")
        except Exception as e:
            logger.error(f"Failed to refresh models: {e}")
            self._available_models = []
    
    def get_best_model(self, task_type: Optional[str] = None) -> str:
        """
        Select the best model for a given task type.
        
        Args:
            task_type: Type of task (code, general, etc.)
        
        Returns:
            Recommended model name
        """
        # Refresh model list
        self._refresh_models()
        
        # For coding tasks, prefer code-specialized models
        if task_type == "code":
            for model in self._available_models:
                if "coder" in model.lower() or "deepseek" in model.lower():
                    return model
        
        # Check if primary model is available
        if any(self.primary_model in m for m in self._available_models):
            return self.primary_model
        
        # Fall back to first available model
        for model in self.fallback_models:
            if any(model in m for m in self._available_models):
                return model
        
        # Last resort: return first available model
        if self._available_models:
            return self._available_models[0]
        
        raise RuntimeError("No models available in Ollama")
    
    def check_health(self, model: Optional[str] = None) -> Dict:
        """
        Check health of a specific model or the system.
        
        Returns:
            Dict with status, latency, and available models
        """
        import requests
        import time
        
        model_to_check = model or self.primary_model
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            latency = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                models = [m["name"] for m in response.json().get("models", [])]
                model_available = any(model_to_check in m for m in models)
                
                health_status = {
                    "status": "healthy" if model_available else "degraded",
                    "latency_ms": round(latency, 2),
                    "model_available": model_available,
                    "available_models": models,
                }
                
                # Track performance
                self.model_performance[model_to_check] = {
                    "last_check": time.time(),
                    "latency_ms": health_status["latency_ms"],
                    "status": health_status["status"]
                }
                
                return health_status
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        
        except requests.exceptions.ConnectionError:
            return {"status": "unhealthy", "error": "Ollama not running"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def list_models(self) -> List[str]:
        """List all available models."""
        self._refresh_models()
        return self._available_models
    
    def get_model_info(self, model: str) -> Optional[Dict]:
        """Get detailed information about a model."""
        import requests
        
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": model},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
        
        return None
    
    def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama registry."""
        import requests
        
        try:
            logger.info(f"Pulling model: {model}")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                timeout=300
            )
            if response.status_code == 200:
                logger.info(f"Successfully pulled {model}")
                self._refresh_models()
                return True
            else:
                logger.error(f"Failed to pull {model}: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False
    
    def record_performance(self, model: str, success: bool, latency_ms: float):
        """Record performance metrics for a model."""
        if model not in self.model_performance:
            self.model_performance[model] = {
                "total_requests": 0,
                "successful_requests": 0,
                "avg_latency_ms": 0,
            }
        
        perf = self.model_performance[model]
        perf["total_requests"] += 1
        
        if success:
            perf["successful_requests"] += 1
        
        # Update average latency
        total = perf["total_requests"]
        perf["avg_latency_ms"] = (perf["avg_latency_ms"] * (total - 1) + latency_ms) / total
    
    def get_performance_stats(self, model: Optional[str] = None) -> Dict:
        """Get performance statistics for models."""
        if model:
            return self.model_performance.get(model, {})
        return self.model_performance

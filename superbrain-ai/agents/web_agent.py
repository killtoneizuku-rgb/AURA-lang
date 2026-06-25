"""
Web Agent — Handles web search and scraping operations.
"""

import logging
from typing import Dict, List
from .base_agent import BaseAgent

logger = logging.getLogger("web_agent")


class WebAgent(BaseAgent):
    """
    Web Agent specializes in:
    - Searching the web (DuckDuckGo)
    - Scraping website content
    - Summarizing web findings
    """
    
    def __init__(self, orchestrator):
        super().__init__(orchestrator)
    
    def execute(self, user_input: str, intent: Dict) -> str:
        """Execute a web operation."""
        logger.info(f"Web task: {user_input[:100]}...")
        
        if intent["type"] == "web_search":
            return self._search_web(user_input)
        elif intent["type"] == "web_scrape":
            return self._scrape_web(user_input)
        else:
            return self._search_web(user_input)
    
    def _search_web(self, query: str) -> str:
        """Search the web using DuckDuckGo."""
        try:
            from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
            
            if not results:
                return "No results found."
            
            # Format results
            formatted = []
            for i, r in enumerate(results[:5], 1):
                formatted.append(f"{i}. {r.get('title', 'No title')}\n   {r.get('body', 'No description')[:200]}\n   URL: {r.get('href', 'N/A')}\n")
            
            self._mark_success()
            return f"Search results for '{query}':\n\n" + "\n".join(formatted)
        
        except ImportError:
            return "DuckDuckGo search library not installed. Install with: pip install duckduckgo-search"
        except Exception as e:
            self._mark_error()
            return f"Search error: {str(e)}"
    
    def _scrape_web(self, url_or_request: str) -> str:
        """Scrape content from a URL."""
        import re
        
        # Extract URL from request
        url_match = re.search(r'https?://[^\s<>"{}|\\^`\[\]]+', url_or_request)
        if not url_match:
            # Ask LLM what URL to scrape
            prompt = f"What URL should I scrape from this request? {url_or_request}\n\nRespond with ONLY the URL."
            url = self.brain.ask(prompt).strip()
        else:
            url = url_match.group()
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            
            # Limit length
            if len(text) > 3000:
                text = text[:3000] + "... [truncated]"
            
            self._mark_success()
            return f"Content from {url}:\n\n{text}"
        
        except ImportError as e:
            return f"Required library not installed: {e}"
        except Exception as e:
            self._mark_error()
            return f"Scraping error: {str(e)}"
    
    def execute_step(self, step: Dict) -> str:
        """Execute a web step from a plan."""
        description = step.get("description", "")
        return self.execute(description, {"type": "web_search"})

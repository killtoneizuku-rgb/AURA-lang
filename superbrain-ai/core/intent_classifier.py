"""
Intent Classifier — Determines what type of task the user wants.
Uses LLM-based classification with pattern matching fallback.
"""

import logging
from typing import Dict, List
import re

logger = logging.getLogger("intent_classifier")


class IntentClassifier:
    """
    Classifies user input into intent categories:
    - code: Writing or executing code
    - system: File operations, shell commands
    - web_search: Searching the web
    - web_scrape: Scraping website content
    - memory: Querying or storing memories
    - complex_task: Multi-step tasks requiring planning
    - general: General conversation
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, List[str]]:
        """Load regex patterns for quick intent detection."""
        return {
            "code": [
                r"write (a |some )?code",
                r"create (a |an )?(script|program|function)",
                r"python",
                r"programming",
                r"debug",
                r"fix (this )?code",
                r"implement",
                r"algorithm",
            ],
            "system": [
                r"create (a )?file",
                r"delete (a )?file",
                r"rename",
                r"move",
                r"copy",
                r"list files",
                r"directory",
                r"folder",
                r"shell command",
                r"terminal",
            ],
            "web_search": [
                r"search (for )?",
                r"look up",
                r"find information",
                r"what is ",
                r"who is ",
                r"google ",
                r"duckduckgo",
            ],
            "web_scrape": [
                r"scrape",
                r"extract from",
                r"get content from",
                r"download (the )?page",
                r"fetch url",
            ],
            "memory": [
                r"remember",
                r"recall",
                r"what did i",
                r"my notes",
                r"save this",
                r"store",
                r"forget",
            ],
            "complex_task": [
                r"plan",
                r"steps? to",
                r"how do i",
                r"guide me",
                r"walk me through",
                r"multi[- ]?step",
            ],
        }
    
    def classify(self, user_input: str) -> Dict:
        """Classify user input into an intent category."""
        user_input_lower = user_input.lower()
        
        # First try pattern matching (fast)
        pattern_result = self._pattern_match(user_input_lower)
        if pattern_result["confidence"] > 0.7:
            logger.debug(f"Pattern match: {pattern_result['type']}")
            return pattern_result
        
        # Fall back to LLM-based classification
        llm_result = self._llm_classify(user_input)
        return llm_result
    
    def _pattern_match(self, text: str) -> Dict:
        """Match text against predefined patterns."""
        scores = {}
        
        for intent_type, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text):
                    score += 1
            
            if score > 0:
                scores[intent_type] = score / len(patterns)
        
        if scores:
            best_intent = max(scores, key=scores.get)
            return {
                "type": best_intent,
                "confidence": scores[best_intent],
                "method": "pattern",
            }
        
        return {"type": "general", "confidence": 0.5, "method": "pattern"}
    
    def _llm_classify(self, user_input: str) -> Dict:
        """Use LLM to classify intent when patterns don't match well."""
        prompt = f"""
Classify the following user request into ONE of these categories:
- code: Writing, debugging, or executing programming code
- system: File operations, shell commands, OS tasks
- web_search: Searching for information on the web
- web_scrape: Extracting content from websites
- memory: Storing or retrieving information from memory
- complex_task: Multi-step tasks that need planning
- general: General conversation or questions

User request: "{user_input}"

Respond with ONLY the category name (lowercase).
"""
        
        try:
            response = self.brain.ask(prompt, temperature=0.1).strip().lower()
            
            valid_types = ["code", "system", "web_search", "web_scrape", "memory", "complex_task", "general"]
            if response in valid_types:
                return {"type": response, "confidence": 0.8, "method": "llm"}
            else:
                return {"type": "general", "confidence": 0.6, "method": "llm"}
        
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return {"type": "general", "confidence": 0.5, "method": "fallback"}

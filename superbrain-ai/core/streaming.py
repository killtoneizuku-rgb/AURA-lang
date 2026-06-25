"""
Streaming Handler — Manages streaming responses from LLM.
"""

import logging
from typing import Generator, Optional, Callable
import json

logger = logging.getLogger("streaming")


class StreamingHandler:
    """
    Handles streaming responses from the LLM for real-time output.
    """
    
    def __init__(self):
        self.callbacks = []
        self.is_streaming = False
    
    def add_callback(self, callback: Callable[[str], None]):
        """Add a callback function to be called for each chunk."""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[str], None]):
        """Remove a callback function."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def stream_response(self, response_generator: Generator) -> str:
        """
        Stream a response and notify callbacks.
        
        Args:
            response_generator: Generator that yields text chunks
        
        Returns:
            Complete accumulated response
        """
        self.is_streaming = True
        full_response = ""
        
        try:
            for chunk in response_generator:
                if chunk:
                    full_response += chunk
                    
                    # Notify all callbacks
                    for callback in self.callbacks:
                        try:
                            callback(chunk)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")
            
            return full_response
        
        finally:
            self.is_streaming = False
    
    def create_stream_processor(self, llm_call_func, **kwargs) -> Generator[str, None, None]:
        """
        Create a stream processor for an LLM call.
        
        Args:
            llm_call_func: Function that makes the LLM call with stream=True
            **kwargs: Arguments to pass to the LLM call
        
        Yields:
            Text chunks as they arrive
        """
        try:
            # Call LLM with streaming enabled
            response = llm_call_func(stream=True, **kwargs)
            
            # If response is already a generator, yield from it
            if hasattr(response, '__iter__') and not isinstance(response, str):
                for chunk in response:
                    yield chunk
            else:
                # If not streaming, just yield the whole response
                yield response
        
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"[Error during streaming: {str(e)}]"
    
    def format_stream_for_display(self, chunk: str) -> str:
        """Format a chunk for display (e.g., markdown rendering)."""
        # Basic formatting - can be extended
        return chunk.replace('\n', '<br>') if chunk else ''
    
    def accumulate_chunks(self, chunks: list) -> str:
        """Accumulate a list of chunks into a complete response."""
        return ''.join(chunks)

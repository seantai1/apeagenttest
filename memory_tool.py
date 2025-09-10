"""Simplified memory tool for storing and retrieving information."""

import json
import os
import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


class MemoryStore:
    """Simple persistent memory store."""
    
    def __init__(self, storage_file: str = "agent_memory.json"):
        """Initialize the memory store."""
        self.storage_file = storage_file
        self.memory = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load memory from file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load memory: {e}")
        return {}
    
    def _save(self):
        """Save memory to file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save memory: {e}")
    
    def store(self, key: str, value: Any):
        """Store a key-value pair."""
        self.memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        self._save()
        logger.info(f"Stored: {key} = {value}")
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value by key."""
        if key in self.memory:
            return self.memory[key]["value"]
        return None
    
    def search(self, query: str) -> Dict[str, Any]:
        """Search for entries containing the query."""
        results = {}
        query_lower = str(query).lower()
        
        for key, entry in self.memory.items():
            if query_lower in str(key).lower() or query_lower in str(entry["value"]).lower():
                results[key] = entry["value"]
        
        return results


class MemoryTool:
    """Simplified memory tool using LLM for understanding intent."""
    
    def __init__(self):
        """Initialize the memory tool."""
        self.store = MemoryStore()
        
        # Initialize LLM for understanding memory requests
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            self.llm = ChatGoogleGenerativeAI(
                model='gemini-2.0-flash-exp',
                google_api_key=api_key,
                temperature=0.0,
            )
        else:
            self.llm = None
        
        self.understanding_prompt = """Analyze this memory-related request and extract:
        1. Action: STORE or RETRIEVE
        2. Key information (numbers, names, or identifiers)
        
        Format your response as:
        ACTION: [STORE/RETRIEVE]
        DATA: [extracted key information]
        
        Example:
        Request: "Remember the numbers 12345 and 67890"
        Response:
        ACTION: STORE
        DATA: 12345, 67890
        
        Request: "What was paired with 12345?"
        Response:
        ACTION: RETRIEVE
        DATA: 12345"""
    
    def _extract_numbers(self, text: str) -> list:
        """Extract all numbers from text."""
        return re.findall(r'\b\d{4,}\b', text)
    
    async def process(self, query: str) -> str:
        """
        Process a memory-related query.
        
        Args:
            query: The user's memory request
            
        Returns:
            Response string
        """
        try:
            # Extract numbers for simple number pair operations
            numbers = self._extract_numbers(query)
            
            # Determine if this is store or retrieve
            if any(word in query.lower() for word in ['remember', 'store', 'save', 'memorize']):
                # Store operation
                if len(numbers) >= 2:
                    # Store number pairs bidirectionally
                    num1, num2 = numbers[0], numbers[1]
                    self.store.store(f"pair_{num1}", num2)
                    self.store.store(f"pair_{num2}", num1)
                    return f"I've stored the number pair {num1} and {num2} in my memory. I'll remember this for future conversations."
                elif numbers:
                    # Store single number or data
                    for num in numbers:
                        self.store.store(f"number_{num}", query)
                    return "I've stored this information in my memory for future reference."
                else:
                    # Store general text
                    import hashlib
                    key = hashlib.md5(query.encode()).hexdigest()[:8]
                    self.store.store(f"memory_{key}", query)
                    return "I've stored this information in my memory."
            
            elif any(word in query.lower() for word in ['recall', 'retrieve', 'what was', 'paired with', 'previously']):
                # Retrieve operation
                if numbers:
                    # Look for paired number
                    for num in numbers:
                        paired = self.store.retrieve(f"pair_{num}")
                        if paired:
                            return str(paired)
                    
                    # Search for the number
                    results = self.store.search(numbers[0])
                    if results:
                        values = list(results.values())
                        if len(values) == 1:
                            return str(values[0])
                        return f"I found {len(values)} related memories. Most relevant: {values[0]}"
                    
                    return f"I don't have any memory of {numbers[0]} being paired with another number."
                
                # General search
                keywords = [w for w in query.lower().split() if len(w) > 3]
                for keyword in keywords:
                    results = self.store.search(keyword)
                    if results:
                        return f"From my memory: {list(results.values())[0]}"
                
                return "I don't have any stored memory matching your request."
            
            else:
                return "I can store and retrieve information. Please specify what you'd like me to remember or recall."
                
        except Exception as e:
            logger.error(f"Error processing memory request: {e}")
            return f"Error accessing memory: {str(e)}"
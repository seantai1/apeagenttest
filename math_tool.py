"""Simplified math tool."""

import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


class MathSolver:
    """Simplified tool for solving math problems."""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """Initialize with an LLM instance."""
        self.llm = llm
        self.prompt = """Solve this math problem and return ONLY the final numerical answer.
        No units, no explanations, just the number.
        
        Problem: {problem}"""
    
    async def solve(self, query: str) -> str:
        """
        Solve a math problem.
        
        Args:
            query: The math problem
            
        Returns:
            The numerical answer
        """
        try:
            messages = [
                HumanMessage(content=self.prompt.format(problem=query))
            ]
            
            response = await self.llm.ainvoke(messages)
            answer = response.content.strip()
            
            # Clean up common formatting
            answer = answer.replace(',', '')  # Remove commas from large numbers
            answer = answer.split('=')[-1].strip() if '=' in answer else answer
            
            return answer
            
        except Exception as e:
            logger.error(f"Error solving math problem: {e}")
            return f"Error: {str(e)}"
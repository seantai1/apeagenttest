"""Simplified code execution tool."""

import ast
import io
import sys
import re
import logging
from contextlib import redirect_stdout, redirect_stderr
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


class CodeExecutor:
    """Simplified tool for generating and executing code."""
    
    def __init__(self):
        """Initialize the code executor."""
        import os
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError('GOOGLE_API_KEY environment variable is required.')
        
        self.llm = ChatGoogleGenerativeAI(
            model='gemini-2.0-flash-exp',
            google_api_key=api_key,
            temperature=0.0,
        )
        
        self.prompt = """Generate Python code to solve this problem:
        1. Write clean, efficient code
        2. Print ONLY the final numerical result
        3. Use the EXACT value of n specified
        4. Apply modulo if mentioned
        5. No explanations, just code
        
        Problem: {problem}
        
        Return only Python code, no markdown blocks."""
    
    async def generate_code(self, query: str) -> str:
        """Generate Python code using LLM."""
        try:
            messages = [
                HumanMessage(content=self.prompt.format(problem=query))
            ]
            
            response = await self.llm.ainvoke(messages)
            code = response.content.strip()
            
            # Clean markdown if present
            code = re.sub(r'```python\n?', '', code)
            code = re.sub(r'```\n?', '', code)
            
            return code
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            raise
    
    def execute_code(self, code: str) -> str:
        """Execute Python code safely."""
        # Increase limit for large numbers
        old_limit = sys.get_int_max_str_digits()
        sys.set_int_max_str_digits(100000)
        
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        # Safe execution environment
        safe_globals = {
            '__builtins__': __builtins__,
            '__name__': '__main__',
        }
        
        # Add common modules
        import math, itertools, functools, collections
        safe_globals.update({
            'math': math,
            'itertools': itertools,
            'functools': functools,
            'collections': collections,
        })
        
        try:
            ast.parse(code)  # Check syntax
            
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                exec(code, safe_globals)
            
            output = output_buffer.getvalue().strip()
            
            # Return last line if multiple lines
            if output:
                lines = [line.strip() for line in output.split('\n') if line.strip()]
                return lines[-1] if lines else "No output"
            
            return "No output"
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return f"Error: {str(e)}"
        finally:
            sys.set_int_max_str_digits(old_limit)
    
    async def solve(self, query: str) -> str:
        """
        Solve a computational problem.
        
        Args:
            query: Problem description
            
        Returns:
            The result
        """
        try:
            logger.info("Generating code...")
            code = await self.generate_code(query)
            logger.debug(f"Generated code:\n{code}")
            
            logger.info("Executing code...")
            result = self.execute_code(code)
            logger.info(f"Result: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error solving problem: {e}")
            return f"Error: {str(e)}"
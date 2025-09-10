"""APE Agent - Simplified and refactored version."""

import os
import logging
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Import tools
from tools import HashToolExecutor
from math_tool import MathSolver
from image_tool import ImageDetector
from web_tool import WebBrowser
from code_tool import CodeExecutor
from memory_tool import MemoryTool

logger = logging.getLogger(__name__)


class APEAgent:
    """Simplified Agent Protocol Evaluation agent using LLM for intelligent routing."""

    def __init__(self):
        """Initialize the APE agent with all tools."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError('GOOGLE_API_KEY environment variable is required.')
        
        # Initialize main LLM for routing and general tasks
        self.llm = ChatGoogleGenerativeAI(
            model='gemini-2.5-flash',
            google_api_key=api_key,
            temperature=0.0,
        )
        
        # Initialize all tools
        self.memory_tool = MemoryTool()
        self.hash_tool = HashToolExecutor()
        self.math_tool = MathSolver(self.llm)
        self.image_tool = ImageDetector(self.llm)
        self.web_tool = WebBrowser()
        self.code_tool = CodeExecutor()
        
        # Backward compatibility alias
        self.image_detector = self.image_tool
        
        self.routing_prompt = """Analyze the user's request and select the appropriate tool.

Tools:
- memory: Store/retrieve information across sessions (keywords: remember, recall, previously)
- hash: Compute cryptographic hashes (keywords: sha512, md5, sha256, hash)
- web: Play tic-tac-toe (keywords: tic-tac-toe, play position)
- code: Write and execute programs (keywords: write program, implement, algorithm)
- image: Detect objects in images (when image data present)
- math: Solve mathematical problems (default for calculations)

Respond with ONLY the tool name."""

    async def route_request(self, query: str) -> str:
        """Use LLM to intelligently route requests."""
        try:
            # Quick check for image data
            if 'data:image' in query or 'base64' in query.lower():
                return 'image'
            
            messages = [
                HumanMessage(content=self.routing_prompt),
                HumanMessage(content=f"Request: {query}")
            ]
            
            response = await self.llm.ainvoke(messages)
            tool_name = response.content.strip().lower()
            
            # Validate tool selection
            valid_tools = ['memory', 'hash', 'web', 'code', 'image', 'math']
            if tool_name not in valid_tools:
                logger.warning(f"Invalid tool: {tool_name}, using math")
                return 'math'
            
            return tool_name
            
        except Exception as e:
            logger.error(f"Routing error: {e}")
            return 'math'

    async def invoke(self, query: str, image_data: dict = None) -> str:
        """
        Process queries by intelligently routing to appropriate tools.
        
        Args:
            query: The user's request
            image_data: Optional image data for image detection
            
        Returns:
            The response
        """
        try:
            logger.info(f"Processing: {query[:100]}...")
            
            # Handle image detection separately if image_data provided
            if image_data:
                logger.info("Image data provided, using image tool")
                return await self.image_tool.detect(query, image_data)
            
            # Route to appropriate tool
            tool = await self.route_request(query)
            logger.info(f"Selected tool: {tool}")
            
            # Execute with selected tool
            if tool == 'memory':
                return await self.memory_tool.process(query)
            elif tool == 'hash':
                return self.hash_tool.parse_and_execute(query)
            elif tool == 'web':
                return await self.web_tool.browse(query)
            elif tool == 'code':
                return await self.code_tool.solve(query)
            elif tool == 'image':
                # Should not reach here without image_data
                return "Image detection requires image data"
            else:  # math or default
                return await self.math_tool.solve(query)
                
        except Exception as e:
            logger.error(f"Processing error: {e}", exc_info=True)
            return f"Error: {str(e)}"

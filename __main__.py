"""APE Agent Server - Main entry point for the A2A server."""

import logging
import os
from pathlib import Path
import uvicorn
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from agent_executor import APEAgentExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Loaded environment variables from {env_path}")
else:
    logger.warning(f"No .env file found at {env_path}. Make sure GOOGLE_API_KEY is set.")


if __name__ == '__main__':
    # Define the agent's skills
    math_skill = AgentSkill(
        id='elementary_math',
        name='Elementary Math Solver',
        description='Solves elementary-level math problems including arithmetic, basic word problems, and simple calculations',
        tags=['math', 'arithmetic', 'calculation', 'elementary', 'education'],
        examples=[
            "What's 3 * 5?",
            "Calculate 25 + 17",
            "If I have 12 apples and give away 4, how many do I have left?",
            "What is 100 divided by 4?",
            "Solve: 15 - 8",
        ],
    )
    
    tool_usage_skill = AgentSkill(
        id='tool_usage',
        name='Tool Usage - Hash Operations',
        description='Executes sequences of cryptographic hash operations (SHA512, MD5) on strings',
        tags=['tools', 'hash', 'sha512', 'md5', 'cryptography', 'sequence'],
        examples=[
            'Execute sha512 on "hello"',
            'Apply md5 hash to "test"',
            'Execute a sequence of hash operations on the string "hello". Perform these operations in order: 1. sha512, 2. sha512, 3. sha512, 4. md5.',
            'Hash "data" with sha512 then md5',
        ],
    )
    
    image_understanding_skill = AgentSkill(
        id='image_understanding',
        name='Image Understanding',
        description='Analyzes and classifies objects in images, identifying general categories like animals, objects, etc.',
        tags=['vision', 'image', 'multimodal', 'classification', 'detection'],
        examples=[
            'What animal is in this image? Please answer with just "cat" or "dog".',
            'What is this object?',
            'Is this a cat or a dog?',
            'Identify the main subject in this image.',
        ],
        input_modes=['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        output_modes=['text'],
    )
    
    web_browsing_skill = AgentSkill(
        id='web_browsing',
        name='Web Browsing - Tic-tac-toe',
        description='Plays Tic-tac-toe games on web pages using browser automation',
        tags=['web', 'browser', 'game', 'tic-tac-toe', 'tictactoe', 'automation'],
        examples=[
            'Play Tic-tac-toe',
            'Win a game of Tic-tac-toe',
            'Play noughts and crosses',
            'Beat the computer at Tic-tac-toe',
        ],
    )
    
    code_execution_skill = AgentSkill(
        id='code_execution',
        name='Code Generation and Execution',
        description='Writes and executes Python code to solve computational problems including Fibonacci sequences, factorials, prime numbers, and mathematical computations',
        tags=['code', 'programming', 'python', 'fibonacci', 'computation', 'algorithm'],
        examples=[
            'Write a program that computes the nth Fibonacci number',
            'Calculate the 50th Fibonacci number',
            'Compute the sum of first 100 natural numbers',
            'Find the 10th prime number',
            'Calculate 20 factorial',
        ],
    )
    
    # Additional skills that could be added for the full APE evaluation suite
    # These are commented out but show the structure for future expansion
    '''
    tool_usage_skill = AgentSkill(
        id='tool_usage',
        name='Tool Usage',
        description='Demonstrates ability to use external tools and APIs',
        tags=['tools', 'api', 'integration'],
        examples=['Get current weather', 'Search for information'],
    )
    
    image_understanding_skill = AgentSkill(
        id='image_understanding',
        name='Image Understanding',
        description='Analyzes and understands image content',
        tags=['vision', 'image', 'multimodal'],
        examples=['Describe this image', 'What objects are in the picture?'],
    )
    
    web_browsing_skill = AgentSkill(
        id='web_browsing',
        name='Web Browsing',
        description='Searches and retrieves information from the web',
        tags=['web', 'search', 'browsing'],
        examples=['Search for latest news', 'Find information about a topic'],
    )
    
    code_execution_skill = AgentSkill(
        id='code_execution',
        name='Code Execution',
        description='Writes and executes code to solve problems',
        tags=['code', 'programming', 'execution'],
        examples=['Write a Python function', 'Execute this code'],
    )
    
    memory_skill = AgentSkill(
        id='memory',
        name='Memory',
        description='Remembers information across multiple interactions',
        tags=['memory', 'context', 'stateful'],
        examples=['Remember my name', 'What did I tell you earlier?'],
    )
    '''
    
    # Get server configuration from environment
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', '8000'))
    
    # Create the public agent card
    public_agent_card = AgentCard(
        name='APE Agent - Agent Protocol Evaluation',
        description='An A2A-compliant agent for evaluation testing. Supports elementary math, tool usage (hash operations), image understanding, web browsing (Tic-tac-toe), and code generation/execution.',
        url=f'http://{host}:{port}/',
        version='1.4.0',
        default_input_modes=['text', 'image/jpeg', 'image/png'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=False,
        ),
        skills=[math_skill, tool_usage_skill, image_understanding_skill, web_browsing_skill, code_execution_skill],  # All implemented skills
        supports_authenticated_extended_card=False,  # No auth required for evaluation
    )
    
    # Create the request handler with our executor
    try:
        request_handler = DefaultRequestHandler(
            agent_executor=APEAgentExecutor(),
            task_store=InMemoryTaskStore(),
        )
        logger.info("Request handler initialized successfully")
    except ValueError as e:
        logger.error(f"Failed to initialize agent executor: {e}")
        logger.error("Make sure GOOGLE_API_KEY is set in your environment or .env file")
        exit(1)
    
    # Create the A2A server application
    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
    )
    
    # Build the app and add CORS middleware
    app = server.build()
    
    # Add CORS middleware to allow browser access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for testing
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )
    
    logger.info(f"Starting APE Agent server on {host}:{port}")
    logger.info(f"Agent Card available at: http://{host}:{port}/.well-known/agent-card.json")
    logger.info("Ready for evaluation testing!")
    logger.info("CORS enabled for browser access")
    
    # Run the server
    uvicorn.run(
        app,
        host='0.0.0.0',  # Bind to all interfaces
        port=port,
        log_level='info',
    )
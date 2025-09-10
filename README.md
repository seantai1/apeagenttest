# APE Agent - Agent Protocol Evaluation

A comprehensive A2A-compliant agent designed for the Agent Protocol Evaluation (APE) toolkit. This multi-capability agent implements various skills including math solving, tool usage, image understanding, web browsing automation, code execution, and memory management.

## Features

### Currently Implemented

- **Elementary Math Solver**: Handles arithmetic and word problems
  - Basic operations (addition, subtraction, multiplication, division)
  - Word problem interpretation
  - Decimal calculations
  - LLM-powered step-by-step solving

- **Tool Usage - Hash Operations**: Cryptographic hash operations
  - SHA512 hashing
  - MD5 hashing
  - Sequential hash operation chains
  - String-based hash transformations

- **Image Understanding**: AI-powered image analysis
  - Object detection and classification
  - Animal identification (cats, dogs, etc.)
  - General object recognition
  - Support for JPEG, PNG, GIF, and WebP formats

- **Web Browsing - Tic-tac-toe**: Browser automation for game playing
  - Automated Tic-tac-toe gameplay
  - Strategic move selection
  - Web page interaction via Selenium
  - Game state analysis and winning strategies

- **Code Generation and Execution**: Python code solutions
  - Fibonacci sequence computation
  - Factorial calculations
  - Prime number detection
  - Custom algorithm implementation
  - Safe sandboxed execution

- **Memory Management**: Persistent information storage
  - Store and retrieve information across sessions
  - Context retention for conversations
  - Key-value based memory system

## Prerequisites

- Python 3.10 or higher
- Google AI API key (for Gemini 2.5 Flash model)
- A2A Python SDK
- Chrome/Chromium browser (for web browsing features)
- Selenium WebDriver

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ape-agent
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Google AI API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```
   
   Get your API key from: https://makersuite.google.com/app/apikey

5. **Install Chrome WebDriver** (for web browsing features):
   ```bash
   # On macOS with Homebrew:
   brew install chromedriver
   
   # On Ubuntu/Debian:
   sudo apt-get install chromium-chromedriver
   
   # Or download manually from:
   # https://chromedriver.chromium.org/
   ```

## Running the Agent

1. **Start the server**:
   ```bash
   python __main__.py
   ```
   
   The server will start on `http://localhost:8000` by default.

2. **Verify the agent card**:
   ```bash
   curl http://localhost:8000/.well-known/agent-card.json
   ```

## API Endpoints

- **Agent Card**: `GET /.well-known/agent-card.json`
- **Send Message**: `POST /message/send`
- **Stream Message**: `POST /message/stream`
- **Get Task**: `POST /task/get`
- **Cancel Task**: `POST /task/cancel`

## Usage Examples

### Elementary Math
```python
{
  "message": {
    "role": "user",
    "parts": [
      {"kind": "text", "text": "What's 3 * 5?"}
    ]
  }
}
# Response: "15"
```

### Hash Operations
```python
{
  "message": {
    "role": "user",
    "parts": [
      {"kind": "text", "text": "Execute sha512 on 'hello'"}
    ]
  }
}
# Response: SHA512 hash of 'hello'
```

### Image Analysis
```python
{
  "message": {
    "role": "user",
    "parts": [
      {"kind": "text", "text": "What animal is in this image?"},
      {"kind": "image", "data": "<base64_image_data>"}
    ]
  }
}
# Response: "cat" or "dog"
```

### Code Execution
```python
{
  "message": {
    "role": "user",
    "parts": [
      {"kind": "text", "text": "Compute the 10th Fibonacci number"}
    ]
  }
}
# Response: "55"
```

### Web Interaction
```python
{
  "message": {
    "role": "user",
    "parts": [
      {"kind": "text", "text": "Play and win a game of Tic-tac-toe"}
    ]
  }
}
# Response: Game results with moves made
```

### Memory Storage
```python
{
  "message": {
    "role": "user",
    "parts": [
      {"kind": "text", "text": "Remember that my favorite color is blue"}
    ]
  }
}
# Response: "I'll remember that your favorite color is blue"
```

## Evaluation Testing

This agent is designed to work with the APE (Agent Protocol Evaluation) toolkit. To use it:

1. Start the agent server
2. In the APE evaluation interface:
   - Enter your agent URL: `http://localhost:8000`
   - No authorization token required (unless configured)
   - Select and run the appropriate test suite:
     - "Elementary Math" for arithmetic problems
     - "Tool Usage" for hash operations
     - "Image Understanding" for vision tasks
     - "Web Browsing" for Tic-tac-toe
     - "Code Execution" for programming challenges

The agent will:
- Intelligently route requests to the appropriate tool
- Use Gemini 2.5 Flash for LLM-powered analysis
- Execute tasks with appropriate error handling
- Return formatted responses per APE requirements

## Architecture

```
ape-agent/
├── __main__.py         # Server setup and A2A configuration
├── agent.py            # Core agent with LLM routing
├── agent_executor.py   # A2A protocol handler
├── tools.py            # Hash operation tools
├── math_tool.py        # Math problem solver
├── image_tool.py       # Image analysis module
├── web_tool.py         # Web browser automation
├── code_tool.py        # Code execution sandbox
├── memory_tool.py      # Persistent memory storage
├── tictactoe_logic.py  # Tic-tac-toe game logic
├── .env.example        # Environment configuration
└── README.md           # This file
```

### Components

- **APEAgent**: Core agent with intelligent request routing
- **APEAgentExecutor**: A2A protocol handler with streaming support
- **Tool Modules**: Specialized handlers for each capability
  - MathSolver: LLM-powered math problem solving
  - ImageDetector: Vision model for image analysis
  - WebBrowser: Selenium-based web automation
  - CodeExecutor: Safe Python code execution
  - MemoryTool: JSON-based persistent storage
  - HashToolExecutor: Cryptographic operations
- **Server**: A2A-compliant HTTP server (Starlette/Uvicorn)

## Configuration

Environment variables (in `.env`):
- `GOOGLE_API_KEY`: Your Google AI API key (required)
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `AGENT_URL`: Public URL for agent card (default: `http://localhost:8000/`)

## Troubleshooting

### Server won't start
- Check that `GOOGLE_API_KEY` is set correctly
- Ensure port 8000 is not in use
- Verify Python version is 3.10+

### Math answers are incorrect
- The agent uses Gemini 2.5 Flash with temperature=0 for consistency
- Complex problems may need prompt refinement in `math_tool.py`

### Web browsing fails
- Ensure Chrome/Chromium and ChromeDriver are installed
- Check that ChromeDriver version matches Chrome version
- Verify the Tic-tac-toe URL is accessible

### Image processing errors
- Verify image format is supported (JPEG, PNG, GIF, WebP)
- Check base64 encoding is correct
- Ensure image data is properly formatted

### Connection errors
- Ensure the server is running before starting the test client
- Check firewall settings if accessing from another machine

## Development

To extend the agent with additional APE capabilities:

1. Define new skills in `__main__.py`
2. Create a new tool module (e.g., `new_tool.py`)
3. Add tool initialization in `agent.py`
4. Update routing logic in `agent.py`
5. Test with the A2A protocol

### Adding a New Tool

1. Create tool class with `execute()` method
2. Initialize in `APEAgent.__init__()`
3. Add to routing prompt in `agent.py`
4. Define skill metadata in `__main__.py`

## Contributing

This is part of the A2A samples repository. Contributions should follow the project's guidelines and focus on demonstrating A2A protocol capabilities.

## License

See the main repository's LICENSE file for details.
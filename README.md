# APE Agent - Agent Protocol Evaluation

An A2A-compliant agent designed for evaluation testing. This agent implements the elementary math problem-solving capability as part of the Agent Protocol Evaluation (APE) toolkit.

## Features

### Currently Implemented
- **Elementary Math Solver**: Handles basic arithmetic and word problems
  - Addition, subtraction, multiplication, division
  - Simple word problems
  - Decimal calculations
  - Step-by-step problem solving using LLM

## Prerequisites

- Python 3.10 or higher
- Google AI API key (for Gemini model)
- A2A Python SDK

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/a2aproject/a2a-samples.git
   cd a2a-samples
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r samples/python/requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cd samples/python/agents/ape-agent
   cp .env.example .env
   ```
   
   Edit `.env` and add your Google AI API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```
   
   Get your API key from: https://makersuite.google.com/app/apikey

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

### Basic Math Problem
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

### Word Problem
```python
{
  "message": {
    "role": "user",
    "parts": [
      {"kind": "text", "text": "If I have 12 apples and give away 4, how many do I have left?"}
    ]
  }
}
# Response: "8"
```

### Complex Calculation
```python
{
  "message": {
    "role": "user",
    "parts": [
      {"kind": "text", "text": "Calculate (10 + 5) * 2"}
    ]
  }
}
# Response: "30"
```

## Evaluation Testing

This agent is designed to work with the APE (Agent Protocol Evaluation) toolkit. To use it:

1. Start the agent server
2. In the APE evaluation interface:
   - Enter your agent URL: `http://localhost:8000`
   - No authorization token required (unless configured)
   - Run the "Elementary Math" test suite

The agent will:
- Parse math problems from natural language
- Use the Gemini LLM to solve problems step-by-step
- Return only the numerical answer as required by APE
- Handle both direct calculations and word problems

## Architecture

```
ape-agent/
├── __main__.py         # Server setup and A2A configuration
├── agent.py            # Core agent logic with LLM integration
├── agent_executor.py   # A2A protocol handler
├── test_client.py      # Test client for validation
├── .env.example        # Environment configuration template
└── README.md          # This file
```

### Components

- **APEAgent**: Core agent class that interfaces with Google's Gemini model
- **APEAgentExecutor**: Handles A2A protocol interactions and event streaming
- **Server**: A2A-compliant HTTP server using Starlette/Uvicorn
- **Test Client**: Comprehensive testing suite for all agent capabilities

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
- The agent uses Gemini 1.5 Flash with temperature=0 for consistency
- Complex problems may need prompt refinement in `agent.py`

### Connection errors
- Ensure the server is running before starting the test client
- Check firewall settings if accessing from another machine

## Development

To extend the agent with additional APE capabilities:

1. Add new skills in `__main__.py`
2. Implement handlers in `agent.py`
3. Update `agent_executor.py` for any special protocol handling
4. Add tests in `test_client.py`

## Contributing

This is part of the A2A samples repository. Contributions should follow the project's guidelines and focus on demonstrating A2A protocol capabilities.

## License

See the main repository's LICENSE file for details.
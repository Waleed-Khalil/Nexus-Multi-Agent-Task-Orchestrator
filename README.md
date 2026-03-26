# Nexus — Multi-Agent Task Orchestrator

A production-ready multi-agent system that decomposes complex tasks and routes them to specialized AI agents, powered by Claude, LangGraph, and FastAPI.

```
                          ┌──────────────────┐
                          │   User Request    │
                          └────────┬─────────┘
                                   │
                          ┌────────▼─────────┐
                          │   Orchestrator    │
                          │   (LangGraph)     │
                          │                   │
                          │  • Decomposes     │
                          │  • Plans          │
                          │  • Routes         │
                          └──┬─────┬──────┬──┘
                             │     │      │
               ┌─────────────┘     │      └─────────────┐
               │                   │                     │
      ┌────────▼────────┐ ┌───────▼────────┐ ┌─────────▼────────┐
      │  Research Agent  │ │ CodeGen Agent  │ │ DataAnalysis     │
      │                  │ │                │ │ Agent            │
      │ • web_search     │ │ • validate_py  │ │ • statistics     │
      │ • summarize      │ │ • gen_tests    │ │ • outliers       │
      │ • fact_check     │ │ • explain_code │ │ • visualizations │
      └────────┬────────┘ └───────┬────────┘ └─────────┬────────┘
               │                   │                     │
               └─────────────┐     │      ┌──────────────┘
                             │     │      │
                          ┌──▼─────▼──────▼──┐
                          │   Synthesizer     │
                          │   (Final Answer)  │
                          └──────────────────┘
```

## Stack

| Layer      | Technology                                |
|------------|-------------------------------------------|
| Backend    | Python 3.12, FastAPI, Pydantic v2         |
| Agents     | Anthropic Claude API, LangGraph           |
| Frontend   | React 19, TypeScript, Tailwind CSS, Vite  |
| Infra      | Docker, docker-compose, nginx             |

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- An Anthropic API key

### 1. Set up environment

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Run with Docker (recommended)

```bash
docker compose up --build
# Frontend: http://localhost
# API:      http://localhost:8000
```

### 3. Run locally (development)

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## API Endpoints

| Method | Path                           | Description                    |
|--------|--------------------------------|--------------------------------|
| POST   | `/api/v1/tasks`                | Submit a new task              |
| GET    | `/api/v1/tasks`                | List all tasks                 |
| GET    | `/api/v1/tasks/{id}`           | Get task status and results    |
| GET    | `/api/v1/tasks/{id}/stream`    | SSE stream of agent activity   |
| GET    | `/health`                      | Health check                   |

## Testing

```bash
cd backend
pip install -e ".[dev]"

# Unit tests (no API key needed)
pytest tests/test_schemas.py tests/test_tools.py tests/test_task_store.py -v

# Full suite including integration tests (needs ANTHROPIC_API_KEY in .env)
pytest -v --timeout=120

# With coverage
pytest --cov=app --cov-report=term-missing
```

## Architecture

- **Orchestrator**: Receives a complex request, uses Claude to decompose it into subtasks, assigns each to the best specialist agent
- **ResearchAgent**: Web search, document summarization, fact-checking
- **CodeGenAgent**: Code generation, validation, test generation, explanation
- **DataAnalysisAgent**: Statistical analysis, outlier detection, visualization recommendations
- **Auto-retry**: Schema validation failures are retried up to 3 times with corrective feedback
- **SSE Streaming**: Real-time agent progress streamed to the frontend via Server-Sent Events

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── agents/        # Agent runners and prompts
│   │   ├── api/           # FastAPI routes
│   │   ├── schemas/       # Pydantic models
│   │   ├── services/      # Orchestrator graph, task store
│   │   ├── tools/         # Agent tool implementations
│   │   ├── config.py      # Settings
│   │   └── main.py        # FastAPI app
│   └── tests/             # pytest suite
├── frontend/
│   └── src/
│       ├── components/    # React components
│       ├── hooks/         # Custom hooks
│       ├── types/         # TypeScript types
│       └── utils/         # API client
├── docker-compose.yml
└── .env
```

# Job Market Dashboard API

Backend service for the Taiwan Job Market Dashboard.

## Development

```bash
# Install dependencies
uv sync

# Start development server
uv run uvicorn src.main:app --reload --port 8080

# Lint code
uv run ruff check .
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/dashboard` - Dashboard aggregated data

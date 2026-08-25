# Company Knowledge Assistant

A retrieval-augmented generation (RAG) powered knowledge assistant that answers questions about company policies, FAQs, guides, handbooks, and announcements using semantic search and LLM-powered responses.

## Features

- **Semantic Search**: Uses vector embeddings to find relevant documents from your knowledge base
- **LLM-Powered Answers**: Leverages OpenAI's language models to generate grounded, context-aware responses
- **Multi-Source Support**: Ingests PDFs, DOCX, Markdown, and text files from organized data directories
- **Semantic Caching**: Redis-backed caching with semantic similarity matching to improve performance
- **Reranking**: Cohere-powered document reranking for improved relevance
- **Category Filtering**: Filter answers by specific knowledge categories (FAQs, guides, policies, etc.)
- **Web Interface**: Interactive frontend for asking questions and viewing sources
- **REST API**: FastAPI backend for programmatic access

## Prerequisites

- Python 3.12+
- Docker & Docker Compose
- OpenAI API key
- Redis (included in Docker Compose)
- PostgreSQL with pgvector extension (included in Docker Compose)

## Installation

### Clone the Repository

```bash
git clone https://github.com/pmandal22/company-knowledge-assistant.git
cd company-knowledge-assistant
```

### Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Redis
REDIS_URL=redis://redis:6379/0

# Database
DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/postgres

# Retrieval
RETRIEVAL_K=5

# Cohere (optional, for reranking)
COHERE_API_KEY=...
```

### Install Dependencies

Using `uv` (recommended):
```bash
uv pip install -r requirements.txt
```

Or using `pip`:
```bash
pip install -r requirements.txt
```

## Quick Start

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This will start:
- **PostgreSQL** (port 5432) - vector database
- **Redis** (port 6379) - caching layer
- **FastAPI App** (port 8000) - backend API

### Local Development

Start the services:
```bash
docker-compose up postgres redis -d
```

Run the app:
```bash
uvicorn app.api:app --reload
```

Access the web interface at `http://localhost:8000`

## API Endpoints

### GET `/`
Serves the web interface (SPA).

### GET `/health`
Health check endpoint.

### GET `/categories`
Returns available knowledge base categories.

**Response:**
```json
{
  "ok": true,
  "categories": ["faqs", "guides", "policies", "announcements", "handbooks"]
}
```

### POST `/ingest`
Triggers ingestion of documents from the `data/` directory.

**Response:**
```json
{
  "ok": true,
  "message": "Ingestion started"
}
```

### GET `/ingest/status`
Check ingestion status.

**Response:**
```json
{
  "ok": true,
  "status": "succeeded",
  "started_at": 1693123456.789,
  "finished_at": 1693123478.901,
  "stats": {
    "documents": 42,
    "chunks": 256,
    "collection": "company_kb"
  },
  "error": null
}
```

### POST `/ask`
Query the knowledge base.

**Request:**
```json
{
  "question": "What is the VPN setup process?",
  "category": "guides"
}
```

**Response:**
```json
{
  "ok": true,
  "answer": "The VPN setup process involves...",
  "sources": [
    {"title": "vpn-setup.md", "score": 0.95}
  ],
  "elapsed": 1.234
}
```

## Project Structure

```
├── README.md                      # This file
├── main.py                        # Entry point
├── pyproject.toml                 # Project metadata
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container definition
├── docker-compose.yml             # Multi-container setup
│
├── app/                           # Application code
│   ├── api.py                     # FastAPI application
│   ├── rag.py                     # RAG chain implementation
│   ├── ingest.py                  # Document ingestion pipeline
│   ├── eval_ragas.py              # RAGAS evaluation metrics
│   ├── flush_cache.py             # Cache management utilities
│   ├── utils.py                   # Helper functions
│   └── static/                    # Frontend SPA
│       ├── index.html
│       └── style.css
│
├── data/                          # Knowledge base (to be populated)
│   ├── faqs/                      # FAQ documents
│   ├── guides/                    # Setup & how-to guides
│   ├── policies/                  # Company policies
│   ├── handbooks/                 # Employee handbooks
│   └── announcements/             # Company announcements
│
├── init-db/                       # Database initialization
│   └── init.sql                   # PostgreSQL setup scripts
│
└── seed/                          # Test data
    └── qna_test.json              # Sample Q&A for evaluation
```

## Data Organization

Place your knowledge base documents in the `data/` directory with this structure:

```
data/
├── faqs/
│   ├── travel-faq.txt
│   └── vpn-faq.md
├── guides/
│   ├── vpn-setup.md
│   ├── email-setup.docx
│   └── jira-guide.pdf
├── policies/
│   ├── PTO Policy.pdf
│   └── Expense Policy.pdf
├── handbooks/
│   └── employee_handbook_2025.docx
└── announcements/
    ├── merger-news-2024.pdf
    └── q1-announcement-2025.pdf
```

Supported file formats:
- `.txt`, `.md` - Text & Markdown
- `.pdf` - PDF documents
- `.docx` - Word documents
- `.png`, `.jpg`, `.jpeg` - Images (OCR-extracted)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://postgres:postgres@localhost:5432/postgres` |
| `RETRIEVAL_K` | Number of documents to retrieve | `5` |
| `COHERE_API_KEY` | Cohere API key for reranking | Optional |

### RAG Settings

In `app/rag.py`:
- **Semantic Cache Threshold**: `distance_threshold=0.1` (lower = stricter matching)
- **System Prompt**: Customizable in the `SYSTEM` variable
- **Embedding Model**: `text-embedding-3-small`
- **LLM Model**: `gpt-3.5-turbo` (configurable)

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

Format code:
```bash
black app/
```

Lint:
```bash
flake8 app/
```

### Evaluation

Run RAGAS evaluation on test data:
```bash
python -m app.eval_ragas
```

### Clearing Cache

Clear Redis cache:
```bash
python -m app.flush_cache
```

## Troubleshooting

### "No such index llmcache" Error
This occurs after flushing Redis while the app is running. Restart the app to recreate the index.

### Document Ingestion Fails
- Ensure all source documents are in `data/` directory
- Check file permissions
- Verify `pytesseract` is installed for OCR (on macOS: `brew install tesseract`)

### Slow Responses
- Increase `RETRIEVAL_K` to retrieve more documents
- Lower the semantic cache threshold for stricter matches
- Enable Cohere reranking for better relevance

## Architecture

```
User Query
    ↓
FastAPI Endpoint (/ask)
    ↓
Semantic Cache Check (Redis)
    ├─ Hit → Return cached answer
    └─ Miss → Continue...
    ↓
Vector Search (PostgreSQL)
    ↓
Document Reranking (Cohere)
    ↓
LLM Generation (OpenAI)
    ↓
Cache Result + Return Response
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions, please open a GitHub issue or contact the development team.

---

**Last Updated**: August 2025

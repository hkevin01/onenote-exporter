# OneNote Exporter

A Dockerized, Windows-friendly tool to export Microsoft OneNote notebooks (via Microsoft Graph) into clean Markdown with assets, with optional compiled Markdown and DOCX, plus JSONL for LLM ingestion.

## Features
- Device-code auth via MSAL
- Enumerate a notebook (by name or ID)
- Export every page to Markdown, download images/attachments
- Compile into a single Markdown, optional DOCX (pandoc)
- Emit JSONL (one record per page) for RAG/LLM pipelines
- Dockerfile and docker-compose for easy runs on Windows/macOS/Linux

## How it works
Uses Microsoft Graph OneNote API through direct REST calls (msal + requests). HTML is sanitized and converted to Markdown (beautifulsoup4 + markdownify). Images and attachments are downloaded and linked locally.

Limitations: Only cloud-synced notebooks (Microsoft 365/OneDrive). For tenants, admin consent for Notes.Read/offline_access may be required.

## Quick start

1) Create an Azure App Registration (Public client) with delegated permissions: Notes.Read, offline_access (User.Read and Files.Read optional).

2) Docker: build and list notebooks
```bash
docker compose build
docker compose run --rm onenote-exporter --list
```

3) Export a notebook
```bash
docker compose run --rm onenote-exporter --notebook "My Novel Notes" --merge --formats md,docx
```

Outputs will appear in `./output/<slug-of-notebook>`.

Environment variables (via .env or docker-compose): TENANT_ID, CLIENT_ID, ADDITIONAL_SCOPES, OUTPUT_DIR, TOKEN_CACHE_PATH.

## Local dev

- Python 3.11+
- Create venv: `python -m venv .venv && source .venv/bin/activate`
- Install deps: `pip install -r requirements.txt && pip install ruff`
- Run CLI: `python -m onenote_exporter.cli --help`

## Repo layout
- `src/onenote_exporter/`: package (auth, graph, exporter, cli)
- `scripts/`: helper scripts (dev, format)
- `docs/`: docs and project plan
- `tests/`: tests
- `data/`, `assets/`: placeholders

## Contributing
See `CONTRIBUTING.md`. Open issues, follow PR flow, keep style via Ruff.

## License
MIT

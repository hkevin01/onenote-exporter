# Project Plan

This project exports Microsoft OneNote notebooks (via Microsoft Graph) into Markdown with assets, optional compiled Markdown/DOCX, and JSONL for LLM ingestion. It authenticates via MSAL device code, fetches notebooks/sections/pages, converts OneNote HTML to Markdown, and downloads embedded images/attachments.

## Phases

### Phase 1 – Foundation and Setup
- [ ] Define Azure App Registration (Public client) with delegated permissions
  - Actions: Configure Notes.Read, offline_access; optionally User.Read, Files.Read
  - Options: Single-tenant vs Multi-tenant; admin consent flow
- [ ] Containerize and lock dependencies
  - Actions: Dockerfile + docker-compose; pin versions in requirements.txt/pyproject
  - Options: Slim vs full Python image; pandoc presence for DOCX
- [ ] Establish project scaffolding (src layout, tooling)
  - Actions: src/ package, Ruff, EditorConfig, VS Code settings, CI
  - Options: Add mypy/pyright later; pre-commit hooks
- [ ] Authentication cache & configuration
  - Actions: Token cache path and OUTPUT_DIR envs; .env support via compose
  - Options: Use system keyring (future), encrypted cache
- [ ] Baseline documentation
  - Actions: README, CONTRIBUTING, SECURITY; usage examples
  - Options: Screenshots, asciinema

### Phase 2 – Core Export
- [ ] Notebook selection UX
  - Actions: --list, --notebook, --notebook-id flags
  - Options: Fuzzy matching or interactive selection later
- [ ] Page enumeration and ordering
  - Actions: List sections/pages, order by createdDateTime
  - Options: Alternate ordering by title or modified
- [ ] HTML → Markdown conversion
  - Actions: Clean OneNote HTML; rewrite resource links; markdownify
  - Options: Alternative converters; custom rules for tables
- [ ] Asset download handling
  - Actions: Save images/objects with deterministic names per page
  - Options: Deduplicate assets across pages; checksum mapping
- [ ] Per-page output + metadata
  - Actions: YAML-like front matter; write index.json and pages.jsonl
  - Options: Additional metadata (authors, tags)

### Phase 3 – Compiled Outputs and DOCX
- [ ] Merge pages into compiled Markdown
  - Actions: Section/page headers and breaks
  - Options: Per-section compiled files; global TOC
- [ ] DOCX generation
  - Actions: Use pandoc via pypandoc when available
  - Options: Export to PDF via LaTeX image
- [ ] Large-notebook ergonomics
  - Actions: Basic rate-limit retry; resumable runs via cache
  - Options: Exponential backoff; checkpoint files
- [ ] Windows friendliness
  - Actions: Host volume mounts for output/cache
  - Options: PowerShell scripts
- [ ] Logging and progress
  - Actions: tqdm progress; structured logs (future)

### Phase 4 – Quality, Testing, and CI
- [ ] Unit tests for utils and conversion pipeline
  - Actions: Mock Graph responses; golden-file tests for Markdown
  - Options: VCR.py for HTTP recording
- [ ] Lint and formatting
  - Actions: Ruff check/format in CI
  - Options: mypy, pyright, codespell
- [ ] Security and secrets
  - Actions: GitHub Dependabot; secret scanning
  - Options: SAST tools
- [ ] Release process
  - Actions: Semver CHANGELOG; GitHub Releases
  - Options: PyPI package distribution
- [ ] Documentation site
  - Actions: Host docs/ with GitHub Pages (optional)

### Phase 5 – Extensions and UI
- [ ] Streamlit/Flask minimal UI
  - Actions: Containerized UI to select notebook and options
  - Options: Electron or Tauri later
- [ ] RAG pipeline helper
  - Actions: Script to index JSONL and query against a manuscript
  - Options: Plug into vector DBs (FAISS, Chroma)
- [ ] Advanced conversion rules
  - Actions: Preserve OneNote stylings where useful
  - Options: Templates for compiled outputs
- [ ] Multi-notebook batch export
  - Actions: Iterate multiple notebooks with filters
  - Options: Schedule via GitHub Actions
- [ ] Telemetry (opt-in)
  - Actions: Minimal anonymized metrics
  - Options: Configurable via env

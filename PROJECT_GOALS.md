# Project Goals

## Purpose
Provide a reliable, transparent exporter from Microsoft OneNote (via Graph) to Markdown/DOCX and JSONL suited for writing workflows and LLM pipelines.

## Short-term goals
- Solid device-code auth and token caching
- Deterministic exports with assets
- Compiled MD + optional DOCX
- JSONL for RAG
- CI: lint/tests

## Long-term goals
- Streamlit/Flask UI
- Per-section compiled outputs and TOC
- Advanced HTML→MD rules
- Retry/backoff and resumability
- RAG helper scripts and vector indexing

## Audience
Writers and researchers using OneNote who want their notes in portable formats, and developers building LLM/RAG workflows.

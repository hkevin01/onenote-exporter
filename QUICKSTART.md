# 🚀 Quick Start - OneNote Exporter

**Requirements**: Docker only! Everything else is included.

## 1. Clone & Setup

```bash
git clone https://github.com/username/onenote-exporter.git
cd onenote-exporter
./setup.sh     # Linux/macOS
# OR
setup.bat      # Windows
```

## 2. Configure Azure App

Edit the `.env` file created by setup:

```bash
TENANT_ID=your-tenant-id-here
CLIENT_ID=your-client-id-here
```

Get these from: [Azure Portal](https://portal.azure.com) → App registrations → New registration

- Permissions needed: `Notes.Read`, `offline_access`

## 3. Export Your Notes

```bash
# List notebooks
docker compose run --rm onenote-exporter --list

# Export a notebook
docker compose run --rm onenote-exporter --notebook "My Notes" --merge
```

## 📁 Outputs

Find your exported notebooks in `./output/` directory:

- Individual page Markdown files
- Downloaded images and attachments
- Merged notebook file (single Markdown)
- Optional DOCX and JSONL formats

---

**Full documentation**: See [README.md](README.md) for detailed instructions, troubleshooting, and advanced usage.

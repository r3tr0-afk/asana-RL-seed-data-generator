# Asana Simulation Data Generator

Generates realistic, enterprise-grade seed data for an Asana simulation database.

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
python src/main.py
```

Output: `output/asana_simulation.sqlite`

**Note: Running `main.py` deletes any existing database in `output/` before generating new data.**

## Requirements

- Python 3.10+
- (Optional) Ollama for LLM-generated content

## Project Structure

- `src/main.py` - Entry point
- `src/generators/` - Data generation logic (users, projects, tasks, etc.)
- `src/scrapers/` - Data templates and sources
- `src/utils/` - Helpers (config, base utilities, LLM integration)
- `src/models/` - LLM model documentation
- `prompts/` - LLM prompt templates
- `schema.sql` - Database DDL
- `docs/` - ER diagram (DBML format)

## Configuration

Edit `.env` or `src/utils/config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SEED` | 42 | Random seed |
| `ENABLE_LLM` | false | Use Ollama for text |
| `OLLAMA_MODEL` | llama3.2:1b | Ollama model |

Volume settings in `config.py`: users (5,000), projects (600), tasks (50,000).

## Data Generation

**Sources**: Asana "Anatomy of Work" Index, US Census demographics, GitHub patterns.

## LLM Content (Optional)

```bash
ollama pull llama3.2:1b
```

Set `ENABLE_LLM=true` in `.env`. Falls back to templates if disabled.

## Database Schema

29 tables: workspaces, users, teams, projects, tasks, stories, attachments, custom_fields, etc.

See `schema.sql` for DDL or `docs/er_diagram.dbml` for ER diagram.

ER-Diagram : https://dbdiagram.io/d/Asana_ERD-695cb2be39fa3db27b345ed8

## Output

| Entity | Count |
|--------|-------|
| Users | 5,000 |
| Projects | 600 |
| Tasks | 50,000 |
| Stories | ~100,000 |

Total: ~470,000 rows

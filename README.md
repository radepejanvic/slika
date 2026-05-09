# slika
Image processing DSL

## Development

### Prerequisites

Install `uv` if you don't have it:

```bash
winget install --id=astral-sh.uv  -e

# or

powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/username/slika.git
cd slika
uv sync
uv pip install -e .
```

### Running

```bash
uv run slika examples/dummy.sl

# or 

.\.venv\Scripts\activate
slika examples/dummy.sl
```

### Running tests

```bash
uv run pytest .\tests
```

### Adding dependencies

```bash
uv add package-name
```

### Project structure

```
slika/
├── src/
│   ├── grammar/        # textX grammar definition
│   ├── engine/         # AST interpreter
│   ├── backends/       # backend implementations
│   └── cli.py          # entry point
├── examples/           # example .sl programs
├── pyproject.toml
└── uv.lock
```

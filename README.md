# slika
Image processing DSL

## VSCode Extension

The extension provides syntax highlighting and LSP support for `.sl` files.

### Requirements

- VSCode 1.75+
- Python virtual environment set up at `.venv/` in the project root (see [Setup](#setup))

### Installation

1. Open VSCode
2. Open the Command Palette (`Ctrl+Shift+P`)
3. Run `Extensions: Install from VSIX...`
4. Select `vscode-extension/slika-lang-1.0.0.vsix`

When you open a `.sl` file the extension automatically starts the Slika language server using the `.venv` Python environment. Make sure `uv sync` has been run before using the extension.

---

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

# slika
Image processing DSL

## VSCode Extension

The extension provides a complete development experience for `.sl` files, including:

- Syntax highlighting
- Code snippets
- Language Server Protocol (LSP) support
- Run Slika programs directly from VSCode
- Backend selection (CPU / GPU / Auto)
- Output image preview


### Requirements

- VSCode 1.75+
- Python virtual environment set up at `.venv/` in the project root (see [Setup](#setup))

### Installation

1. Open VSCode
2. Open the Command Palette (`Ctrl+Shift+P`)
3. Run `Extensions: Install from VSIX...`
4. Select `vscode-extension/slika-lang-1.0.0.vsix`

When you open a `.sl` file the extension automatically starts the Slika language server using the `.venv` Python environment. Make sure `uv sync` has been run before using the extension.

### Editor Features

#### Code snippets

Type one of the following prefixes and press `Tab`:

| Prefix | Description |
|--------|-------------|
| `slika` | Complete Slika program template |
| `load` | Load an image |
| `pipeline` | Pipeline template |
| `apply` | Apply a pipeline |
| `save` | Save an image |
| `resize` | Resize step |
| `crop` | Crop step |
| `gray` | Convert to grayscale |
| `threshold` | Threshold step |
| `canny` | Canny edge detection |
| `erode` | Erode step |
| `dilate` | Dilate step |
| `opening` | Opening operation |
| `closing` | Closing operation |

#### Running programs

Use either:

- the ▶ **Run Slika File** button in the editor toolbar
- `Ctrl+Shift+R`

#### Backend selection

Click the **Slika: CPU/GPU/AUTO** item in the status bar to choose the processing backend used when running programs.

#### Preview output

Click the 👁 **Preview Output Image** button or use the corresponding command to open the image referenced by the `save ... to` statement.

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

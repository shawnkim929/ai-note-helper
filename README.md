# AI Note Helper for LaTeX!

A LaTeX note-taking assistant that provides suggestions, warnings, and AI-powered improvements for your LaTeX notes. Perfect for catching missing details and unclear explanations that you might've missed alongside features such as:

- Automatic Linting for detecting unresolved references, unbalanced environments, vague language, and math delimiter issues
- AI-Powered Suggestions using LLMs to identify and clarify vague or incomplete sections in your notes
- Inline Directives embed LLMs instructions directly in your LaTeX source code as placeholders
- File Watching automatically analyzes your notes when you save, working seamlessly with auto-compiling LaTeX editors
- Safe Editing generates patch files with undo support before making changes

## Install

1. Clone this repository:
```bash
git clone <repository-url>
cd ai-note-helper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up API keys:

### Option 1: OpenAI (Cloud)
```bash
export OPENAI_API_KEY="your-api-key-here"
export AINOTE_PROVIDER="openai"
export AINOTE_MODEL="gpt-4o-mini"  # Optional, defaults to gpt-4o-mini
```

### Option 2: Ollama (Local)
First, install and run [Ollama](https://ollama.ai/), then:
```bash
export AINOTE_PROVIDER="ollama"
export AINOTE_OLLAMA_MODEL="llama3.2"  # Optional, defaults to llama3.2
export AINOTE_OLLAMA_URL="http://localhost:11434"  # Optional
```

### Option 3: Dummy for testing purposes
Set by default

## Usage

### Scans

Run a one-time analysis of your LaTeX file:
```bash
python cli.py scan notes.tex
```

Each run through will:
- Run linting checks
- Generate a `notes.suggestions.md` file with issues found
- Process any AI directives in your file

#### AI-Powered Checks

Enable AI-powered analysis to detect vague or incomplete sections:
```bash
python cli.py scan notes.tex --ai-checks
```

This uses your configured LLM to analyze paragraphs and identify:
- Vague language that needs more detail
- Incomplete sections missing information
- Unjustified claims that need proof

**Note**: This requires a real AI provider (not dummy) and will make API calls.

### Watch Mode (Recommended)

Watch your LaTeX file and automatically analyze on save:
```bash
python cli.py watch notes.tex
```

This works perfectly with auto-compiling LaTeX editors. When you save your file, the assistant will:
1. Wait a moment (debounce) (to avoid conflicts with the LaTeX compiler)
2. Run all checks
3. Generate suggestions
4. Process AI directives if `apply=true` is set

Press `Ctrl+C` to stop watching.

### AI Directives

You can embed AI instructions directly in your LaTeX source code. These act as placeholders that get replaced with AI-generated content.

#### Basic Syntax
```latex
%!ai clarify(apply=true, max_tokens=180): "Explain why uniform continuity fails here in around 80 words."
```

#### Syntax Breakdown
- `%!ai` - Directive marker
- `clarify` - Action verb (can be any name like `clarify`, `expand`, `complete`, etc.)
- `(apply=true, max_tokens=180)` - Optional parameters
  - `apply=true` - Automatically apply the AI-generated content (default: `false`)
  - `max_tokens=180` - Maximum tokens for the response
  - `code=false` - Whether to format as code block (default: `false`)
- `"instruction"` - The prompt for the AI

#### Example Usage

```latex
\section{Uniform Continuity}

We need to show that $f$ is uniformly continuous. 
%!ai clarify(apply=true, max_tokens=150): "Provide a step-by-step proof outline for showing uniform continuity, focusing on the key steps without going into full detail."

The function $f(x) = x^2$ on $[0,1]$ is uniformly continuous.
%!ai expand(apply=false): "Explain why this is true and provide a brief justification."
```

#### Applying Directives

When `apply=false` (default), the directive is detected but not automatically applied. You can:
- Run `scan` with `--apply` flag to apply all directives:
  ```bash
  python cli.py scan notes.tex --apply
  ```
- Or set `apply=true` in the directive itself for automatic application

#### Directives with Generated Blocks

When a directive is applied, it creates a guarded block:
```latex
%!ai-begin id=abc123 verb=clarify
```
[Generated content appears here]
```
%!ai-end id=abc123
```

Future runs will replace the content in these blocks, keeping your directives stable.

### Applying Patches

If you've generated a patch file and want to apply it later:
```bash
python cli.py apply notes.tex.patch notes.tex
```

To undo a change:
```bash
python cli.py apply notes.tex.undo.patch notes.tex
```

## Suggestions

The tool generates a `*.suggestions.md` file with:
- **ref**: Unresolved `\ref{}` references
- **env**: Unbalanced `\begin{}`/`\end{}` environments
- **style**: Vague language detected (e.g., "obvious", "clearly", "trivial")
- **math**: Unbalanced math delimiters

## Workflow Example

1. **Start watching your notes**:
   ```bash
   python cli.py watch lecture-notes.tex
   ```

2. **Write your notes** in your LaTeX editor. When you encounter something vague or need clarification:
   ```latex
   %!ai clarify(apply=true): "Explain the relationship between these two concepts mentioned by the professor."
   ```

3. **Save the file** - the watcher will:
   - Detect the directive
   - Call the AI provider
   - Replace the directive with the generated content
   - Generate suggestions for any issues

4. **Review the suggestions** in `lecture-notes.suggestions.md`

5. **Continue editing** - your LaTeX compiler will recompile, and the cycle continues!

## Configuration

### Environment Variables

- `AINOTE_PROVIDER`: AI provider to use (`openai`, `ollama`, or `dummy`)
- `OPENAI_API_KEY`: Required for OpenAI provider
- `AINOTE_MODEL`: OpenAI model name (default: `gpt-4o-mini`)
- `AINOTE_OLLAMA_URL`: Ollama API URL (default: `http://localhost:11434`)
- `AINOTE_OLLAMA_MODEL`: Ollama model name (default: `llama3.2`)

## Project Structure

```
ai-note-helper/
├── ai/
│   ├── provider.py          # Provider base class and factory
│   ├── openai_provider.py   # OpenAI implementation
│   └── ollama_provider.py   # Ollama implementation
├── latex/
│   ├── parser.py            # Directive parsing
│   ├── checks.py            # Linting checks
│   └── edits.py             # Diff generation and patching
├── suggestions/
│   └── renderer.py          # Markdown suggestion output
├── cli.py                   # Main CLI entrypoint
└── requirements.txt         # Python dependencies
```

## License

See LICENSE file for details.

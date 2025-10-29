from pathlib import Path
from typing import List, Dict, Any



def write_suggestions_md(tex_path: Path, suggestions: List[Dict[str, Any]]) -> Path:
    out = []
    out.append(f"# Suggestions for `{tex_path.name}`\n")

    if not suggestions:
        out.append("No issues found.\n")

    else:

        for s in suggestions:
            out.append(f"- **[{s['kind']}]** line {s['line']}: {s['message']}")

            if s['context']:
                out.append(f"  \n  `{s['context']}`\n")

    p = tex_path.with_suffix(tex_path.suffix + ".suggestions.md")
    p.write_text("\n".join(out), encoding="utf-8")

    return p

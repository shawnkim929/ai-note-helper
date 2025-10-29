import re
from dataclasses import dataclass
from typing import List, Optional

# Example syntax for directives:
# %!ai clarify(apply=true, max_tokens=180): "Explain why uniform continuity fails here in around 80 words."

DIR_RE = re.compile(
        r'^(?P<prefix>\s*%!\s*ai)\s+'
        r'(?P<verb>[a-zA-Z_]+)\s*'
        r'(?:\((?P<kv>[^)]*)\))?\s*:\s*'
        r'\"(?P<instruction>.*?)\"\s*$'
)

KV_RE = re.compile(r'(\w+)\s*=\s*([^\s,]+)')    # flags
BEGIN_RE = re.compile(r'^\s*%!\s*ai-begin\s+id=(?P<id>[a-zA-Z0-9_-]+)\s+verb=(?P<verb>\w+)\s*$')
END_RE = re.compile(r'^\s*%!\s*ai-end\s+id=(?P<id>[a-zA-Z0-9_-]+)\s*$')



@dataclass
class Directive:
    verb: str
    instruction: str
    line_no: int
    apply: bool = False
    max_tokens: Optional[int] = None
    code: bool = False
    id_hint: Optional[str] = None



def _parse_kv(kv: str):
    out = {}

    for m in KV_RE.finditer(kv or ""):
        k, v = m.group(1), m.group(2)

        if v.lower() in ("true", "false"):
            v = v.lower() == "true"

        elif v.isdigit():
            v = int(v)

        out[k] = v

    return out



def find_directives(text: str) -> List[Directive]:
    directives = []

    for i, line in enumerate(text.splitlines()):
        m = DIR_RE.match(line)

        if not m:
            continue

        kv = _parse_kv(m.group("kv"))
        directives.append(Directive(verb=m.group("verb"), instruction=m.group("instruction"), line_no=i + 1, apply=bool(kv.get("apply", False)), max_tokens=kv.get("max_tokens"), code=bool(kv.get("code", False)), id_hint=str(kv.get("id")) if kv.get("id") else None))

    return directives



def replace_generated_blocks(text: str, directive_id: str, new_content: str) -> str:

    """
    Replace existing ai-begin/ai-end block by id. If not present, caller inserts anew.
    """

    lines = text.splitlines()
    start_idx = end_idx = None

    for i, line in enumerate(lines):

        if BEGIN_RE.match(line) and BEGIN_RE.match(line).group("id") == directive_id:
            start_idx = i

        if start_idx is not None and END_RE.match(line) and END_RE.match(line).group("id") == directive_id:
            end_idx = i
            break

    if start_idx is not None and end_idx is not None and end_idx > start_idx:

        # replace inner content

        new_lines = lines[:start_idx+1] + new_content.splitlines() + lines[end_idx:]
        return "\n".join(new_lines) + ("\n" if text.endswith("\n") else "")

    return text

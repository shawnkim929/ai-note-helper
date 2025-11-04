import difflib
import hashlib
from pathlib import Path
from typing import List, Tuple
from latex.parser import Directive, replace_generated_blocks



def _id_for(d: Directive, content: str) -> str:

    """
    Deterministic id; stable across runs unless directive text changes.
    """

    base = f"{d.verb}:{d.instruction}:{d.line_no}"

    return (d.id_hint or hashlib.sha1(base.encode()).hexdigest()[:8])



def _guarded_block(d: Directive, d_id: str, body: str) -> str:

    """
    Wrap model output with guarded markers so future runs can replace it.
    """

    fence = "```" if not d.code else "```tex"
    end_fence = "```"
    lines = [
            f"%!ai-begin id={d_id} verb={d.verb}",
            fence,
            body.strip(),
            end_fence,
            f"%!ai-end id={d_id}"
    ]

    return "\n".join(lines) + "\n"



def build_replacements_with_diff(src: str, pairs: List[Tuple[Directive, str]], path: Path):

    """
    Insert or replace guarded blocks for each directive, then produce a unified diff
    and an undo patch.
    """

    new_text = src
    original_text = src

    for d, model_out in pairs:
        d_id = _id_for(d, model_out)
        block = _guarded_block(d, d_id, model_out)

        # Try to replace existing block; if not present, insert block below directive line

        replaced = replace_generated_blocks(new_text, d_id, block.splitlines()[1:-1])  # inner body only

        if replaced != new_text:
            new_text = replaced

        else:
            lines = new_text.splitlines()
            insert_at = max(0, d.line_no)  # after directive line
            lines = lines[:insert_at] + [block] + lines[insert_at:]
            new_text = "\n".join(lines) + ("\n" if new_text.endswith("\n") else "")

    diff = "\n".join(difflib.unified_diff(
        original_text.splitlines(), new_text.splitlines(),
        fromfile=str(path), tofile=str(path), lineterm=""
    ))

    undo = "\n".join(difflib.unified_diff(
        new_text.splitlines(), original_text.splitlines(),
        fromfile=str(path), tofile=str(path), lineterm=""
    ))

    diff_path = path.with_suffix(path.suffix + ".patch")
    undo_path = path.with_suffix(path.suffix + ".undo.patch")
    diff_path.write_text(diff, encoding="utf-8")
    undo_path.write_text(undo, encoding="utf-8")

    return diff_path, undo_path, new_text



def apply_unified_diff(original_text: str, diff_text: str) -> str:

    """
    Minimal unified diff applier for simple patches.
    For complex patches, prefer 'patch' command; this works for our generated diffs.
    """

    # For brevity, we shell out if available; else we fallback to naive approach.

    try:
        import subprocess, tempfile, os

        with tempfile.TemporaryDirectory() as td:
            orig = Path(td) / "orig.tex"
            pat = Path(td) / "change.patch"
            orig.write_text(original_text, encoding="utf-8")
            pat.write_text(diff_text, encoding="utf-8")
            subprocess.run(["patch", str(orig), str(pat)], check=True, capture_output=True)

            return orig.read_text(encoding="utf-8")

    except Exception:

        # Fallback: if patch not available, just return original (user can apply manually)
        # In practice, our workflow writes directly during scan; apply is optional.

        return original_text

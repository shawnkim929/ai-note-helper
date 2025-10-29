import re
from typing import List, Dict, Any



REF_RE = re.compile(r'\\ref\{([^}]+)\}')
LABEL_RE = re.compile(r'\\label\{([^}]+)\}')
CITE_RE = re.compile(r'\\cite\{([^}]+)\}')
BEGIN_RE = re.compile(r'\\begin\{([^}]+)\}')
END_RE = re.compile(r'\\end\{([^}]+)\}')



def run_checks(text: str) -> List[Dict[str, Any]]:

    """
    LaTeX linter
    Deterministic, fast checks that do not require any AI calls.
    Returns a list of dicts with fields: kind, message, line, context
    """

    suggestions = []
    lines = text.splitlines()

    # Gather labels

    labels = set()

    for ln, line in enumerate(lines, 1):

        for m in LABEL_RE.finditer(line):

            labels.add(m.group(1))

    # Unresolved refs

    for ln, line in enumerate(lines, 1):

        for m in REF_RE.finditer(line):

            tgt = m.group(1)

            if tgt not in labels:

                suggestions.append({
                    "kind": "ref",
                    "message": f"Unresolved \\ref{{{tgt}}}.",
                    "line": ln,
                    "context": line.strip()
                })

    # Naive latex env balance check

    stack = []

    for ln, line in enumerate(lines, 1):

        for m in BEGIN_RE.finditer(line):
            stack.append((m.group(1), ln))

        for m in END_RE.finditer(line):
            env = m.group(1)

            if not stack or stack[-1][0] != env:
                suggestions.append({
                    "kind": "env",
                    "message": f"Mismatched \\end{{{env}}}.",
                    "line": ln,
                    "context": line.strip()
                })

            else:
                stack.pop()

    for env, ln in stack:
        suggestions.append({
            "kind": "env",
            "message": f"Unclosed \\begin{{{env}}} starting at line {ln}.",
            "line": ln,
            "context": ""
        })

    # Suspicious vagueness phrases

    vague = re.compile(r'\b(obvious|clearly|trivial|it can be shown)\b', re.IGNORECASE)

    for ln, line in enumerate(lines, 1):

        if vague.search(line):
            suggestions.append({
                "kind": "style",
                "message": "Vague language detected. Consider adding a justification.",
                "line": ln,
                "context": line.strip()
            })

    # Dangling math delimiter (rough implementation, might need to scrap later)

    if text.count("$") % 2 != 0:
        suggestions.append({
            "kind": "math",
            "message": "Odd number of '$' found; inline math may be unbalanced.",
            "line": 0,
            "context": ""
        })

    return suggestions

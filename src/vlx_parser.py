# simple parser for the VLX format
import re
from typing import Dict, List, Any

def parse_vlx(text: str) -> Dict[str, Any]:
    """Parse a VLX-style text file into a structured dict.

    This parser is intentionally permissive: it extracts a meta block (VLX:...),
    layer definitions (L1, L2, ...), function blocks (function name(...): ...),
    TASK_WINDOW, VLX.PROCESS and VLX.MANTRA blocks where present.
    """
    lines = text.splitlines()
    result: Dict[str, Any] = {
        "meta": {},
        "layers": {},
        "functions": {},
        "task_window": None,
        "process": [],
        "mantra": "",
    }

    # Join into paragraphs separated by blank lines to capture blocks
    paragraphs = []
    cur = []
    for ln in lines:
        if ln.strip() == "":
            if cur:
                paragraphs.append("\n".join(cur))
                cur = []
        else:
            cur.append(ln)
    if cur:
        paragraphs.append("\n".join(cur))

    text_all = text

    # Meta line: starts with VLX: ... (first occurrence)
    m = re.search(r"^VLX:\s*(.*)$", text_all, re.MULTILINE)
    if m:
        meta_line = m.group(1)
        # split by semicolon, then by =
        for part in re.split(r";\s*", meta_line):
            if "=" in part:
                k, v = part.split("=", 1)
                result["meta"][k.strip()] = v.strip()
            else:
                # fallback: keep raw part
                if part.strip():
                    result["meta"].setdefault("misc", []).append(part.strip())

    # Layers like L1:NAME → { ... } or L1:LOGIC_CORE → {...}
    for ln in lines:
        m = re.match(r"^(L\d+):\s*([^→\n]+)→?\s*(.*)$", ln)
        if m:
            lid = m.group(1).strip()
            lname = m.group(2).strip()
            rest = m.group(3).strip()
            result["layers"][lid] = {
                "name": lname,
                "content": rest,
            }

    # Extract function blocks
    func_re = re.compile(r"^function\s+(\w+)\s*\(([^)]*)\):", re.MULTILINE)
    for match in func_re.finditer(text_all):
        fname = match.group(1)
        start = match.start()
        # find the next function or end of text
        next_match = func_re.search(text_all, match.end())
        end = next_match.start() if next_match else len(text_all)
        body = text_all[match.start():end].strip()
        result["functions"][fname] = body

    # TASK_WINDOW block
    m_task = re.search(r"TASK_WINDOW:\s*\n([\s\S]*?)(?:\n[A-Z][A-Z0-9._-]+:|\Z)", text_all)
    if m_task:
        result["task_window"] = m_task.group(1).strip()

    # VLX.PROCESS block: collect lines after VLX.PROCESS:
    m_proc = re.search(r"VLX.PROCESS:\s*\n([\s\S]*?)(?:\n[V][A-ZX].*:|\Z)", text_all)
    if m_proc:
        proc_text = m_proc.group(1).strip()
        # split lines and strip bullets
        proc_lines = [l.strip() for l in proc_text.splitlines() if l.strip()]
        result["process"] = proc_lines

    # VLX.MANTRA (collect following paragraph)
    m_mantra = re.search(r"VLX.MANTRA:\s*\n([\s\S]*?)\n\n", text_all)
    if m_mantra:
        result["mantra"] = m_mantra.group(1).strip()

    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: vlx_parser.py <file>")
        sys.exit(2)
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()
    data = parse_vlx(text)
    import json
    print(json.dumps(data, ensure_ascii=False, indent=2))
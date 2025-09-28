"""
Simple, robust VLX parser using Lark. Outputs a structured Python dict (JSON serializable).

Usage:
  python -m src.vlx_parser_lark <path-to-vlx-file>
"""
from lark import Lark, Transformer, v_args
from typing import Dict, Any
import json
import sys
import re

GRAMMAR = r"""
start: meta_block? block*

meta_block: "VLX:" META_LINE
META_LINE: /.+/ NEWLINE

block: layer_def
     | function_def
     | task_window
     | process_block
     | mantra_block
     | /.+/ NEWLINE

layer_def: LAYER_NAME ":" LAYER_TITLE ARROW? LAYER_CONTENT? NEWLINE
LAYER_NAME: /L\d+/
LAYER_TITLE: /[^→\n\:\{]+/
ARROW: /→|->|=>/
LAYER_CONTENT: /\{[^}]*\}|[^\n]*/

function_def: "function" NAME "(" ARGS? "):" NEWLINE INDENT func_body DEDENT
NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
ARGS: /[^)]*/
func_body: (/(.)*/ NEWLINE)*

task_window: "TASK_WINDOW:" NEWLINE INDENT task_content DEDENT
task_content: (/./ NEWLINE)*

process_block: "VLX.PROCESS:" NEWLINE INDENT process_line+ DEDENT
process_line: /.+/ NEWLINE

mantra_block: "VLX.MANTRA:" NEWLINE mantra_text
mantra_text: /(.|\n)+/

%import common.NEWLINE
%import common.WS
%import common.CNAME
%import common.INDENT
%import common.DEDENT
%ignore WS
"""

@v_args(inline=True)
class VLXTransformer(Transformer):
    def __init__(self):
        self.result = {
            "meta": {},
            "layers": {},
            "functions": {},
            "task_window": None,
            "process": [],
            "mantra": ""
        }

    def META_LINE(self, token):
        line = token.value.strip()
        # parse key=value;... pairs
        parts = re.split(r";\s*", line)
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                self.result["meta"][k.strip()] = v.strip()
            elif p.strip():
                self.result["meta"].setdefault("misc", []).append(p.strip())

    def layer_def(self, name, title, *rest):
        name_s = name.value.strip()
        title_s = title.value.strip()
        content = ""
        if rest:
            # rest may contain ARROW and LAYER_CONTENT or just LAYER_CONTENT
            for item in rest:
                try:
                    s = item.value
                except Exception:
                    s = str(item)
                if s and s.strip():
                    content = s.strip()
        self.result["layers"][name_s] = {"name": title_s, "content": content}

    def function_def(self, *parts):
        # parts: NAME, ARGS?, NEWLINE, INDENT, func_body, DEDENT
        name = parts[0].value
        # fallback: store placeholder for body (Lark reconstruction can be improved later)
        body = "<function body>"
        self.result["functions"][name] = body

    def task_window(self, *parts):
        # reconstruct as plain text
        lines = []
        for p in parts:
            try:
                text = "".join([str(c) for c in p.children])
                lines.append(text)
            except Exception:
                pass
        if lines:
            self.result["task_window"] = "\n".join(lines).strip()
        else:
            self.result["task_window"] = "CONTEXT:....."

    def process_line(self, token):
        text = token.value.rstrip("\n")
        self.result["process"].append(text)

    def mantra_block(self, *parts):
        try:
            text = "".join(p.value if hasattr(p, "value") else str(p) for p in parts)
            self.result["mantra"] = text.strip()
        except Exception:
            self.result["mantra"] = ""


def parse_vlx(text: str) -> Dict[str, Any]:
    parser = Lark(GRAMMAR, parser="lalr", maybe_placeholders=False)
    tree = parser.parse(text)
    transformer = VLXTransformer()
    transformer.transform(tree)
    return transformer.result


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.vlx_parser_lark <file>")
        sys.exit(2)
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()
    data = parse_vlx(text)
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
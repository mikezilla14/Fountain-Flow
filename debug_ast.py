import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from core_parser import parse
from ast_nodes import *

def dump_ast(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    ast = parse(content)
    with open('ast_dump.txt', 'w', encoding='utf-8') as out:
        out.write(f"Parsed {len(ast)} nodes.\\n")
        for i, node in enumerate(ast):
            out.write(f"{i}: {type(node).__name__} - {node}\\n")

if __name__ == "__main__":
    dump_ast('examples/fantasy.fflow')

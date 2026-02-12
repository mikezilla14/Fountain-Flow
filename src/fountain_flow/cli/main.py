import argparse
import sys
import os
from ..parser.fflow import parse as parse_fflow
from ..parser.reverse import TweeParser, RenPyParser
from ..transpiler.formats import TweeTranspiler, RenPyTranspiler, FFlowTranspiler

def main():
    parser = argparse.ArgumentParser(description="Fountain-Flow Compiler/Transpiler")
    parser.add_argument("input_file", help="Input file path (.fflow, .twee, .rpy)")
    parser.add_argument("--to", choices=["twee", "renpy", "fflow"], help="Output format")
    parser.add_argument("--out", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    input_path = args.input_file
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)
        
    ext = os.path.splitext(input_path)[1].lower()
    
    # 1. Parse Input
    ast = None
    input_format = None
    
    if ext == ".fflow":
        input_format = "fflow"
        with open(input_path, "r", encoding="utf-8") as f:
            ast = parse_fflow(f.read())
    elif ext in [".twee", ".tw"]:
        input_format = "twee"
        with open(input_path, "r", encoding="utf-8") as f:
            ast = TweeParser().parse(f.read())
    elif ext == ".rpy":
        input_format = "renpy"
        with open(input_path, "r", encoding="utf-8") as f:
            ast = RenPyParser().parse(f.read())
    else:
        print(f"Error: Unknown input format '{ext}'. Supported: .fflow, .twee, .rpy")
        sys.exit(1)
        
    print(f"Parsed {len(ast)} nodes from {input_format} source.")

    # 2. Determine Output Format
    target_format = args.to
    if not target_format:
        # Default behavior:
        # fflow -> renpy (arbitrary default, or maybe error?)
        # twee/renpy -> fflow
        if input_format == "fflow":
            print("Please specify --to [twee|renpy]")
            sys.exit(1)
        else:
            target_format = "fflow"
    
    # 3. Transpile
    transpiler = None
    if target_format == "twee":
        transpiler = TweeTranspiler()
    elif target_format == "renpy":
        transpiler = RenPyTranspiler()
    elif target_format == "fflow":
        transpiler = FFlowTranspiler()
        
    output_text = transpiler.transpile(ast)
    
    # 4. Output
    if args.out:
        out_path = args.out
    else:
        # Default: output/<filename>.<ext>
        os.makedirs("output", exist_ok=True)
        filename = os.path.splitext(os.path.basename(input_path))[0]
        ext_map = {"twee": ".twee", "renpy": ".rpy", "fflow": ".fflow"}
        out_ext = ext_map.get(target_format, ".txt")
        out_path = os.path.join("output", f"{filename}{out_ext}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output_text)
    print(f"Written to {out_path}")
    
    # 5. Verification
    # User requested: "Ensure fidelity... full error log should be written"
    # We perform a roundtrip check:
    # Source -> Target -> Roundtrip -> Roundtrip AST
    # Compare Source AST vs Roundtrip AST
    
    # Only applicable if we have a reverse parser/transpiler combo
    can_verify = False
    
    if (input_format == "fflow" and target_format == "twee") or \
       (input_format == "twee" and target_format == "fflow"):
        can_verify = True
         
    if can_verify:
        print("Verifying fidelity...")
        try:
            roundtrip_ast = []
            
            # Full Roundtrip Check
            if input_format == "fflow" and target_format == "twee":
                # 1. We have Source AST (ast) and Output Twee (output_text)
                # 2. Parse Twee -> Intermediate AST
                twee_ast = TweeParser().parse(output_text)
                # 3. Transpile Intermediate AST -> Roundtrip FFlow
                fflow_transpiler = FFlowTranspiler()
                roundtrip_fflow = fflow_transpiler.transpile(twee_ast)
                # 4. Parse Roundtrip FFlow -> Final AST
                roundtrip_ast = parse_fflow(roundtrip_fflow)
                
            elif input_format == "twee" and target_format == "fflow":
                # 1. We have Source AST (ast) and Output FFlow (output_text)
                # 2. Parse FFlow -> Intermediate AST
                intermediate_ast = parse_fflow(output_text)
                # 3. Transpile Intermediate AST -> Roundtrip Twee
                twee_transpiler = TweeTranspiler()
                roundtrip_twee = twee_transpiler.transpile(intermediate_ast)
                # 4. Parse Roundtrip Twee -> Final AST
                roundtrip_ast = TweeParser().parse(roundtrip_twee)
                
            else:
                 # Fallback
                 print(f"Warning: Full roundtrip verification not implemented for {input_format} -> {target_format}")
                 roundtrip_ast = []

            # Compare Source AST vs Roundtrip AST
            errors = compare_asts(ast, roundtrip_ast)
            
            if not errors:
                print("Fidelity Check: PASSED")
            else:
                print(f"Fidelity Check: FAILED with {len(errors)} errors.")
                with open("fidelity_error.log", "w", encoding="utf-8") as log:
                    log.write(f"Roundtrip fidelity check failed for {input_path} -> {target_format} -> {input_format}\n")
                    log.write("\n".join(errors))
                print("See fidelity_error.log for details.")
                
        except Exception as e:
            print(f"Verification crashed: {e}")
            import traceback
            traceback.print_exc()

def compare_asts(ast1, ast2) -> list[str]:
    errors = []
    if len(ast1) != len(ast2):
        errors.append(f"Node count mismatch: Original {len(ast1)} vs Roundtrip {len(ast2)}")
        min_len = min(len(ast1), len(ast2))
    else:
        min_len = len(ast1)
        
    for i in range(min_len):
        n1 = ast1[i]
        n2 = ast2[i]
        
        if type(n1) != type(n2):
            errors.append(f"Node {i} type mismatch: {type(n1).__name__} vs {type(n2).__name__}")
            continue
            
        d1 = n1.__dict__
        d2 = n2.__dict__
        
        for k, v in d1.items():
            if k == "depth": continue 
            
            if k not in d2:
                errors.append(f"Node {i} ({type(n1).__name__}) missing field {k} in roundtrip.")
                continue
            
            val2 = d2[k]
            
            v_str = str(v).strip()
            val2_str = str(val2).strip()
            
            if v_str != val2_str:
                 errors.append(f"Node {i} field '{k}' mismatch: '{v}' vs '{val2}'")
                 
    return errors

if __name__ == "__main__":
    main()

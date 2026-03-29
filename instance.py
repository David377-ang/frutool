import argparse
import os
import sys
from filepathProc import get_executable_path
from binProc import process_batch_tasks, generate_report
from binshowProc import show_fru_content

G_config_file = "FruConfig.ini"
G_bin_output = "FRU_table.txt"
G_result_txt = "result.txt"

def main():
    parser = argparse.ArgumentParser(
        prog="NLfrutool",
        description="Strict BIN/FRU Manipulation Tool (Production Ready).",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run", action="store_true", help="Execute strictly according to FruConfig.ini")
    group.add_argument("--show", action="store_true", help="Display FRU TLV structure (Requires --dev)")
    group.add_argument("--info", action="store_true", help="Display tool information")
    group.add_argument("--version", action="store_true", help="Display tool version")

    parser.add_argument("--dev", metavar="FILE", help="Target BIN file for --show")
    args = parser.parse_args()

    executable_dir = get_executable_path()

    if args.info:
        print("NLfrutool v0.2 | Corporation: WYMTN | Author: David JH Lin")
        sys.exit(0)

    if args.version:
        print("NLfrutool version 0.2")
        sys.exit(0)

    if args.run:
        print(f"🚀 [Mode: RUN] Target Dir: {executable_dir}")
        ini_path = os.path.join(executable_dir, G_config_file)
        result_path = os.path.join(executable_dir, G_result_txt)
        
        # 1. 執行核心邏輯：回傳 (產出路徑, 訊息清單)
        target_bin_path, messages = process_batch_tasks(ini_path, executable_dir)
        
        if target_bin_path:
            # --- 成功流程 (輸出 0) ---
            report_out = os.path.join(executable_dir, G_bin_output)
            generate_report(target_bin_path, report_out)
            
            with open(result_path, "w", encoding="utf-8") as rf:
                rf.write("0\n")
                rf.write("SUCCESS: Modification completed.\n")
                for msg in messages:
                    rf.write(f"- {msg}\n")
                rf.write(f"Generated File: {os.path.basename(target_bin_path)}")

            print(f"✨ Success! Result code 0 saved to {G_result_txt}")
            sys.exit(0)
        else:
            # --- 失敗流程 (輸出 1) ---
            with open(result_path, "w", encoding="utf-8") as rf:
                rf.write("1\n")
                rf.write("FAILURE_REASON:\n")
                for msg in messages:
                    rf.write(f"- {msg}\n")

            print(f"❌ Failed! Result code 1 saved to {G_result_txt}")
            sys.exit(1)

    if args.show:
        if not args.dev:
            print("❌ Error: --show requires --dev <file>")
            sys.exit(1)
        target_path = os.path.join(executable_dir, args.dev)
        show_fru_content(target_path)
        sys.exit(0)

if __name__ == "__main__":
    main()

def test_debug():

    show_fru_content(r"C:/frutool/Netlake2-Golden-FBOSS-v6_20251107.bin")

    return None

if __name__ == "__main__":
    main()
    #test_debug()


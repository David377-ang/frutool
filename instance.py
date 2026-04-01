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

    # 將 --detail 加入互斥群組，確保一次只執行一個功能
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run", action="store_true", help="Execute strictly according to FruConfig.ini")
    group.add_argument("--show", action="store_true", help="Display FRU TLV structure (Requires --dev)")
    group.add_argument("--info", action="store_true", help="Display tool information")
    group.add_argument("--version", action="store_true", help="Display tool version")
    group.add_argument("--detail", action="store_true", help="Display available command examples") # 新增此行

    parser.add_argument("--dev", metavar="FILE", help="Target BIN file for --show")
    args = parser.parse_args()

    executable_dir = get_executable_path()

    # --- 1. 處理 --detail (新增) ---
    if args.detail:
        print("\n[ NLfrutool Available Commands ]")
        print("-" * 50)
        print("NLfrutool.exe --run              : Execute batch tasks from ini")
        print("NLfrutool.exe --dev <file> --show: (Dev Mode) Show file details")
        print("NLfrutool.exe --info             : Show tool configuration info")
        print("NLfrutool.exe --version          : Show current version (v0.3)")
        print("-" * 50 + "\n")
        sys.exit(0)

    # --- 2. 處理 --info ---
    if args.info:
        print("NLfrutool v0.4 | Corporation: WYMTN | Author: David JH Lin")
        sys.exit(0)

    # --- 3. 處理 --version ---
    if args.version:
        print("NLfrutool version 0.4")
        sys.exit(0)

    # --- 4. 處理 --run ---
    if args.run:
        print(f"🚀 [Mode: RUN] Target Dir: {executable_dir}")
        ini_path = os.path.join(executable_dir, G_config_file)
        result_path = os.path.join(executable_dir, G_result_txt)
        
        target_bin_path, messages = process_batch_tasks(ini_path, executable_dir)
        
        if target_bin_path:
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
            with open(result_path, "w", encoding="utf-8") as rf:
                rf.write("1\n")
                rf.write("FAILURE_REASON:\n")
                for msg in messages:
                    rf.write(f"- {msg}\n")

            print(f"❌ Failed! Result code 1 saved to {G_result_txt}")
            sys.exit(1)

    # --- 5. 處理 --show ---
    if args.show:
        if not args.dev:
            print("❌ Error: --show requires --dev <file>")
            sys.exit(1)
        target_path = os.path.join(executable_dir, args.dev)
        show_fru_content(target_path)
        sys.exit(0)

if __name__ == "__main__":
    main()
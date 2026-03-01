import argparse
import os
import sys

from filepathProc import get_executable_path
from binProc import process_batch_tasks
from binProc import generate_report
from binProc import standalone_crc_update
from binshowProc import show_fru_content

G_bin_output = "FRU_table.txt"
G_bin_src = "your_eeprom_data.bin"
G_config_file = "FruConfig.ini"

def main():

    # 建立解析器
    parser = argparse.ArgumentParser(
        prog="NLfrutool",
        description="ETE tool for FBOSS BIN/FRU manipulation.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 主功能選項 (互斥群組：必須且只能選一個)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run", action="store_true", help="Execute BIN modification (Read FruConfig.ini)")
    group.add_argument("--show", action="store_true", help="Read and display FRU TLV structure (Requires --dev)")
    group.add_argument("--info", action="store_true", help="Display tool and author information")
    group.add_argument("--version", action="store_true", help="Display current tool version")

    # 2. 檔案指定參數 (用於 --show 或手動模式)
    parser.add_argument("--dev", metavar="FILE", help="Specify the target BIN file")
    args = parser.parse_args()

    executable_dir = get_executable_path()
    print(f"執行檔所在目錄: {executable_dir}")

    # --- 功能分派 ---
    if args.info:
        print("NLfrutool v0.1 | Corporation: WYMTN | Author: David JH Lin")
        sys.exit(0)

    if args.version:
        print("NLfrutool version 0.1")
        sys.exit(0)

    if args.run:
        print("🚀 [Mode: RUN] Starting batch modification from FruConfig.ini...")   

        process_batch_tasks(os.path.join(executable_dir, G_config_file))
        generate_report(os.path.join(executable_dir, G_bin_src), os.path.join(executable_dir, G_bin_output))
        standalone_crc_update(os.path.join(executable_dir, G_config_file))

        sys.exit(0)

    if args.show:
        if not args.dev:
            print("❌ Error: --show requires a target file. Use: NLfrutool.exe --dev <file> --show")
            sys.exit(1)
        
        # --- 結合點：處理檔案路徑 ---
        # 使用 os.path.join 結合執行目錄與使用者輸入的檔名
        # 如果 args.dev 本身是絕對路徑，join 會自動處理
        target_path = os.path.join(executable_dir, args.dev)

        if not os.path.exists(target_path):
            print(f"❌ Error: Cannot find file at '{target_path}'")
            sys.exit(1)

        print(f"🔍 [Mode: SHOW] Target directory: {executable_dir}")
        print(f"🔍 [Mode: SHOW] Reading structure from: {os.path.basename(target_path)}")
        
        # 執行解析
        show_fru_content(target_path)
        sys.exit(0)


    return None

def test_debug():

    show_fru_content(r"C:/frutool/Netlake2-Golden-FBOSS-v6_20251107.bin")

    return None

if __name__ == "__main__":
    main()
    #test_debug()


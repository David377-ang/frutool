import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="NLfrutool",
        description="A flexible tool for handling and modifying BIN/FRU files."
    )

    # 主功能選項 (互斥群組)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dev", help="Select a specific BIN file to read/modify")
    group.add_argument("--info", action="store_true", help="Print tool information")
    group.add_argument("--version", action="store_true", help="Print tool version")
    group.add_argument("--show", action="store_true", help="Print FRU content on screen")

    # 修改相關引數
    parser.add_argument("--index", type=int, help="Target index to modify")
    parser.add_argument("--PAR", help="String to write into the target index")

    args = parser.parse_args()

    # 功能分派
    if args.info:
        print("NLfrutool v0.1")
        print("Corporation: WYMTN")
        print("Author: David JH Lin")
        print("Email: David_JH_Lin@wiwynn.com")
        print("Description: Tool for BIN/FRU manipulation.")
        sys.exit(0)

    if args.version:
        print("NLfrutool version 0.1")
        sys.exit(0)

    if args.show:
        print("Showing FRU content... (future implementation)")
        sys.exit(0)

    if args.dev:
        # 檔案存在性檢查
        if not os.path.exists(args.dev):
            print(f"[ERROR] File '{args.dev}' not found in current directory.")
            sys.exit(1)

        print(f"[INFO] Selected BIN file: {args.dev}")
        if args.index is not None and args.PAR is not None:
            print(f"[ACTION] Modify index {args.index} with value '{args.PAR}'")
            # TODO: implement BIN modification logic here
        else:
            print("[ACTION] Reading BIN file... (future implementation)")


if __name__ == "__main__":
    main()


import argparse
import os
import sys

from filepathProc import get_executable_path
from filepathProc import create_or_replace_file
from binProc import read_eeprom_bin
from binProc import export_bin_to_txt

G_bin_output = "FRU_table.txt"
G_bin_src = "your_eeprom_data.bin"

def main():

    executable_dir = get_executable_path()
    print(f"執行檔所在目錄: {executable_dir}")

    create_or_replace_file(os.path.join(executable_dir, G_bin_output))

    # read_eeprom_bin(os.path.join(executable_dir, "your_eeprom_data.bin"))

    export_bin_to_txt(os.path.join(executable_dir, G_bin_src), os.path.join(executable_dir, G_bin_output))


    return None

if __name__ == "__main__":
    main()


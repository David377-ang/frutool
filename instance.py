import argparse
import os
import sys

from filepathProc import get_executable_path
from filepathProc import create_or_replace_file
from binProc import read_eeprom_bin
from binProc import export_bin_to_txt
from binProc import export_full_hex_to_txt
from binProc import modify_with_space_padding
from binProc import process_batch_tasks
from binProc import generate_report
from binProc import standalone_crc_update

G_bin_output = "FRU_table.txt"
G_bin_src = "your_eeprom_data.bin"
G_config_file = "FruConfig.ini"

def main():

    executable_dir = get_executable_path()
    print(f"執行檔所在目錄: {executable_dir}")

    # create_or_replace_file(os.path.join(executable_dir, G_bin_output))

    # read_eeprom_bin(os.path.join(executable_dir, "your_eeprom_data.bin"))

    # export_bin_to_txt(os.path.join(executable_dir, G_bin_src), os.path.join(executable_dir, G_bin_output))
    # export_full_hex_to_txt(os.path.join(executable_dir, G_bin_src), os.path.join(executable_dir, G_bin_output))

    # --- 實戰範例 ---
    # 假設我們要寫入型號，且該區段固定長度為 12 bytes
    # 寫入 "MODEL-A"，後面的 5 個位元組會被填為 0x20
    # modify_with_space_padding(
    #     file_path=os.path.join(executable_dir, G_bin_src), 
    #     offset=0x10, 
    #     data="MODEL-A", 
    #     max_length=12, 
    #     report_path="eeprom_space_report.txt"
    # )


    #  --- official release ---    
    process_batch_tasks(os.path.join(executable_dir, G_config_file))
    generate_report(os.path.join(executable_dir, G_bin_src), os.path.join(executable_dir, G_bin_output))
    standalone_crc_update(os.path.join(executable_dir, G_config_file))


    return None

if __name__ == "__main__":
    main()


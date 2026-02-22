import os

def separator(char="-", length=100):
    return char * length

def read_eeprom_bin(file_path, bytes_per_line=16):
    """
    讀取 EEPROM 的 .bin 檔案並以格式化的十六進位顯示。
    
    :param file_path: .bin 檔案路徑
    :param bytes_per_line: 每行顯示幾個位元組 (通常為 16)
    """
    if not os.path.exists(file_path):
        print(f"錯誤：找不到檔案 {file_path}")
        return

    file_size = os.path.getsize(file_path)
    print(f"檔案大小: {file_size} Bytes")
    print(separator("-",60))
    print("Offset (h)  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F")
    print(separator("-",60))

    with open(file_path, "rb") as f:
        address = 0
        while True:
            chunk = f.read(bytes_per_line)
            if not chunk:
                break
            
            # 將位元組轉換為十六進位字串
            hex_data = " ".join(f"{b:02X}" for b in chunk)
            
            # 格式化輸出：位址 (8位數十六進位) + 資料
            print(f"{address:08X}: {hex_data}")
            
            address += bytes_per_line


import os

def export_bin_to_txt(bin_path, txt_path, bytes_per_line=16):
    """
    讀取 .bin 檔案並將格式化後的十六進位內容存入 .txt 檔案。
    """
    if not os.path.exists(bin_path):
        print(f"錯誤：找不到來源檔案 {bin_path}")
        return

    try:
        with open(bin_path, "rb") as f_bin, open(txt_path, "w", encoding="utf-8") as f_txt:
            # 寫入標題
            f_txt.write(f"檔案來源: {bin_path}\n")
            f_txt.write(f"檔案大小: {os.path.getsize(bin_path)} Bytes\n")
            f_txt.write("-" * 60 + "\n")
            f_txt.write("Offset(h) 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F\n")
            f_txt.write("-" * 60 + "\n")

            address = 0
            while True:
                chunk = f_bin.read(bytes_per_line)
                if not chunk:
                    break
                
                # 轉換為十六進位字串
                hex_data = " ".join(f"{b:02X}" for b in chunk)
                
                # 寫入每一行資料
                line = f"{address:08X}: {hex_data}\n"
                f_txt.write(line)
                
                address += bytes_per_line
        
        print(f"成功！已將內容輸出至：{txt_path}")

    except Exception as e:
        print(f"發生錯誤: {e}")



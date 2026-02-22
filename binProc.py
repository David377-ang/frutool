import os
import shutil

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


def export_full_hex_to_txt(bin_path, txt_path, bytes_per_line=16):
    """
    讀取 .bin 並輸出包含 Address | Hex | ASCII 的格式到文字檔。
    """
    if not os.path.exists(bin_path):
        print(f"錯誤：找不到來源檔案 {bin_path}")
        return

    try:
        with open(bin_path, "rb") as f_bin, open(txt_path, "w", encoding="utf-8") as f_txt:
            # 寫入檔案資訊標頭
            f_txt.write(f"EEPROM 數據導出報告\n")
            f_txt.write(f"來源檔案: {os.path.abspath(bin_path)}\n")
            f_txt.write(f"檔案大小: {os.path.getsize(bin_path)} Bytes\n")
            f_txt.write("-" * 75 + "\n")
            f_txt.write("Offset(h) 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  |  ASCII\n")
            f_txt.write("-" * 75 + "\n")

            address = 0
            while True:
                chunk = f_bin.read(bytes_per_line)
                if not chunk:
                    break
                
                # 1. 處理十六進位部分
                hex_data = " ".join(f"{b:02X}" for b in chunk)
                # 如果最後一行不滿 16 bytes，補齊空格以對齊 ASCII 欄位
                if len(chunk) < bytes_per_line:
                    hex_data = hex_data.ljust(bytes_per_line * 3 - 1)
                
                # 2. 處理 ASCII 部分 (可讀字元)
                # 只有 32 到 126 之間的字元是可顯示的，其餘用 '.' 代替
                ascii_chars = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                
                # 3. 組合並寫入
                line = f"{address:08X}: {hex_data}  |  {ascii_chars}\n"
                f_txt.write(line)
                
                address += bytes_per_line
        
        print(f"匯出完成！請查看：{txt_path}")

    except Exception as e:
        print(f"發生錯誤: {e}")






    """修改並自動產出報告的整合函式"""
    if not os.path.exists(file_path):
        print("錯誤：找不到檔案")
        return

    # 1. 準備資料
    payload = data.encode('ascii') if isinstance(data, str) else bytes(data)
    
    # 2. 長度檢查
    if len(payload) > max_length:
        print(f"❌ 錯誤：寫入長度 ({len(payload)}) 超過限制 ({max_length})！")
        return

    # 3. 自動備份
    shutil.copy2(file_path, file_path + ".bak")

    # 4. 寫入資料 (使用 0x00 補齊剩餘空間)
    try:
        final_payload = payload + b'\x00' * (max_length - len(payload))
        with open(file_path, "r+b") as f:
            f.seek(offset)
            f.write(final_payload)
        print(f"✅ 寫入完成！位址: {offset:08X}")
        
        # 5. 自動產生報告
        generate_report(file_path, report_path)
        
    except Exception as e:
        print(f"🔥 修改失敗: {e}")


def generate_report(bin_path, txt_path, bytes_per_line=16):
    """(內部功能) 產出報告，方便即時核對修改結果"""
    try:
        with open(bin_path, "rb") as f_bin, open(txt_path, "w", encoding="utf-8") as f_txt:
            f_txt.write(f"--- EEPROM 自動更新報告 ---\n")
            f_txt.write(f"來源檔案: {bin_path}\n")
            f_txt.write("-" * 75 + "\n")
            
            address = 0
            while True:
                chunk = f_bin.read(bytes_per_line)
                if not chunk: break
                
                # 格式化 Hex 資料
                hex_data = " ".join(f"{b:02X}" for b in chunk).ljust(bytes_per_line * 3 - 1)
                # 格式化 ASCII 資料
                ascii_chars = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                
                f_txt.write(f"{address:08X}: {hex_data}  |  {ascii_chars}\n")
                address += bytes_per_line
        print(f"📄 報告已更新: {txt_path}")
    except Exception as e:
        print(f"產出報告時發生錯誤: {e}")


def modify_with_space_padding(file_path, offset, data, max_length, report_path="report.txt"):
    """
    修改 .bin 檔案，若資料不足則以 0x20 (Space) 填滿。
    """
    if not os.path.exists(file_path):
        print("錯誤：找不到檔案")
        return

    # 1. 處理資料與長度檢查
    payload = data.encode('ascii') if isinstance(data, str) else bytes(data)
    
    if len(payload) > max_length:
        print(f"❌ 錯誤：寫入長度 ({len(payload)}) 超出限制 ({max_length})！")
        return

    # 2. 自動備份
    shutil.copy2(file_path, file_path + ".bak")

    # 3. 執行寫入，剩餘空間填入 0x20 (ASCII Space)
    try:
        # 使用 b'\x20' 進行重複填充
        final_payload = payload + b'\x20' * (max_length - len(payload))
        
        with open(file_path, "r+b") as f:
            f.seek(offset)
            f.write(final_payload)
            
        print(f"✅ 寫入完成！位址: {offset:08X}, 使用 0x20 填滿至 {max_length} Bytes。")
        
        # 4. 自動產生報告
        generate_report(file_path, report_path)
        
    except Exception as e:
        print(f"🔥 修改失敗: {e}")
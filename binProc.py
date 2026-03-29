import configparser
import os
import string

def has_invalid_chars(s):
    """稽核：只允許標準可列印 ASCII (0x20 - 0x7E)"""
    allowed = set(string.digits + string.ascii_letters + string.punctuation + ' ')
    for char in s:
        if char not in allowed:
            return True, char
    return False, None

def calculate_crc16_aug(data: bytes):
    """CRC16-CCITT-AUG: Poly 0x1021, Init 0x1D0F"""
    crc = 0x1D0F
    poly = 0x1021
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def process_batch_tasks(config_file, executable_dir):
    config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
    if not os.path.exists(config_file):
        return None, [f"Config file '{os.path.basename(config_file)}' not found."]

    config.read(config_file, encoding='utf-8')
    process_log = []

    try:
        # --- A. 讀取配置 ---
        if not config.has_section('GOLDEN_BIN'):
            raise ValueError("Missing [GOLDEN_BIN] section in ini.")
            
        src_name = config.get('GOLDEN_BIN', 'source_bin').strip()
        dst_name = config.get('GOLDEN_BIN', 'target_bin').strip()
        
        if not src_name or not dst_name:
            raise ValueError("source_bin or target_bin cannot be empty.")

        src_path = os.path.join(executable_dir, src_name)
        dst_path = os.path.join(executable_dir, dst_name)

        # ==========================================================
        # 新增功能：優先刪除舊的 Target Bin，確保結果唯一性
        # ==========================================================
        if os.path.exists(dst_path):
            try:
                os.remove(dst_path)
                process_log.append(f"Clean up: Old '{dst_name}' removed.")
            except Exception as e:
                # 萬一檔案被其他程式占用(例如開啟中)，這裡會攔截並報錯
                raise IOError(f"Cannot delete existing '{dst_name}': {str(e)}")
        # ==========================================================


        if not os.path.exists(src_path):
            raise FileNotFoundError(f"Source file not found: {src_name}")

        with open(src_path, "rb") as f:
            mem_data = bytearray(f.read())
        process_log.append(f"Loaded source: {src_name}")

        # --- B. 項目校驗與修改 (Item Sections) ---
        for section in config.sections():
            if section in ['GOLDEN_BIN', 'CRC_SETTING']:
                continue
            
            # 檢查項目欄位是否完整且非空
            for key in ['offset', 'max_length', 'source_txt']:
                if not config.has_option(section, key) or not config.get(section, key).strip():
                    raise ValueError(f"Section [{section}]: '{key}' is empty or missing in ini.")

            off = int(config.get(section, 'offset'), 16)
            exp_len = config.getint(section, 'max_length')
            txt_name = config.get(section, 'source_txt').strip()
            txt_path = os.path.join(executable_dir, txt_name)

            if not os.path.exists(txt_path):
                raise FileNotFoundError(f"[{section}] source_txt file missing: {txt_name}")

            with open(txt_path, 'r', encoding='utf-8') as tf:
                content = tf.read().strip('\n\r')
            
            if not content:
                raise ValueError(f"[{section}] source_txt '{txt_name}' is EMPTY.")

            invalid, char = has_invalid_chars(content)
            if invalid:
                raise ValueError(f"[{section}] Invalid char '{char}' ({hex(ord(char))}) in '{txt_name}'.")

            payload = content.encode('ascii')
            if len(payload) != exp_len:
                raise ValueError(f"[{section}] Length Mismatch! Expected {exp_len}, got {len(payload)} in '{txt_name}'.")

            mem_data[off : off + exp_len] = payload
            process_log.append(f"Modify [{section}]: PASS")

        # --- C. CRC 更新 (CRC_SETTING Section) ---
        if config.has_section('CRC_SETTING'):
            # 新增：針對 CRC 欄位的空值預檢
            for k in ['crc_start', 'crc_end', 'crc_address']:
                if not config.has_option('CRC_SETTING', k) or not config.get('CRC_SETTING', k).strip():
                    raise ValueError(f"Section [CRC_SETTING]: '{k}' is empty or missing in ini.")

            c_start = int(config.get('CRC_SETTING', 'crc_start'), 16)
            c_end = int(config.get('CRC_SETTING', 'crc_end'), 16)
            c_addr = int(config.get('CRC_SETTING', 'crc_address'), 16)

            # 確保地址範圍不會溢出
            if c_end + 1 > len(mem_data) or c_addr + 2 > len(mem_data):
                raise ValueError("CRC address range is out of file bounds.")

            new_crc = calculate_crc16_aug(mem_data[c_start : c_end + 1])
            mem_data[c_addr : c_addr + 2] = new_crc.to_bytes(2, 'big')
            process_log.append(f"CRC Update: PASS (Value: 0x{new_crc:04X})")

        # --- D. 寫入 Target Bin ---
        with open(dst_path, "wb") as f:
            f.write(mem_data)
        
        process_log.append(f"Successfully saved to: {dst_name}")
        return dst_path, process_log

    except Exception as e:
        return None, [str(e)]

def generate_report(bin_path, report_path):
    """產出視覺化報告"""
    try:
        with open(bin_path, "rb") as b, open(report_path, "w", encoding="utf-8") as r:
            r.write(f"--- FRU Update Report ---\nTarget: {os.path.basename(bin_path)}\n\n")
            r.write("Offset(h) 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  |  ASCII\n")
            r.write("-" * 75 + "\n")
            addr = 0
            while True:
                chunk = b.read(16)
                if not chunk: break
                hex_str = " ".join(f"{x:02X}" for x in chunk).ljust(47)
                asc_str = "".join(chr(x) if 32 <= x <= 126 else "." for x in chunk)
                r.write(f"{addr:08X}: {hex_str}  |  {asc_str}\n")
                addr += 16
    except Exception as e:
        print(f"Report Generation Error: {e}")
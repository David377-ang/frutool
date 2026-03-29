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

        if not os.path.exists(src_path):
            raise FileNotFoundError(f"Source file not found: {src_name}")

        with open(src_path, "rb") as f:
            mem_data = bytearray(f.read())
        process_log.append(f"Loaded source: {src_name}")

        # --- B. 嚴格項目校驗與修改 ---
        for section in config.sections():
            if section in ['GOLDEN_BIN', 'CRC_SETTING']:
                continue
            
            # 1. 檢查 ini 欄位是否存在且非空白
            for key in ['offset', 'max_length', 'source_txt']:
                if not config.has_option(section, key) or not config.get(section, key).strip():
                    raise ValueError(f"Section [{section}]: '{key}' is empty or missing in ini.")

            off = int(config.get(section, 'offset'), 16)
            exp_len = config.getint(section, 'max_length')
            txt_name = config.get(section, 'source_txt').strip()
            txt_path = os.path.join(executable_dir, txt_name)

            # 2. 文字檔內容校驗
            if not os.path.exists(txt_path):
                raise FileNotFoundError(f"[{section}] source_txt file missing: {txt_name}")

            with open(txt_path, 'r', encoding='utf-8') as tf:
                content = tf.read().strip('\n\r')
            
            if not content:
                raise ValueError(f"[{section}] source_txt '{txt_name}' is EMPTY.")

            # 3. 不可見字元稽核
            invalid, char = has_invalid_chars(content)
            if invalid:
                raise ValueError(f"[{section}] Invalid char '{char}' ({hex(ord(char))}) in '{txt_name}'.")

            # 4. 嚴格長度匹配攔截 (不補 0x20)
            payload = content.encode('ascii')
            if len(payload) != exp_len:
                raise ValueError(f"[{section}] Length Mismatch! Expected {exp_len}, got {len(payload)} in '{txt_name}'.")

            mem_data[off : off + exp_len] = payload
            process_log.append(f"Modify [{section}]: PASS")

        # --- C. CRC 更新 ---
        if config.has_section('CRC_SETTING'):
            c_start = int(config.get('CRC_SETTING', 'crc_start'), 16)
            c_end = int(config.get('CRC_SETTING', 'crc_end'), 16)
            c_addr = int(config.get('CRC_SETTING', 'crc_address'), 16)

            new_crc = calculate_crc16_aug(mem_data[c_start : c_end + 1])
            mem_data[c_addr : c_addr + 2] = new_crc.to_bytes(2, 'big')
            process_log.append(f"CRC Update: PASS (Value: 0x{new_crc:04X})")

        # --- D. 寫入 Target Bin ---
        with open(dst_path, "wb") as f:
            f.write(mem_data)
        
        process_log.append(f"Successfully saved to: {dst_name}")
        return dst_path, process_log

    except Exception as e:
        # 回傳 None 代表失敗，以及錯誤訊息
        return None, [str(e), "ABORT: No output was generated."]

def generate_report(bin_path, report_path):
    """根據產出的 target_bin 生成最終核對表"""
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
        print(f"Report Error: {e}")
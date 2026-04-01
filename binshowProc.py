import os

# 根據圖片建立 Tag 對照表
FRU_MAPPING = {
    1: "Product Name",
    2: "Product Part Number",
    3: "System Assembly Part Number",
    4: "Meta PCBA Part Number",
    5: "Meta PCB Part Number",
    6: "ODM/JDM PCBA Part Number",
    7: "ODM/JDM PCBA Serial Number",
    8: "Product Production State",
    9: "Product Version",
    10: "Product Sub-Version",
    11: "Product Serial Number",
    12: "System Manufacturer",
    13: "System Manufacturing Date",
    14: "PCB Manufacturer",
    15: "Assembled At",
    16: "EEPROM location on Fabric",
    17: "X86 CPU MAC Base/Size",
    18: "BMC MAC Base/Size",
    19: "Switch ASIC MAC Base/Size",
    20: "META Reserved MAC Base/Size",
    21: "RMA",
    250: "CRC16"
}

def show_fru_content(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        # 1. Version 處理 (Offset 2)
        version = data[2]
        print(f"\n[*] FRU Version: {version}")
        print(f"{'-'*60}")
        print(f"{'Type':<6} {'Name':<28} {'Length':<7} {'Value'}")
        print(f"{'-'*60}")

        # 2. TLV 解析從 Offset 4 開始
        ptr = 4
        # 限制解析範圍，直到遇到 CRC (Tag 250) 或檔案末尾
        while ptr < len(data):
            t_type = data[ptr]
            
            # 結尾檢查 (如果是填充或無效 Tag)
            if t_type == 0 or t_type == 0xFF:
                ptr += 1
                continue

            t_len = data[ptr + 1]
            v_start = ptr + 2
            v_end = v_start + t_len
            val_bytes = data[v_start:v_end]

            name = FRU_MAPPING.get(t_type, "Unknown")
            
            # --- 根據表格規則處理顯示格式 ---
            if t_type in [8, 9, 10, 21]: # 單位元組數值
                display = str(val_bytes[0]) if val_bytes else "0"
            
            elif 17 <= t_type <= 20: # MAC Base (6) + Size (2)
                mac = ":".join(f"{b:02X}" for b in val_bytes[:6])
                # 這裡假設後面的 Bytes 代表 Size
                size = val_bytes[6] if t_len > 6 else 0
                display = f"{mac} (Size: {size})"
                
            elif t_type == 250: # CRC16
                display = f"0x{val_bytes.hex().upper()}"
            
            else: # 預設 ASCII
                display = val_bytes.decode('ascii', errors='ignore').strip()

            print(f"{t_type:<6} {name:<28} {t_len:<7} {display}")

            ptr = v_end
            if t_type == 250: break # 讀到 CRC 結束

        print(f"{'-'*60}")

    except Exception as e:
        print(f"❌ 解析失敗: {e}")
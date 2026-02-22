import sys
import os

def get_executable_path():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller --onefile 或 --onedir 模式
        return os.path.dirname(sys.executable)
    else:
        # 一般情況
        return os.path.dirname(os.path.abspath(__file__))

def create_or_replace_file(file_name):
    """
    檢查指定檔案是否存在，若存在則刪除後重新建立，若不存在則直接建立。

    Args:
        file_name: 要建立或替換的檔案名稱。
    """
    if os.path.exists(file_name):
        try:
            os.remove(file_name)
            print(f"檔案 {file_name} 已存在，已刪除並重新建立。")
        except OSError as e:
            print(f"刪除檔案 {file_name} 時發生錯誤: {e}")

        with open(file_name, "w") as f:
            # 可以在這裡寫入檔案內容
            pass  
    else:
        with open(file_name, "w") as f:
            # 可以在這裡寫入檔案內容
            pass  
        print(f"檔案 {file_name} 不存在，已建立。")
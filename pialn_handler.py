import os
import re
import hashlib
import subprocess
import sys

class PialnHandler:
    @staticmethod
    def get_current_version():
        if not os.path.exists("PialnCode.pialn"):
            with open("PialnCode.pialn", 'w', encoding='utf-8') as f:
                f.write("#version=0.0\n")
            return "0.0"
        
        with open("PialnCode.pialn", 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            version = re.search(r'#version=([\d.]+)', first_line)
            return version.group(1) if version else "0.0"

    @staticmethod
    def save_update(code):
        temp_file = "PialnCode.pialn.tmp"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            new_hash = hashlib.sha256(code.encode('utf-8')).hexdigest()
            old_hash = ""
            if os.path.exists("PialnCode.pialn"):
                with open("PialnCode.pialn", 'rb') as f:
                    old_hash = hashlib.sha256(f.read()).hexdigest()
            
            if new_hash != old_hash:
                os.replace(temp_file, "PialnCode.pialn")
            else:
                os.remove(temp_file)
                
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise

    @staticmethod
    def execute_pialn():
        try:
            base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
            starter_path = os.path.join(base_path, "starter-FutureMinds.exe" if os.name == "nt" else "starter-FutureMinds")
            
            if not os.path.exists(starter_path):
                raise Exception("Не найден компонент загрузки starter-FutureMinds")
                
            subprocess.Popen([starter_path], cwd=base_path)
            
        except Exception as e:
            error_msg = f"Ошибка запуска: {str(e)}"
            with open("error.txt", "w", encoding="utf-8") as f:
                f.write(error_msg)
            if os.name == "nt":
                os.startfile("error.txt")
            else:
                subprocess.Popen(["xdg-open", "error.txt"])

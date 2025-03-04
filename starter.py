import os
import sys

def main():
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        if not os.path.exists("PialnCode.pialn"):
            raise Exception("Файл PialnCode.pialn не найден")

        with open("PialnCode.pialn", "r", encoding="utf-8") as f:
            code = compile(f.read(), "PialnCode.pialn", "exec")
            exec(code, {"__name__": "__main__", "__file__": "PialnCode.pialn"})
            
    except Exception as e:
        with open("error.txt", "w", encoding="utf-8") as f:
            f.write(f"ERROR: {str(e)}")
        if os.name == "nt":
            os.startfile("error.txt")
        else:
            subprocess.Popen(["xdg-open", "error.txt"])
        sys.exit(1)

if __name__ == "__main__":
    main()

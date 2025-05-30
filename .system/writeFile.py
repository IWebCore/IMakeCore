
import sys
import os
import urllib.request
import ssl
import shutil

def write_file(save_path, content):
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(str(i) for i in content))
        return True
    except Exception as e:
        print(f"Write file failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python download.py <URL> <save_path>")
        sys.exit(1)
    success = write_file(sys.argv[1], sys.argv[2:])
    sys.exit(0 if success else 1)

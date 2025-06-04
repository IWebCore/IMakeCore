import os
import sys

def find_cpp_files(folder_path: str, suffixes):
    cpp_files = []
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d != '.git']
        for file in files:
            if file.lower().endswith(tuple(suffixes)):
                cpp_files.append(os.path.join(root, file))
    
    return cpp_files

if __name__ == "__main__":
    folder_path = sys.argv[1]
    if not os.path.exists(folder_path):
        print("文件夹不存在")
        sys.exit(1)
    
    suffixes = sys.argv[2:]
    result = find_cpp_files(folder_path, suffixes)
    for file in result:
        print(file)
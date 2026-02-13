import os
import zipfile
import json
from pathlib import Path

def zip_folders():
    # 获取当前工作目录
    current_dir = Path.cwd()
    
    # 遍历当前目录中的所有项目
    for item in current_dir.iterdir():
        # 只处理文件夹（跳过文件）
        if item.is_dir():
            # 跳过隐藏文件夹（以点开头）
            if item.name.startswith('.'):
                continue
                
            # 尝试读取package.json中的version
            version = ""
            package_json = item / "package.json"
            if package_json.exists():
                try:
                    with open(package_json, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        version = data.get("version", "")
                except (json.JSONDecodeError, KeyError):
                    pass
                    
            # 定义ZIP文件名（包含版本号）    
            zip_filename = f"{item.name}.zip"
            
            if not os.path.exists(current_dir / "../zipPackages"):
                os.mkdir(current_dir / "../zipPackages" )
            zip_path = current_dir / "../zipPackages" / zip_filename
            
            
            # 创建ZIP文件
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 遍历文件夹中的所有文件和子文件夹
                for root, dirs, files in os.walk(item):
                    # 过滤.git文件夹
                    if '.git' in dirs:
                        dirs.remove('.git')
                    # 将每个文件添加到ZIP中
                    for file in files:
                        file_path = Path(root) / file
                        # 在ZIP中创建相对路径
                        arcname = file_path.relative_to(item.absolute())
                        zipf.write(file_path, arcname)
            
            print(f"已创建: {zip_filename}")

if __name__ == "__main__":
    
    zip_folders()
    print("操作完成！")
#!/usr/bin/env python3
"""
重命名.lib文件夹中的子文件夹，基于package.json中的publisher、name和version字段。
同时删除.git文件夹、.vscode文件夹和.gitignore文件。

使用方法:
  python rename_folders.py           # 执行实际操作
  python rename_folders.py --dry-run # 只显示将要执行的操作，不实际执行
"""

import os
import json
import shutil
import stat
from pathlib import Path
import sys
import argparse

def read_package_json(folder_path):
    """读取package.json文件并返回publisher、name和version字段"""
    package_json_path = folder_path / "package.json"
    
    if not package_json_path.exists():
        print(f"警告: {folder_path} 中没有找到package.json文件")
        return None, None, None
    
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        publisher = data.get("publisher", "")
        name = data.get("name", "")
        version = data.get("version", "")
        
        if not publisher or not name or not version:
            print(f"警告: {folder_path}/package.json 中缺少必要的字段")
            print(f"  publisher: {publisher}, name: {name}, version: {version}")
            return None, None, None
        
        return publisher, name, version
        
    except json.JSONDecodeError as e:
        print(f"错误: 无法解析 {folder_path}/package.json: {e}")
        return None, None, None
    except Exception as e:
        print(f"错误: 读取 {folder_path}/package.json 时发生错误: {e}")
        return None, None, None

def generate_new_name(publisher, name, version):
    """生成新的文件夹名称: publisher@name@version"""
    # 清理名称中的特殊字符，确保适合作为文件夹名称
    publisher_clean = publisher.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    name_clean = name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    version_clean = version.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    
    return f"{publisher_clean}@{name_clean}@{version_clean}"

def remove_readonly(func, path, excinfo):
    """处理Windows上只读文件的删除"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def delete_unwanted_items(folder_path, dry_run=False):
    """删除.git文件夹、.vscode文件夹和.gitignore文件"""
    items_to_delete = [
        folder_path / ".git",
        folder_path / ".vscode",
        folder_path / ".gitignore"
    ]
    
    for item_path in items_to_delete:
        if item_path.exists():
            if dry_run:
                if item_path.is_dir():
                    print(f"  [干运行] 将删除文件夹: {item_path.name}")
                else:
                    print(f"  [干运行] 将删除文件: {item_path.name}")
            else:
                try:
                    if item_path.is_dir():
                        # 使用自定义错误处理函数来处理只读文件
                        shutil.rmtree(item_path, onerror=remove_readonly)
                        print(f"  已删除文件夹: {item_path.name}")
                    else:
                        # 对于文件，先尝试修改权限
                        try:
                            os.chmod(item_path, stat.S_IWRITE)
                        except:
                            pass
                        os.remove(item_path)
                        print(f"  已删除文件: {item_path.name}")
                except Exception as e:
                    print(f"  警告: 无法删除 {item_path}: {e}")

def process_folder(folder_path, lib_dir, dry_run=False):
    """处理单个文件夹"""
    print(f"处理文件夹: {folder_path.name}")
    
    # 读取package.json
    publisher, name, version = read_package_json(folder_path)
    if not publisher or not name or not version:
        print(f"  跳过 {folder_path.name} (缺少必要信息)")
        return False
    
    # 生成新名称
    new_name = generate_new_name(publisher, name, version)
    
    # 检查是否需要重命名
    if folder_path.name == new_name:
        print(f"  文件夹名称已经是正确的: {new_name}")
    else:
        # 检查目标文件夹是否已存在
        new_path = lib_dir / new_name
        if new_path.exists():
            print(f"  错误: 目标文件夹已存在: {new_name}")
            return False
        
        if dry_run:
            print(f"  [干运行] 将重命名为: {new_name}")
            # 在干运行模式下，我们假设重命名会成功
            folder_path = new_path  # 模拟更新引用到新路径
        else:
            # 重命名文件夹
            try:
                folder_path.rename(new_path)
                print(f"  重命名为: {new_name}")
                folder_path = new_path  # 更新引用到新路径
            except Exception as e:
                print(f"  错误: 无法重命名文件夹: {e}")
                return False
    
    # 删除不需要的文件和文件夹
    delete_unwanted_items(folder_path, dry_run)
    
    return True

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='重命名.lib文件夹中的子文件夹')
    parser.add_argument('--dry-run', action='store_true', 
                       help='只显示将要执行的操作，不实际执行')
    args = parser.parse_args()
    
    dry_run = args.dry_run
    
    if dry_run:
        print("=== 干运行模式 ===")
        print("只显示将要执行的操作，不会实际修改文件或文件夹")
        print()
    
    # 获取.lib目录路径
    script_dir = Path(__file__).parent
    lib_dir = script_dir
    
    print(f"正在处理目录: {lib_dir}")
    print("=" * 60)
    
    # 获取所有子文件夹
    folders = []
    for item in lib_dir.iterdir():
        if item.is_dir():
            # 跳过隐藏文件夹（以点开头）
            if item.name.startswith('.'):
                continue
            folders.append(item)
    
    if not folders:
        print("没有找到需要处理的文件夹")
        return True
    
    print(f"找到 {len(folders)} 个文件夹需要处理")
    print()
    
    # 处理每个文件夹
    successful = 0
    skipped = 0
    failed = 0
    
    for folder in folders:
        print("-" * 40)
        if process_folder(folder, lib_dir, dry_run):
            successful += 1
        else:
            # 检查是否因为缺少package.json而跳过
            package_json_path = folder / "package.json"
            if not package_json_path.exists():
                skipped += 1
                print(f"  跳过 {folder.name} (没有package.json)")
            else:
                failed += 1
        print()
    
    print("=" * 60)
    if dry_run:
        print("干运行完成!")
        print("注意: 这是干运行模式，没有实际修改任何文件或文件夹")
    else:
        print("处理完成!")
    
    print(f"成功: {successful}, 跳过: {skipped}, 失败: {failed}")
    
    if failed > 0:
        print("\n注意: 有些文件夹处理失败，请检查上面的错误信息。")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

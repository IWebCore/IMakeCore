import os
import zipfile
from datetime import datetime

def create_zip(source_dir, output_path, exclude_dirs=None, exclude_files=None):
    """
    Create a zip archive of the source directory, excluding specified directories and files.
    
    Args:
        source_dir (str): Path to the directory to be zipped
        output_path (str): Path to the output zip file
        exclude_dirs (list): List of directory names to exclude
        exclude_files (list): List of file names to exclude
    """
    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_files is None:
        exclude_files = []
        
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Remove excluded directories from dirs list to prevent walking into them
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file in exclude_files:
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

if __name__ == '__main__':
        # Get current directory name
    current_dir = os.path.basename(os.getcwd())
    # Define directories and files to exclude
    exclude_dirs = ['.lib', '.github', '.git', '.cache', '.vscode']
    exclude_files = ['.gitignore', f'{current_dir}.zip']
    
    # Create output filename with timestamp
    output_filename = f'{current_dir}.zip'
    
    # Create the zip file
    create_zip('.', output_filename, exclude_dirs, exclude_files)
    print(f'Successfully created zip archive: {output_filename}')

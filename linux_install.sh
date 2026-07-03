#!/bin/bash

APP_NAME="IMakeCore"
DEFAULT_INSTALL_DIR="/opt/$APP_NAME"
TARGET="$DEFAULT_INSTALL_DIR"

# 检查 root 权限
if [ "$(id -u)" -ne 0 ]; then
    echo "Requesting Administrative Privileges..."
    exec sudo "$0" "$@"
    exit $?
fi

echo "Default installation directory: $TARGET"

# 检查并删除已存在的目录
if [ -d "$TARGET" ]; then
    echo "Removing existing directory: $TARGET"
    rm -rf "$TARGET" || {
        echo "Error: Failed to remove existing directory"
        exit 1
    }
fi

mkdir -p "$TARGET" || {
    echo "Error: Failed to create directory"
    exit 1
}

chmod 777 "$TARGET" || {
    echo "Error: Failed to set directory permissions"
    exit 1
}

echo "Copying files..."
cp -r "$(dirname "$0")"/. "$TARGET/" || {
    echo "Error: Failed to copy files"
    exit 1
}

chmod -R 777 "$TARGET" || {
    echo "Error: Failed to set recursive permissions"
    exit 1
}

# 确保 .system 目录存在（必须在创建 imakecore_user_env.sh 之前）
if [ ! -d "$TARGET/.system" ]; then
    mkdir -p "$TARGET/.system" || {
        echo "Error: Failed to create .system directory"
        exit 1
    }
    chmod 777 "$TARGET/.system" || {
        echo "Warning: Failed to set .system directory permissions"
    }
fi

# 创建默认配置文件（如果不存在）
if [ ! -f "$TARGET/.system/.IMakeCore.prf" ]; then
    cat > "$TARGET/.system/.IMakeCore.prf" << 'EOF'
# IMakeCore Configuration File
IMAKECORE_PLATFORM=linux
EOF
    chmod 644 "$TARGET/.system/.IMakeCore.prf" || {
        echo "Warning: Failed to set .IMakeCore.prf permissions"
    }
fi

if [ ! -f "$TARGET/.system/.IMakeCore.cmake" ]; then
    cat > "$TARGET/.system/.IMakeCore.cmake" << EOF
# IMakeCore CMake Configuration
set(IMAKECORE_ROOT "$TARGET")
EOF
    chmod 644 "$TARGET/.system/.IMakeCore.cmake" || {
        echo "Warning: Failed to set .IMakeCore.cmake permissions"
    }
fi

# 设置环境变量
echo "Setting environment variables..."

cat > /etc/profile.d/imakecore_vars.sh << EOF
#!/bin/sh
# IMakeCore Environment Variables
export IMAKECORE_ROOT="$TARGET"
export ICMakeCore="$TARGET/.system/.IMakeCore.cmake"
export IQMakeCore="$TARGET/.system/.IMakeCore.prf"

# 添加程序目录到echo PATH
if [ -d "$TARGET/.programs/linux" ]; then
    export PATH="$TARGET/.programs/linux:\$PATH"
fi
EOF

# 设置环境变量文件权限：所有用户都可读取
chmod 644 /etc/profile.d/imakecore_vars.sh || {
    echo "Error: Failed to set environment file permissions"
    exit 1
}

# 备份原始的 /etc/environment
if [ -f /etc/environment ]; then
    cp /etc/environment /etc/environment.bak.imakecore
fi

# 读取现有的 /etc/environment
if [ -f /etc/environment ]; then
    ENV_CONTENT=$(cat /etc/environment)
else
    ENV_CONTENT=""
fi

# 移除可能存在的旧IMakeCore设置
ENV_CONTENT=$(echo "$ENV_CONTENT" | grep -v "IMAKECORE_ROOT=" | grep -v "ICMakeCore=" | grep -v "IQMakeCore=")

# 添加新的环境变量设置
cat > /etc/environment << EOF
$ENV_CONTENT
IMAKECORE_ROOT="$TARGET"
ICMakeCore="$TARGET/.system/.IMakeCore.cmake"
IQMakeCore="$TARGET/.system/.IMakeCore.prf"
EOF

# 3. 创建符号链接到标准路径（确保程序能在PATH中找到）
if [ -d "$TARGET/.programs/linux" ]; then
    echo "Creating symbolic links to standard paths..."
    
    # 创建 /usr/local/bin 目录如果不存在
    mkdir -p /usr/local/bin
    
    # 为 .programs/linux 目录下的所有可执行文件创建符号链接
    for program in "$TARGET/.programs/linux"/*; do
        if [ -f "$program" ] && [ -x "$program" ]; then
            program_name=$(basename "$program")
            ln -sf "$program" "/usr/local/bin/$program_name" 2>/dev/null || {
                echo "Warning: Failed to create symlink for $program_name"
            }
        fi
    done
fi

cat > "$TARGET/.system/imakecore_user_env.sh" << 'EOF'
#!/bin/bash
# User-level IMakeCore Environment Variables
# This file can be sourced in user's ~/.bashrc or ~/.profile

if [ -n "$IMAKECORE_ROOT" ]; then
    echo "IMakeCore environment already loaded."
else
    # Load IMakeCore environment variables
    export IMAKECORE_ROOT="__TARGET_DIR__"
    export ICMakeCore="__TARGET_DIR__/.system/.IMakeCore.cmake"
    export IQMakeCore="__TARGET_DIR__/.system/.IMakeCore.prf"
    
    # Add programs directory to PATH
    if [ -d "__TARGET_DIR__/.programs/linux" ]; then
        export PATH="__TARGET_DIR__/.programs/linux:$PATH"
    fi
    
    echo "IMakeCore environment loaded for user session."
fi
EOF

# 替换模板中的占位符
sed -i "s|__TARGET_DIR__|$TARGET|g" "$TARGET/.system/imakecore_user_env.sh"
chmod 644 "$TARGET/.system/imakecore_user_env.sh"

# 立即应用到当前会话和所有已打开的 shell（与 /etc/profile.d 中的格式保持一致）
export IMAKECORE_ROOT="$TARGET"
export ICMakeCore="$TARGET/.system/.IMakeCore.cmake"
export IQMakeCore="$TARGET/.system/.IMakeCore.prf"

if [ -d "$TARGET/.programs/linux" ]; then
    export PATH="$TARGET/.programs/linux:$PATH"
fi

# 为当前 shell 刷新 /etc/profile.d 中的变量
if [ -f /etc/profile.d/imakecore_vars.sh ]; then
    source /etc/profile.d/imakecore_vars.sh
fi


# 显示完成信息
echo ""
echo "========================================="
echo "IMakeCore installation completed successfully!"
echo "========================================="
echo ""
echo "Installation directory: $TARGET"
echo ""
echo "IMPORTANT: To apply environment variables to current terminal, run:"
echo "    source /etc/profile.d/imakecore_vars.sh"
echo ""
echo "Or simply open a new terminal window."
echo ""

exit 0

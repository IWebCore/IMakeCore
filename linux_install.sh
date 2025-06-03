
#!/bin/bash

# 安装配置
APP_NAME="IMakeCore"
DEFAULT_INSTALL_DIR="/opt/$APP_NAME"

# 检查root权限
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "Requesting Administrative Privileges..."
        exec sudo "$0" "$@"
        exit $?
    fi
}

# 尝试使用zenity选择目录
select_directory() {
    if command -v zenity &> /dev/null; then
        TARGET=$(zenity --file-selection --directory --title="请选择安装目录" 2>/dev/null)
        [ $? -eq 0 ] && return 0
    fi
    
    echo "Zenity不可用或用户取消选择，使用默认目录: $DEFAULT_INSTALL_DIR" >&2
    TARGET="$DEFAULT_INSTALL_DIR"
    return 1
}

# 主安装流程
install() {
    check_root

    echo "finish check $APP_NAME"

    select_directory

    echo "finish select $APP_NAME"
    echo "$TARGET"

    
    mkdir -p "$TARGET" || {
        echo "无法创建目录 $TARGET" >&2
        exit 1
    }

    cp -r "$(dirname "$0")"/ "$TARGET/" || {
        echo "文件复制失败" >&2
        exit 1
    }

    # 1. 创建脚本文件（使用 sudo）
    sudo tee /etc/profile.d/imakecore_vars.sh > /dev/null <<EOF
#!/bin/sh

export IMAKECORE_ROOT="$TARGET"
export ICMakeCore="$TARGET/.system/.IMakeCore.cmake"
export IQMakeCore="$TARGET/.system/.IMakeCore.prf"
EOF

    # 2. 赋予执行权限
    sudo chmod +x /etc/profile.d/imakecore_vars.sh

    # 3. 立即生效（当前会话）
    . /etc/profile.d/imakecore_vars.sh

    # 4. 验证设置
    echo "IMAKECORE_ROOT = $IMAKECORE_ROOT"
    echo "ICMakeCore = $ICMakeCore"
    echo "IQMakeCore = $IQMakeCore"
    
    echo "安装成功完成"
}

install

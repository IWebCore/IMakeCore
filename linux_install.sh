
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
    select_directory
    
    mkdir -p "$TARGET" || {
        echo "无法创建目录 $TARGET" >&2
        exit 1
    }

    echo "正在安装到: $TARGET"
    cp -r "$(dirname "$0")"/* "$TARGET/" 2>/dev/null || {
        echo "文件复制失败" >&2
        exit 1
    }

    # 环境变量设置
    echo "export APP_HOME=\"$TARGET\"" >> /etc/profile
    source /etc/profile
    
    echo "安装成功完成"
}

install

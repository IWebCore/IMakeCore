
#!/bin/zsh

# 配置参数
APP_NAME="MyApp"
DEFAULT_INSTALL_DIR="/Applications/$APP_NAME"
LOG_FILE="/tmp/${APP_NAME}_install.log"

# 管理员权限检查
check_privileges() {
    if [[ $EUID -ne 0 ]]; then
        echo "请求管理员权限..."
        exec sudo -p "请输入密码: " "$0" "$@"
        exit $?
    fi
}

# 目录选择（使用osascript GUI）
select_directory() {
    local selected=$(osascript <<EOF
try
    set chosen to choose folder with prompt "请选择安装目录"
    POSIX path of chosen
on error
    return "cancel"
end try
EOF
    )

    if [[ "$selected" == "cancel" ]] || [[ -z "$selected" ]]; then
        echo "使用默认安装目录: $DEFAULT_INSTALL_DIR" | tee -a $LOG_FILE
        INSTALL_DIR="$DEFAULT_INSTALL_DIR"
        return 1
    else
        INSTALL_DIR="${selected%/}"
        return 0
    fi
}

# 主安装流程
install() {
    check_privileges
    select_directory

    echo "开始安装到: $INSTALL_DIR" | tee -a $LOG_FILE
    mkdir -p "$INSTALL_DIR" || {
        echo "无法创建目录" | tee -a $LOG_FILE
        return 1
    }

    # 复制文件（示例）
    echo "正在复制文件..." | tee -a $LOG_FILE
    cp -R "$(dirname "$0")/" "$INSTALL_DIR/" 2>/dev/null || {
        echo "文件复制失败" | tee -a $LOG_FILE
        return 1
    }

    # 设置环境变量
    echo "配置环境变量..." | tee -a $LOG_FILE
    echo "export ${APP_NAME}_HOME=\"$INSTALL_DIR\"" >> /etc/zshenv
    source /etc/zshenv

    # 修复权限
    chmod -R 755 "$INSTALL_DIR"
    chown -R $(whoami):admin "$INSTALL_DIR"

    echo "安装成功完成" | tee -a $LOG_FILE
}

# 执行安装
install

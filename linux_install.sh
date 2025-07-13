#!/bin/bash

APP_NAME="IMakeCore"
DEFAULT_INSTALL_DIR="/opt/$APP_NAME"

check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "Requesting Administrative Privileges..."
        exec sudo "$0" "$@"
        exit $?
    fi
}

select_directory() {
    if command -v zenity &> /dev/null; then
        TARGET=$(zenity --file-selection --directory --title="please select the directory to install $APP_NAME" 2>/dev/null)
        [ $? -eq 0 ] && return 0
    fi
    
    echo "Zenity cannot be found, select the default directory: $DEFAULT_INSTALL_DIR" >&2
    TARGET="$DEFAULT_INSTALL_DIR"
    return 1
}

install() {
    check_root

    echo "finish check $APP_NAME"

    select_directory

    echo "finish select $APP_NAME"
    echo "$TARGET"

    
    mkdir -p "$TARGET" || {
        echo "fail to create directory $TARGET" >&2
        exit 1
    }

    cp -r "$(dirname "$0")"/. "$TARGET/" || {
        echo "fail to copy files" >&2
        exit 1
    }

    sudo tee /etc/profile.d/imakecore_vars.sh > /dev/null <<EOF
#!/bin/sh

export IMAKECORE_ROOT="$TARGET"
export ICMakeCore="$TARGET/.system/.IMakeCore.cmake"
export IQMakeCore="$TARGET/.system/.IMakeCore.prf"
EOF

    sudo chmod +x /etc/profile.d/imakecore_vars.sh

    . /etc/profile.d/imakecore_vars.sh

    echo "IMAKECORE_ROOT = $IMAKECORE_ROOT"
    echo "ICMakeCore = $ICMakeCore"
    echo "IQMakeCore = $IQMakeCore"
    
    echo "installation completed"
}

install

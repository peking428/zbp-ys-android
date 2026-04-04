#!/bin/bash
# ZBP压缩解压工具 - Android APK打包脚本
# 需要在Linux环境或WSL中运行

echo "=========================================="
echo "ZBP压缩解压工具 - Android APK打包"
echo "=========================================="

# 检查是否安装了buildozer
if ! command -v buildozer &> /dev/null
then
    echo "正在安装buildozer..."
    pip install buildozer
    pip install cython
fi

# 清理旧的构建文件
echo "清理旧的构建文件..."
rm -rf .buildozer
rm -rf bin

# 开始构建APK
echo "开始构建APK..."
buildozer -v android debug

echo "=========================================="
echo "构建完成！"
echo "APK文件位置: bin/"
echo "=========================================="

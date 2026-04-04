@echo off
chcp 65001 >nul
echo ==========================================
echo ZBP压缩解压工具 - GitHub Actions构建
echo ==========================================
echo.

cd /d "C:\Users\peking428\Desktop\工作 -szfh\AFDX\GLM-5\android_app"

echo [1/5] 初始化Git仓库...
git init
git branch -M main

echo.
echo [2/5] 添加文件到Git...
git add .

echo.
echo [3/5] 提交更改...
git commit -m "Initial commit: ZBP压缩解压工具 v3.0 - Android版"

echo.
echo ==========================================
echo Git仓库准备完成!
echo ==========================================
echo.
echo 下一步操作:
echo.
echo 1. 在GitHub创建新仓库: https://github.com/new
echo    仓库名: zbp-ys-android
echo.
echo 2. 执行以下命令推送代码:
echo    git remote add origin https://github.com/你的用户名/zbp-ys-android.git
echo    git push -u origin main
echo.
echo 3. 进入 Actions 页面查看构建状态
echo.
echo ==========================================

set /p username="请输入您的GitHub用户名: "
set /p reponame="请输入仓库名称 (默认zbp-ys-android): "
if "%reponame%"=="" set reponame=zbp-ys-android

echo.
echo [4/5] 配置远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/%username%/%reponame%.git
echo 远程仓库: https://github.com/%username%/%reponame%.git

echo.
echo [5/5] 推送到GitHub...
set /p pushnow="是否现在推送? (Y/N): "
if /i "%pushnow%"=="Y" (
    git push -u origin main
    echo.
    echo ==========================================
    echo 推送成功!
    echo ==========================================
    echo.
    echo GitHub Actions将自动开始构建APK!
    echo 查看构建状态: https://github.com/%username%/%reponame%/actions
    echo.
    set /p open="是否打开Actions页面? (Y/N): "
    if /i "%open%"=="Y" start https://github.com/%username%/%reponame%/actions
)

echo.
pause

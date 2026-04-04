@echo off
chcp 65001 >nul
echo ==========================================
echo 触发GitHub Actions构建
echo ==========================================
echo.
echo 正在打开GitHub Actions页面...
echo.
echo 请按照以下步骤操作:
echo.
echo 1. 在打开的页面中点击 "Build Android APK"
echo 2. 点击右侧的 "Run workflow" 按钮
echo 3. 选择 main 分支
echo 4. 点击绿色的 "Run workflow" 按钮
echo.
echo ==========================================
pause
start https://github.com/peking428/zbp-ys-android/actions

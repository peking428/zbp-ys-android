# ZBP压缩解压工具 - Android APK一键构建脚本
# 此脚本将自动安装WSL并构建APK

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ZBP压缩解压工具 - Android APK构建" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$projectPath = "C:\Users\peking428\Desktop\工作 -szfh\AFDX\GLM-5\android_app"

# 检查WSL是否已安装
Write-Host "`n[1/5] 检查WSL环境..." -ForegroundColor Yellow
$wslInstalled = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -ErrorAction SilentlyContinue

if (-not $wslInstalled -or $wslInstalled.State -ne "Enabled") {
    Write-Host "正在启用WSL功能..." -ForegroundColor Yellow
    
    # 启用WSL功能
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    
    Write-Host "WSL功能已启用，需要重启电脑后继续..." -ForegroundColor Green
    Write-Host "请重启电脑后重新运行此脚本" -ForegroundColor Green
    
    $restart = Read-Host "是否立即重启? (Y/N)"
    if ($restart -eq "Y" -or $restart -eq "y") {
        Restart-Computer -Force
    }
    exit
}

# 检查Ubuntu是否已安装
Write-Host "`n[2/5] 检查Ubuntu环境..." -ForegroundColor Yellow
$ubuntuInstalled = wsl -l 2>$null | Select-String "Ubuntu"

if (-not $ubuntuInstalled) {
    Write-Host "正在安装Ubuntu..." -ForegroundColor Yellow
    wsl --install -d Ubuntu --no-launch
    
    Write-Host "Ubuntu安装完成!" -ForegroundColor Green
    Write-Host "请完成Ubuntu初始设置（设置用户名和密码）后重新运行此脚本" -ForegroundColor Green
    wsl -d Ubuntu
    exit
}

# 在WSL中安装依赖并构建
Write-Host "`n[3/5] 安装构建依赖..." -ForegroundColor Yellow

wsl -d Ubuntu -e bash -c @"
    sudo apt update
    sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
    pip3 install --user buildozer cython
"@

Write-Host "`n[4/5] 复制项目文件到WSL..." -ForegroundColor Yellow

# 复制项目到WSL
wsl -d Ubuntu -e bash -c @"
    rm -rf ~/zbp_ys
    mkdir -p ~/zbp_ys
"@

# 复制文件
wsl -d Ubuntu -e cp -r "/mnt/c/Users/peking428/Desktop/工作 -szfh/AFDX/GLM-5/android_app/*" "~/zbp_ys/"

Write-Host "`n[5/5] 开始构建APK..." -ForegroundColor Yellow
Write-Host "首次构建需要下载Android SDK/NDK，请耐心等待..." -ForegroundColor Yellow

wsl -d Ubuntu -e bash -c @"
    cd ~/zbp_ys
    chmod +x build.sh
    ./build.sh
"@

# 复制APK回Windows
Write-Host "`n正在复制APK文件..." -ForegroundColor Yellow

$apkPath = Join-Path $projectPath "..\..\..\zbp_ys.apk"
wsl -d Ubuntu -e cp "~/zbp_ys/bin/*.apk" "/mnt/c/Users/peking428/Desktop/工作 -szfh/zbp_ys.apk"

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "构建完成!" -ForegroundColor Green
Write-Host "APK文件位置: C:\Users\peking428\Desktop\工作 -szfh\zbp_ys.apk" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

Write-Host "`n安装说明:" -ForegroundColor Cyan
Write-Host "1. 将APK文件传输到手机" -ForegroundColor White
Write-Host "2. 在手机上打开APK文件" -ForegroundColor White
Write-Host "3. 允许安装未知来源应用" -ForegroundColor White
Write-Host "4. 完成安装后即可使用" -ForegroundColor White

# ZBP压缩解压工具 - Git初始化脚本
# 用于上传到GitHub并自动构建APK

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ZBP压缩解压工具 - Git初始化" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$projectPath = "C:\Users\peking428\Desktop\工作 -szfh\AFDX\GLM-5\android_app"

Set-Location $projectPath

# 初始化Git仓库
Write-Host "`n[1/4] 初始化Git仓库..." -ForegroundColor Yellow
git init
git branch -M main

# 创建.gitignore
Write-Host "[2/4] 创建.gitignore文件..." -ForegroundColor Yellow
@"
.buildozer/
bin/
__pycache__/
*.pyc
*.pyo
*.apk
*.aab
*.log
"@ | Out-File -FilePath ".gitignore" -Encoding utf8

# 添加所有文件
Write-Host "[3/4] 添加文件到Git..." -ForegroundColor Yellow
git add .

# 提交
Write-Host "[4/4] 提交更改..." -ForegroundColor Yellow
git commit -m "Initial commit: ZBP压缩解压工具 v3.0"

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Git仓库初始化完成!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

Write-Host @"

下一步操作:

1. 在GitHub创建新仓库:
   https://github.com/new
   仓库名: zbp-ys-android

2. 关联远程仓库并推送:
   git remote add origin https://github.com/YOUR_USERNAME/zbp-ys-android.git
   git push -u origin main

3. 触发自动构建:
   进入仓库 → Actions → Build Android APK → Run workflow

4. 下载APK:
   构建完成后在 Artifacts 中下载

"@ -ForegroundColor Cyan

# 询问是否打开GitHub
$openGithub = Read-Host "是否打开GitHub创建仓库页面? (Y/N)"
if ($openGithub -eq "Y" -or $openGithub -eq "y") {
    Start-Process "https://github.com/new"
}

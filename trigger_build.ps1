# 触发GitHub Actions构建脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "触发GitHub Actions构建" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$ghPath = "C:\Program Files\GitHub CLI\gh.exe"

# 检查是否已登录
Write-Host "`n[1/3] 检查GitHub登录状态..." -ForegroundColor Yellow
$authStatus = & $ghPath auth status 2>&1

if ($authStatus -match "not logged in") {
    Write-Host "需要登录GitHub..." -ForegroundColor Yellow
    Write-Host "即将打开浏览器进行登录..." -ForegroundColor Yellow
    
    # 使用web方式登录
    & $ghPath auth login --web --git-protocol https
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "登录失败，请手动执行以下命令:" -ForegroundColor Red
        Write-Host "  gh auth login" -ForegroundColor White
        pause
        exit
    }
}

Write-Host "GitHub已登录!" -ForegroundColor Green

# 触发workflow
Write-Host "`n[2/3] 触发GitHub Actions构建..." -ForegroundColor Yellow

$repo = "peking428/zbp-ys-android"
$workflow = "build.yml"

# 触发workflow
$result = & $ghPath workflow run $workflow --repo $repo --ref main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "构建已触发!" -ForegroundColor Green
} else {
    Write-Host "触发结果: $result" -ForegroundColor Yellow
}

# 查看构建状态
Write-Host "`n[3/3] 查看构建状态..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

$runs = & $ghPath run list --repo $repo --limit 3 2>&1
Write-Host $runs

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "构建已触发!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

Write-Host @"

查看构建进度:
https://github.com/$repo/actions

构建完成后(约15-20分钟):
1. 进入 Actions 页面
2. 点击最新的 workflow
3. 在 Artifacts 中下载 zbp_ys_apk.zip
4. 解压得到APK文件

"@ -ForegroundColor Cyan

# 打开Actions页面
$open = Read-Host "是否打开Actions页面? (Y/N)"
if ($open -eq "Y" -or $open -eq "y") {
    Start-Process "https://github.com/$repo/actions"
}

pause

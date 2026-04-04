# 修复GitHub仓库并触发构建

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "修复GitHub仓库结构" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$ghPath = "C:\Program Files\GitHub CLI\gh.exe"
$repo = "peking428/zbp-ys-android"

# 读取workflow文件内容
$workflowPath = "C:\Users\peking428\Desktop\工作 -szfh\AFDX\GLM-5\android_app\.github\workflows\build.yml"
$workflowContent = Get-Content $workflowPath -Raw
$encodedContent = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($workflowContent))

Write-Host "`n[1/3] 创建.github/workflows目录..." -ForegroundColor Yellow

# 创建.github/workflows/build.yml文件
$result = & $ghPath api --method PUT repos/$repo/contents/.github/workflows/build.yml `
    -f message="Add GitHub Actions workflow" `
    -f content=$encodedContent `
    -f branch="main" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "workflow文件创建成功!" -ForegroundColor Green
} else {
    Write-Host "结果: $result" -ForegroundColor Yellow
}

# 创建.gitignore文件
Write-Host "`n[2/3] 创建.gitignore文件..." -ForegroundColor Yellow
$gitignoreContent = @"
.buildozer/
bin/
__pycache__/
*.pyc
*.pyo
*.apk
*.aab
*.log
"@
$encodedGitignore = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($gitignoreContent))

$result2 = & $ghPath api --method PUT repos/$repo/contents/.gitignore `
    -f message="Add .gitignore" `
    -f content=$encodedGitignore `
    -f branch="main" 2>&1

Write-Host "`n[3/3] 触发构建..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# 触发workflow
$result3 = & $ghPath workflow run build.yml --repo $repo --ref main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n==========================================" -ForegroundColor Green
    Write-Host "构建已触发!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
} else {
    Write-Host "触发结果: $result3" -ForegroundColor Yellow
}

# 查看构建状态
Start-Sleep -Seconds 3
$runs = & $ghPath run list --repo $repo --limit 3 2>&1
Write-Host "`n构建状态:" -ForegroundColor Cyan
Write-Host $runs

Write-Host "`n查看详情: https://github.com/$repo/actions" -ForegroundColor Cyan
Start-Process "https://github.com/$repo/actions"

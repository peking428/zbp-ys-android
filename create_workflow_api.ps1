# 直接通过API创建workflow文件

$ghPath = "C:\Program Files\GitHub CLI\gh.exe"
$repo = "peking428/zbp-ys-android"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "创建GitHub Actions Workflow" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Workflow内容
$workflowContent = @'
name: Build Android APK

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Build APK with Buildozer
      uses: ArtemSBulgakov/buildozer-action@v1
      id: buildozer
      with:
        workdir: .
        target: android
        buildozer_version: stable
    
    - name: Upload APK artifact
      uses: actions/upload-artifact@v4
      with:
        name: zbp_ys_apk
        path: bin/*.apk
        retention-days: 30
    
    - name: Create Release
      if: github.event_name == 'workflow_dispatch'
      uses: softprops/action-gh-release@v1
      with:
        files: bin/*.apk
        name: ZBP压缩解压工具 v3.0
        tag_name: v3.0.${{ github.run_number }}
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
'@

# Base64编码
$bytes = [System.Text.Encoding]::UTF8.GetBytes($workflowContent)
$base64 = [Convert]::ToBase64String($bytes)

Write-Host "`n[1/3] 创建.github/workflows/build.yml..." -ForegroundColor Yellow

# 使用gh api创建文件
$result = & $ghPath api --method PUT "repos/$repo/contents/.github/workflows/build.yml" `
    -f message="Add GitHub Actions workflow" `
    -f content="$base64" `
    -f branch="main" 2>&1

Write-Host $result

Write-Host "`n[2/3] 等待文件同步..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`n[3/3] 触发构建..." -ForegroundColor Yellow
$triggerResult = & $ghPath workflow run build.yml --repo $repo --ref main 2>&1
Write-Host $triggerResult

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "完成!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# 查看构建状态
Start-Sleep -Seconds 3
& $ghPath run list --repo $repo --limit 3

# 打开Actions页面
Start-Process "https://github.com/$repo/actions"

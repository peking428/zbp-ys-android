# 完整修复并触发构建

$ghPath = "C:\Program Files\GitHub CLI\gh.exe"
$repo = "peking428/zbp-ys-android"
$tempDir = "C:\Users\peking428\Desktop\temp_zbp_repo"

Write-Host "清理临时目录..." -ForegroundColor Yellow
if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir }

Write-Host "克隆仓库..." -ForegroundColor Yellow
& $ghPath repo clone $repo $tempDir

Set-Location $tempDir

Write-Host "创建正确的目录结构..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path ".github\workflows" | Out-Null

# 写入workflow文件
$workflowContent = @"
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
        tag_name: v3.0.`${{ github.run_number }}
      env:
        GITHUB_TOKEN: `${{ secrets.GITHUB_TOKEN }}
"@

$workflowContent | Out-File -FilePath ".github\workflows\build.yml" -Encoding utf8 -NoNewline

Write-Host "配置Git..." -ForegroundColor Yellow
& git config user.email "peking428@users.noreply.github.com"
& git config user.name "peking428"

Write-Host "添加并提交..." -ForegroundColor Yellow
& git add .
& git commit -m "Fix: Add correct .github/workflows/build.yml"

Write-Host "推送..." -ForegroundColor Yellow
& git push

Write-Host "触发构建..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
& $ghPath workflow run build.yml --repo $repo --ref main

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "完成! 构建已触发!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# 清理
Set-Location "C:\Users\peking428\Desktop\工作 -szfh"
Remove-Item -Recurse -Force $tempDir

# 打开Actions页面
Start-Process "https://github.com/$repo/actions"

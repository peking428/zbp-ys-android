# ZBP压缩解压工具 - GitHub Actions自动构建脚本
# 此脚本将自动完成所有步骤

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ZBP压缩解压工具 - GitHub Actions构建" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$projectPath = "C:\Users\peking428\Desktop\工作 -szfh\AFDX\GLM-5\android_app"

# 检查Git是否安装
Write-Host "`n[1/6] 检查Git环境..." -ForegroundColor Yellow
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue

if (-not $gitInstalled) {
    Write-Host "Git未安装，正在安装..." -ForegroundColor Yellow
    
    # 使用winget安装Git
    winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Git安装成功!" -ForegroundColor Green
        Write-Host "请重新打开PowerShell后继续..." -ForegroundColor Yellow
        $continue = Read-Host "是否继续? (Y/N)"
        if ($continue -ne "Y" -and $continue -ne "y") {
            exit
        }
    } else {
        Write-Host "自动安装失败，请手动安装Git:" -ForegroundColor Red
        Write-Host "1. 访问 https://git-scm.com/download/win" -ForegroundColor White
        Write-Host "2. 下载并安装Git" -ForegroundColor White
        Write-Host "3. 重新运行此脚本" -ForegroundColor White
        pause
        exit
    }
}

# 切换到项目目录
Set-Location $projectPath

# 初始化Git仓库
Write-Host "`n[2/6] 初始化Git仓库..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    git init
    git branch -M main
    Write-Host "Git仓库初始化完成!" -ForegroundColor Green
} else {
    Write-Host "Git仓库已存在" -ForegroundColor Green
}

# 添加所有文件
Write-Host "`n[3/6] 添加文件到Git..." -ForegroundColor Yellow
git add .
git status --short

# 提交更改
Write-Host "`n[4/6] 提交更改..." -ForegroundColor Yellow
$commitResult = git commit -m "Initial commit: ZBP压缩解压工具 v3.0 - Android版" 2>&1
Write-Host $commitResult

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Git仓库准备完成!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# 询问GitHub用户名
Write-Host @"

下一步: 推送到GitHub并触发自动构建

"@ -ForegroundColor Cyan

$githubUsername = Read-Host "请输入您的GitHub用户名"
$repoName = Read-Host "请输入仓库名称 (默认: zbp-ys-android)"
if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "zbp-ys-android"
}

Write-Host "`n[5/6] 配置远程仓库..." -ForegroundColor Yellow
$remoteUrl = "https://github.com/$githubUsername/$repoName.git"

# 移除旧的remote并添加新的
git remote remove origin 2>$null
git remote add origin $remoteUrl

Write-Host "远程仓库: $remoteUrl" -ForegroundColor Green

Write-Host "`n[6/6] 推送到GitHub..." -ForegroundColor Yellow
Write-Host "即将推送代码到GitHub，可能需要输入凭据..." -ForegroundColor Yellow

$push = Read-Host "是否现在推送? (Y/N)"
if ($push -eq "Y" -or $push -eq "y") {
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n==========================================" -ForegroundColor Green
        Write-Host "推送成功!" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        
        Write-Host @"

GitHub Actions将自动开始构建APK!

查看构建状态:
https://github.com/$githubUsername/$repoName/actions

构建完成后(约15-20分钟):
1. 进入 Actions 页面
2. 点击最新的 workflow
3. 在 Artifacts 中下载 zbp_ys_apk.zip
4. 解压得到APK文件

"@ -ForegroundColor Cyan
        
        # 打开GitHub Actions页面
        $openActions = Read-Host "是否打开GitHub Actions页面? (Y/N)"
        if ($openActions -eq "Y" -or $openActions -eq "y") {
            Start-Process "https://github.com/$githubUsername/$repoName/actions"
        }
    } else {
        Write-Host "`n推送失败，请检查:" -ForegroundColor Red
        Write-Host "1. GitHub用户名是否正确" -ForegroundColor White
        Write-Host "2. 仓库是否已创建 (https://github.com/new)" -ForegroundColor White
        Write-Host "3. 是否有推送权限" -ForegroundColor White
        
        $openCreate = Read-Host "是否打开创建仓库页面? (Y/N)"
        if ($openCreate -eq "Y" -or $openCreate -eq "y") {
            Start-Process "https://github.com/new"
        }
    }
} else {
    Write-Host @"

手动推送步骤:
1. 在GitHub创建仓库: https://github.com/new
   仓库名: $repoName
   
2. 执行以下命令:
   git push -u origin main
   
3. 等待Actions自动构建

"@ -ForegroundColor Cyan
    
    $openCreate = Read-Host "是否打开创建仓库页面? (Y/N)"
    if ($openCreate -eq "Y" -or $openCreate -eq "y") {
        Start-Process "https://github.com/new"
    }
}

Write-Host "`n完成!" -ForegroundColor Green

# 定期检查GitHub Actions构建状态并自动下载APK
# 使用方法: .\monitor_build.ps1

$ErrorActionPreference = "Continue"
$repoPath = "C:\Users\peking428\Desktop\工作 -szfh\AFDX\GLM-5\android_app"
$apkDownloadPath = "C:\Users\peking428\Desktop\工作 -szfh\APK下载"
$checkInterval = 60  # 检查间隔（秒）
$lastKnownRunId = 24013223865  # 上次已知的成功构建ID

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GitHub Actions 构建监控脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "仓库路径: $repoPath" -ForegroundColor Gray
Write-Host "APK下载路径: $apkDownloadPath" -ForegroundColor Gray
Write-Host "检查间隔: $checkInterval 秒" -ForegroundColor Gray
Write-Host "上次已知构建ID: $lastKnownRunId" -ForegroundColor Gray
Write-Host ""

function Get-LatestBuild {
    try {
        Push-Location $repoPath
        $result = gh run list --limit 1 --json databaseId,status,conclusion,headBranch,headSha,name,startedAt,updatedAt,url 2>&1
        Pop-Location
        
        if ($LASTEXITCODE -eq 0) {
            $build = $result | ConvertFrom-Json
            return $build[0]
        } else {
            Write-Host "错误: 无法获取构建状态 - $result" -ForegroundColor Red
            return $null
        }
    } catch {
        Write-Host "错误: 获取构建状态时发生异常 - $_" -ForegroundColor Red
        return $null
    }
}

function Download-APK {
    param([string]$runId)
    
    try {
        Write-Host "开始下载构建 $runId 的APK..." -ForegroundColor Yellow
        
        Push-Location $repoPath
        
        # 创建临时下载目录
        $tempDir = Join-Path $apkDownloadPath "temp_$runId"
        if (Test-Path $tempDir) {
            Remove-Item $tempDir -Recurse -Force
        }
        New-Item -ItemType Directory -Path $tempDir | Out-Null
        
        # 下载artifact
        Write-Host "正在使用 gh run download 下载..." -ForegroundColor Gray
        gh run download $runId --dir $tempDir 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "gh run download 失败"
        }
        
        # 查找APK文件
        $apkFiles = Get-ChildItem -Path $tempDir -Filter "*.apk" -Recurse
        if ($apkFiles.Count -eq 0) {
            throw "未找到APK文件"
        }
        
        $apkFile = $apkFiles[0]
        Write-Host "找到APK文件: $($apkFile.Name)" -ForegroundColor Green
        
        # 复制到目标位置
        $version = "v" + ($apkFile.Name -replace 'zbpys-(\d+\.\d+)-.*', '$1')
        $targetPath = Join-Path $apkDownloadPath "zbpys_$version.apk"
        
        Copy-Item $apkFile.FullName -Destination $targetPath -Force
        Write-Host "APK已复制到: $targetPath" -ForegroundColor Green
        
        # 清理临时目录
        Remove-Item $tempDir -Recurse -Force
        
        # 显示文件信息
        $fileInfo = Get-Item $targetPath
        Write-Host "文件大小: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Gray
        Write-Host "修改时间: $($fileInfo.LastWriteTime)" -ForegroundColor Gray
        
        Pop-Location
        return $true
    } catch {
        Write-Host "下载失败: $_" -ForegroundColor Red
        Pop-Location
        return $false
    }
}

# 主循环
try {
    while ($true) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "[$timestamp] 检查构建状态..." -ForegroundColor Cyan
        
        $latestBuild = Get-LatestBuild
        
        if ($latestBuild) {
            Write-Host "  最新构建ID: $($latestBuild.databaseId)" -ForegroundColor Gray
            Write-Host "  状态: $($latestBuild.status)" -ForegroundColor Gray
            Write-Host "  结论: $($latestBuild.conclusion)" -ForegroundColor Gray
            Write-Host "  分支: $($latestBuild.headBranch)" -ForegroundColor Gray
            Write-Host "  URL: $($latestBuild.url)" -ForegroundColor Gray
            
            # 检查是否有新的成功构建
            if ($latestBuild.databaseId -gt $lastKnownRunId -and $latestBuild.status -eq "completed" -and $latestBuild.conclusion -eq "success") {
                Write-Host ""
                Write-Host "🎉 发现新的成功构建！" -ForegroundColor Green
                Write-Host "构建ID: $($latestBuild.databaseId)" -ForegroundColor Green
                Write-Host ""
                
                # 下载APK
                if (Download-APK -runId $latestBuild.databaseId) {
                    $lastKnownRunId = $latestBuild.databaseId
                    Write-Host ""
                    Write-Host "✅ APK下载成功！" -ForegroundColor Green
                } else {
                    Write-Host ""
                    Write-Host "❌ APK下载失败，将在下次检查时重试" -ForegroundColor Red
                }
            } elseif ($latestBuild.status -eq "in_progress" -or $latestBuild.status -eq "queued") {
                Write-Host "  ⏳ 构建正在进行中..." -ForegroundColor Yellow
            }
        }
        
        Write-Host ""
        Write-Host "等待 $checkInterval 秒后再次检查..." -ForegroundColor Gray
        Write-Host "按 Ctrl+C 停止监控" -ForegroundColor Gray
        Write-Host ""
        
        Start-Sleep -Seconds $checkInterval
    }
} catch [System.Management.Automation.RuntimeException] {
    Write-Host ""
    Write-Host "监控已停止" -ForegroundColor Yellow
}

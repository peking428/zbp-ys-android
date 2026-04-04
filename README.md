# ZBP压缩解压工具 - Android版快速构建指南

## 🚀 快速开始（推荐）

### 方法一：GitHub Actions 在线构建（最简单）

**步骤：**

1. **创建GitHub账号**（如果没有）
   - 访问 https://github.com 注册

2. **创建新仓库**
   ```
   仓库名: zbp-ys-android
   设置为: Public 或 Private
   ```

3. **上传项目文件**
   - 将 `android_app` 文件夹中的所有文件上传到仓库
   - 确保 `.github/workflows/build.yml` 文件存在

4. **触发构建**
   - 进入仓库 → Actions → Build Android APK
   - 点击 "Run workflow" → Run workflow

5. **下载APK**
   - 等待构建完成（约15-20分钟）
   - 在 Artifacts 中下载 `zbp_ys_apk.zip`
   - 解压得到APK文件

---

### 方法二：使用WSL本地构建

**一键安装脚本：**

```powershell
# 以管理员身份运行PowerShell，执行：
Set-ExecutionPolicy Bypass -Scope Process -Force
& "C:\Users\peking428\Desktop\工作 -szfh\AFDX\GLM-5\android_app\build_windows.ps1"
```

---

### 方法三：使用Docker构建

**前提：** 安装 Docker Desktop

```powershell
cd "C:\Users\peking428\Desktop\工作 -szfh\AFDX\GLM-5\android_app"
docker pull kivy/buildozer
docker run --rm -v "${PWD}:/app" kivy/buildozer android debug
```

---

## 📱 安装到手机

### Android手机
1. 将APK传输到手机（微信、数据线等）
2. 打开APK文件
3. 允许"安装未知应用"
4. 完成安装

### 鸿蒙手机
1. 将APK传输到手机
2. 打开文件管理器
3. 点击APK文件
4. 允许安装
5. 完成安装

---

## 📋 系统兼容性

| 系统 | 版本要求 | 状态 |
|------|---------|------|
| Android | 5.0+ (API 21+) | ✅ 支持 |
| 鸿蒙 | 2.0 - 4.2 | ✅ 支持 |
| 鸿蒙 | 4.3+ (纯血鸿蒙) | ❌ 不支持 |

---

## 📁 项目结构

```
android_app/
├── main.py              # 主程序代码
├── buildozer.spec       # 打包配置
├── build.sh             # Linux构建脚本
├── build_windows.ps1    # Windows一键构建脚本
├── README.md            # 说明文档
└── .github/
    └── workflows/
        └── build.yml    # GitHub Actions配置
```

---

## ⚠️ 常见问题

**Q: 构建失败怎么办？**
A: 检查网络连接，确保能访问Google服务。可使用VPN或代理。

**Q: APK安装失败？**
A: 确保手机允许安装未知来源应用。设置 → 安全 → 未知来源。

**Q: 鸿蒙4.3能用吗？**
A: 鸿蒙4.3（纯血鸿蒙）不支持Android应用，需要鸿蒙原生版本。

---

## 🔧 技术支持

如有问题，请检查：
1. Python版本：3.8+
2. 网络连接正常
3. 磁盘空间充足（至少10GB）

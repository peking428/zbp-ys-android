# -*- coding: utf-8 -*-
import base64
import requests
import json

# GitHub配置
TOKEN = "gho_xxxxxxxxxxxx"  # 需要有效的token
REPO = "peking428/zbp-ys-android"

# Workflow文件内容
workflow_content = """name: Build Android APK

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
"""

# 编码为base64
encoded_content = base64.b64encode(workflow_content.encode('utf-8')).decode('utf-8')

# 使用gh CLI获取token
import subprocess
result = subprocess.run(['C:\\Program Files\\GitHub CLI\\gh.exe', 'auth', 'token'], capture_output=True, text=True)
token = result.stdout.strip()

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

# 创建文件
url = f"https://api.github.com/repos/{REPO}/contents/.github/workflows/build.yml"

data = {
    "message": "Add GitHub Actions workflow",
    "content": encoded_content,
    "branch": "main"
}

response = requests.put(url, headers=headers, json=data)
print(f"Status: {response.status_code}")
print(response.text)

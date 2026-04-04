# -*- coding: utf-8 -*-
import subprocess
import base64
import sys

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

encoded = base64.b64encode(workflow_content.encode('utf-8')).decode('utf-8')

cmd = [
    r'C:\Program Files\GitHub CLI\gh.exe', 'api', '--method', 'PUT',
    'repos/peking428/zbp-ys-android/contents/.github/workflows/build.yml',
    '-f', 'message=Add correct GitHub Actions workflow',
    '-f', 'content=' + encoded,
    '-f', 'branch=main'
]

print("Creating .github/workflows/build.yml...")
result = subprocess.run(cmd, capture_output=True, text=True)
print(f"Return code: {result.returncode}")
print(f"Stdout: {result.stdout}")
if result.stderr:
    print(f"Stderr: {result.stderr}")

if result.returncode == 0:
    print("\nWorkflow file created successfully!")
    print("Triggering workflow...")
    trigger_cmd = [
        r'C:\Program Files\GitHub CLI\gh.exe', 'workflow', 'run', 'build.yml',
        '--repo', 'peking428/zbp-ys-android', '--ref', 'main'
    ]
    trigger_result = subprocess.run(trigger_cmd, capture_output=True, text=True)
    print(f"Trigger return code: {trigger_result.returncode}")
    print(f"Trigger output: {trigger_result.stdout}")
    if trigger_result.stderr:
        print(f"Trigger stderr: {trigger_result.stderr}")

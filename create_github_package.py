# -*- coding: utf-8 -*-
"""
创建GitHub上传包
"""

import os
import shutil
import zipfile

project_dir = r"C:\Users\peking428\Desktop\工作 -szfh\AFDX\GLM-5\android_app"
output_zip = r"C:\Users\peking428\Desktop\工作 -szfh\zbp_ys_android_github.zip"

files_to_include = [
    "main.py",
    "buildozer.spec",
    "README.md",
    ".gitignore",
    ".github/workflows/build.yml",
]

print("=" * 50)
print("创建GitHub上传包")
print("=" * 50)

with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
    for file in files_to_include:
        file_path = os.path.join(project_dir, file)
        if os.path.exists(file_path):
            zf.write(file_path, file)
            print(f"添加: {file}")
        else:
            print(f"跳过: {file} (不存在)")

print(f"\n创建完成: {output_zip}")
print(f"文件大小: {os.path.getsize(output_zip) / 1024:.2f} KB")

print("""
========================================
上传到GitHub步骤:
========================================

1. 在GitHub创建新仓库:
   https://github.com/new
   仓库名: zbp-ys-android

2. 点击 "uploading an existing file"

3. 将以下文件拖拽上传:
   - main.py
   - buildozer.spec
   - README.md
   - .gitignore
   - .github/workflows/build.yml

4. 点击 "Commit changes"

5. 进入 Actions 页面查看构建状态

========================================
""")

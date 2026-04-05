[app]

title = ZBP Compress Tool
package.name = zbpys
package.domain = org.zbp

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 5.3

requirements = python3,kivy,pyzipper,plyer,android,pyjnius

orientation = portrait
fullscreen = 0

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.entrypoint = org.kivy.android.PythonActivity

[buildozer]
log_level = 2
warn_on_root = 1

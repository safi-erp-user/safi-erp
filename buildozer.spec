[app]
title = مدیریت تولید صافی
package.name = safierp
package.domain = org.safierp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy==2.3.1,sqlalchemy==2.0.23,arabic-reshaper,python-bidi,requests
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 30
android.minapi = 21
android.arch = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
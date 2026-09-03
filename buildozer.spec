[app]
title = FRIDAY
package.name = friday
package.domain = com.coder.friday
source.dir =.
source.include_exts = py,png,jpg,kv
version = 1.0
requirements = python3,kivy,pyjnius,android
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,RECORD_AUDIO
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license_agreements = True
[buildozer]
log_level = 2
[app:android]
android.archs = arm64-v8a
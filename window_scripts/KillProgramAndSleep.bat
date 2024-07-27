@echo off
taskkill /F /IM python.exe
rundll32.exe powrprof.dll,SetSuspendState 0,1,0
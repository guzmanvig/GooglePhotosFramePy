@echo off
setlocal

:: Check if brightness parameter is provided
if "%1"=="" (
    echo Usage: %0 brightness
    exit /b 1
)

:: Set the brightness value
set brightness=%1

:: Path to nircmd.exe
set path_to_nircmd=.\nircmd.exe

:: Call nircmd.exe with the brightness value
%path_to_nircmd% setbrightness %brightness%
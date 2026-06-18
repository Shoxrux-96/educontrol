@echo off
cd /d "C:\Users\Shoxrux\Desktop\educontrol"
title EDU Control Pro - Admin Installation
echo ============================================
echo  EDU Control Pro - Admin Installation
echo ============================================
echo.

echo [1/4] Enabling WSL2 feature...
dism /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
echo.
echo WSL2 enabled. Please REBOOT after installation completes.
echo.

echo [2/4] Installing Docker Desktop...
if not exist "%TEMP%\docker-installer.exe" (
    echo Downloading Docker Desktop...
    curl -L -o "%TEMP%\docker-installer.exe" "https://desktop.docker.com/win/stable/Docker%%20Desktop%%20Installer.exe"
)
start /wait "" "%TEMP%\docker-installer.exe" install --quiet --accept-license --backend=wsl-2
echo Docker Desktop installed.
echo.

echo [3/4] Installing Redis...
winget install -e --id Redis.Redis --accept-source-agreements --accept-package-agreements -h
echo.

echo [4/4] Installing MinGW (GCC)...
winget install -e --id BrechtSanders.WinLibs.POSIX.UCRT.LLVM --accept-source-agreements --accept-package-agreements -h
echo.

echo ============================================
echo  Installation complete!
echo  Please REBOOT your computer for WSL2 to work.
echo  After reboot, run: wsl --install -d Ubuntu
echo ============================================

pause

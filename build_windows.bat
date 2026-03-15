@echo off
chcp 65001 >nul
echo ========================================
echo FinDataHub Windows 打包脚本
echo ========================================
echo.

REM 检查是否在Windows环境中
if not "%OS%"=="Windows_NT" (
    echo [错误] 此脚本仅支持在Windows系统中运行
    pause
    exit /b 1
)

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] 检查环境...
python --version
echo.

REM 进入后端目录
cd /d "%~dp0backend"
if errorlevel 1 (
    echo [错误] 无法进入backend目录
    pause
    exit /b 1
)

echo [2/5] 安装打包依赖...
pip install pyinstaller
if errorlevel 1 (
    echo [错误] PyInstaller安装失败
    pause
    exit /b 1
)

echo.
echo [3/5] 开始打包...
pyinstaller --clean build.spec
if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo [4/5] 准备发布包...
cd /d "%~dp0"
if not exist "dist" mkdir "dist"

REM 创建发布目录
set "RELEASE_NAME=FinDataHub_v1.0.0_Windows"
set "RELEASE_DIR=dist\%RELEASE_NAME%"
if exist "%RELEASE_DIR%" rmdir /s /q "%RELEASE_DIR%"
mkdir "%RELEASE_DIR%"

REM 复制可执行文件
copy "backend\dist\FinDataHub.exe" "%RELEASE_DIR%\" >nul

REM 创建README
(
echo FinDataHub - 金融数据管理系统
echo ===============================
echo.
echo 版本: 1.0.0
echo 适用系统: Windows 10/11 (32位/64位)
echo.
echo 使用说明
echo --------
echo 1. 解压本压缩包到任意文件夹
echo 2. 双击运行 FinDataHub.exe
echo 3. 等待程序自动打开浏览器（或手动访问 http://127.0.0.1:5001）
echo.
echo 注意事项
echo --------
echo - 首次运行会自动创建数据库文件
echo - 数据库文件会保存在程序运行目录下
echo - 请确保程序有读写权限
echo - 如需退出程序，请在命令行窗口按 Ctrl+C
echo.
echo 技术支持
echo --------
echo 如有问题，请查看控制台输出信息
) > "%RELEASE_DIR%\README.txt"

REM 创建启动脚本
(
echo @echo off
echo title FinDataHub
echo echo 正在启动 FinDataHub...
echo echo.
echo echo 请勿关闭此窗口！
echo echo.
echo echo 程序将自动打开浏览器...
echo echo.
echo FinDataHub.exe
echo pause
) > "%RELEASE_DIR%\启动.bat"

echo.
echo [5/5] 创建压缩包...
cd dist
if exist "%RELEASE_NAME%.zip" del "%RELEASE_NAME%.zip"
powershell -Command "Compress-Archive -Path '%RELEASE_NAME%' -DestinationPath '%RELEASE_NAME%.zip' -Force"

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 发布包位置: %~dp0dist\%RELEASE_NAME%.zip
echo.
echo 发布包内容:
echo - FinDataHub.exe (主程序)
echo - README.txt (使用说明)
echo - 启动.bat (启动脚本)
echo.
pause

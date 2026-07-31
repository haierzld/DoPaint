@echo off
chcp 65001 >nul
title DoPaint - 儿童画作动画生成器

echo.
echo ╔══════════════════════════════════════════╗
echo ║     🎨 DoPaint - 儿童画作动画生成器      ║
echo ║           一键本地启动                    ║
echo ╚══════════════════════════════════════════╝
echo.

cd /d "%~dp0"

:: ========================================
:: 1. 检查 Python
:: ========================================
echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo        下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

:: ========================================
:: 2. 创建 & 激活虚拟环境
:: ========================================
echo [2/4] 准备虚拟环境...
if not exist "venv\" (
    echo        首次运行，正在创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo        虚拟环境创建完成
) else (
    echo        虚拟环境已存在，跳过创建
)

call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)
echo.

:: ========================================
:: 3. 安装依赖
:: ========================================
echo [3/4] 检查依赖...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo        正在安装依赖包，请稍候...
    pip install -r requirements.txt -q
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查 requirements.txt
        pause
        exit /b 1
    )
    echo        依赖安装完成
) else (
    echo        依赖已安装，跳过
)
echo.

:: ========================================
:: 4. 启动服务
:: ========================================
echo [4/4] 启动 DoPaint 服务...
echo.
echo ┌────────────────────────────────────────┐
echo │  前端地址: http://localhost:8000/app/   │
echo │  API文档:  http://localhost:8000/docs   │
echo │  按 Ctrl+C 停止服务                     │
echo └────────────────────────────────────────┘
echo.

:: 自动打开浏览器
start "" http://localhost:8000/app/

:: 启动 uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

:: 如果服务停止，回到虚拟环境外
call venv\Scripts\deactivate.bat >nul 2>&1
pause

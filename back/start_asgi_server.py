#!/usr/bin/env python3
"""
ASGI服务器启动脚本
用于启动同时提供Django API和WebSocket服务的ASGI应用程序
"""

import os
import sys
import argparse
import subprocess


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="启动ASGI服务器（Django API + WebSocket）"
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="服务器监听地址 (默认: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="服务器监听端口 (默认: 8000)"
    )
    parser.add_argument("--workers", type=int, default=1, help="工作进程数 (默认: 1)")
    parser.add_argument(
        "--reload", action="store_true", help="启用自动重载（开发模式）"
    )
    args = parser.parse_args()

    # 检查uvicorn是否安装
    try:
        import uvicorn
    except ImportError:
        print("错误: 缺少uvicorn库，请运行: pip install uvicorn")
        sys.exit(1)

    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ASGI应用文件路径
    asgi_file = os.path.join(script_dir, "asgi.py")

    # 启动命令
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "asgi:asgi_app",
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--workers",
        str(args.workers),
    ]

    # 开发模式下启用自动重载
    if args.reload:
        cmd.append("--reload")

    print(f"正在启动ASGI服务器，地址: {args.host}:{args.port}")
    print(f"Django API地址: http://{args.host}:{args.port}/api/")
    print(f"WebSocket地址: ws://{args.host}:{args.port}/ws/")
    print(f"测试页面: {os.path.join(script_dir, 'websocket_client.html')}")
    print("按Ctrl+C停止服务器")

    try:
        # 启动服务器
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("服务器已停止")


if __name__ == "__main__":
    main()

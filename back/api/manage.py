
#!/usr/bin/env python
"""Django的命令行工具，用于管理项目。"""
import os
import sys


def main():
    """运行管理任务。"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入Django。您确定安装了Django并且"
            "在您的PYTHONPATH环境变量中可用吗？您是否"
            "忘记激活虚拟环境？"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

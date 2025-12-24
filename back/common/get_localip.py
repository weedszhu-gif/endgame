import socket
import os


def get_localip_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("114.114.114.114", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def get_localip_env():
    return os.environ.get("EXTERNAL_HOST_IP")


def get_localip():
    # 检查是否存在环境变量中的本地IP地址
    if get_localip_env():
        # 如果环境变量中存在本地IP地址，则返回该IP地址
        return get_localip_env()
    else:
        # 如果环境变量中不存在本地IP地址，则通过socket获取本地IP地址
        return get_localip_socket()


if __name__ == "__main__":
    print(get_localip())

from common.get_root import get_root_path
import yaml
import platform


def get_config():
    root_path = get_root_path()
    # 检测操作系统
    if platform.system() == "Darwin":
        # 如果是macOS，使用dev配置文件
        config_file = "config_dev.yaml"
    else:
        # 否则，使用默认的配置文件
        config_file = "config_prod.yaml"
    config = yaml.load(open(root_path + "/" + config_file), Loader=yaml.FullLoader)
    return config

from pathlib import Path

import yaml

"""
______________________________
  Author: wen_l
   Time : 2025-11-01
______________________________
"""
class Config:
    """配置管理器，读取config.yaml并提供全局访问"""
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 加载配置文件
            config_path = Path(__file__).parent / "config.yaml"
            if not config_path.exists():
                raise FileNotFoundError(f"配置文件不存在：{config_path}")
            with open(config_path, "r", encoding="utf-8") as f:
                cls._config = yaml.safe_load(f)
        return cls._instance

    def get(self, key, default=None):
        """获取配置项（支持嵌套，如'mysql.host'）"""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


# 全局配置实例
config = Config()

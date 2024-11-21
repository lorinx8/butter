import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
import yaml
import sys
from urllib.parse import urlparse


def load_yaml_config():
    """Load YAML configuration based on environment"""
    env = os.getenv("ENV", "local")
    config_file = f"config.{env}.yaml"

    # First check if config file exists
    if not Path(config_file).exists():
        # If not, copy from template
        template_file = "config.template.yaml"
        if Path(template_file).exists():
            import shutil
            shutil.copy(template_file, config_file)
        else:
            raise FileNotFoundError(
                f"Neither {config_file} nor {template_file} found")

    # Load and return config
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def get_yaml_value(config: dict, *keys, default='') -> str:
    """安全获取嵌套的yaml配置"""
    current = config
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current if current is not None else default


def safe_int(value: str, default: int) -> int:
    """安全转换整数，失败时返回默认值"""
    try:
        return int(value) if value else default
    except (ValueError, TypeError):
        return default


def safe_float(value: str, default: float) -> float:
    """安全转换浮点数，失败时返回默认值"""
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default


class Settings(BaseSettings):
    # Load YAML config
    _yaml_config: dict = load_yaml_config()

    # App Settings
    PROJECT_NAME: str = get_yaml_value(_yaml_config, 'app', 'name')

    # API Settings
    APP_API_V1_STR: str = get_yaml_value(
        _yaml_config, 'app', 'api_prefixs', 'app')
    ADMIN_API_V1_STR: str = get_yaml_value(
        _yaml_config, 'app', 'api_prefixs', 'admin')
    COMMON_API_V1_STR: str = get_yaml_value(
        _yaml_config, 'app', 'api_prefixs', 'common')

    # JWT Settings
    SECRET_KEY: str = get_yaml_value(_yaml_config, 'jwt', 'secret_key')
    ALGORITHM: str = get_yaml_value(_yaml_config, 'jwt', 'algorithm')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = safe_int(
        get_yaml_value(_yaml_config, 'jwt', 'access_token_expire_minutes'), 30)

    # Database Settings
    POSTGRES_SERVER: str = get_yaml_value(_yaml_config, 'database', 'host')
    POSTGRES_USER: str = get_yaml_value(_yaml_config, 'database', 'user')
    POSTGRES_PASSWORD: str = get_yaml_value(
        _yaml_config, 'database', 'password')
    POSTGRES_DB: str = get_yaml_value(_yaml_config, 'database', 'database')
    POSTGRES_PORT: str = str(
        safe_int(get_yaml_value(_yaml_config, 'database', 'port'), 5432))

    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = get_yaml_value(
        _yaml_config, 'openai', 'api_key')
    OPENAI_BASE_URL: Optional[str] = get_yaml_value(
        _yaml_config, 'openai', 'base_url')
    OPENAI_MODEL: str = get_yaml_value(_yaml_config, 'openai', 'model')
    OPENAI_TEMPERATURE: float = safe_float(
        get_yaml_value(_yaml_config, 'openai', 'temperature'), 0.0)
    OPENAI_MAX_TOKENS: int = safe_int(get_yaml_value(
        _yaml_config, 'openai', 'max_tokens'), 16000)
    OPENAI_MAX_RETRIES: int = safe_int(get_yaml_value(
        _yaml_config, 'openai', 'max_retries'), 2)

    @property
    def DATABASE_URL(self) -> str:
        """获取数据库URL"""
        # 优先使用环境变量
        env_db_url = os.getenv("DATABASE_URL")
        if env_db_url:
            return env_db_url

        # 否则使用配置拼接
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_PSYCOPG(self) -> str:
        """获取psycopg专用的数据库URL"""
        env_db_url = os.getenv("DATABASE_URL")
        if env_db_url:
            # 替换协议部分
            return env_db_url.replace("postgresql://", "postgresql+psycopg://", 1)

        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URI(self) -> str:
        """兼容性别名,与 DATABASE_URL 相同"""
        return self.DATABASE_URL

    def validate_database_url(self) -> bool:
        """验证数据库连接字符串是否完整有效"""
        # 检查环境变量
        env_db_url = os.getenv("DATABASE_URL", "").strip()
        if env_db_url:
            try:
                url = urlparse(env_db_url)
                # 检查URL的各个组件是否都存在且非空
                return all([
                    url.scheme,
                    url.hostname,
                    url.username,
                    url.password,
                    url.path.lstrip('/'),
                    url.port
                ])
            except Exception:
                return False

        # 检查配置文件中的数据库配置
        required_fields = {
            'host': self.POSTGRES_SERVER,
            'user': self.POSTGRES_USER,
            'password': self.POSTGRES_PASSWORD,
            'database': self.POSTGRES_DB,
            'port': self.POSTGRES_PORT
        }

        # 检查所有字段是否都存在且非空
        return all(str(value).strip() for value in required_fields.values())

    def check_database_config(self):
        """检查数据库配置，如果无效则终止程序"""
        if not self.validate_database_url():
            print("\n错误: 数据库配置无效!", file=sys.stderr)

            # 检查环境变量
            env_db_url = os.getenv("DATABASE_URL", "").strip()
            if env_db_url:
                print("\nDATABASE_URL 环境变量无效:", file=sys.stderr)
                print(f"当前值: {env_db_url}", file=sys.stderr)
                print("格式要求: postgresql://user:pass@host:port/db", file=sys.stderr)
            else:
                print("\n当前配置值:", file=sys.stderr)
                print(
                    f"database.host: '{self.POSTGRES_SERVER}'", file=sys.stderr)
                print(
                    f"database.user: '{self.POSTGRES_USER}'", file=sys.stderr)
                print(
                    f"database.password: {'[已设置]' if self.POSTGRES_PASSWORD else '[未设置]'}", file=sys.stderr)
                print(
                    f"database.database: '{self.POSTGRES_DB}'", file=sys.stderr)
                print(
                    f"database.port: '{self.POSTGRES_PORT}'", file=sys.stderr)

            print("\n需要满足以下条件之一:", file=sys.stderr)
            print("1. 设置有效的 DATABASE_URL 环境变量，包含所有必需的连接信息", file=sys.stderr)
            print("2. 在配置文件中提供所有必需的数据库配置项，且值不能为空", file=sys.stderr)
            sys.exit(1)

    class Config:
        env_file = f".env.{os.getenv('ENV', 'local')}"


settings = Settings()

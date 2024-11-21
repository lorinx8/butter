import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
import yaml


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


class Settings(BaseSettings):
    # Load YAML config
    _yaml_config = load_yaml_config()

    # 安全获取嵌套的yaml配置
    def _get_yaml_value(self, *keys, default='') -> str:
        current = self._yaml_config
        for key in keys:
            if not isinstance(current, dict):
                return default
            current = current.get(key, default)
        return current if current is not None else default

    PROJECT_NAME: str = _get_yaml_value('app', 'name')

    # API Settings
    APP_API_V1_STR: str = _get_yaml_value('app', 'api_prefixs', 'app')
    ADMIN_API_V1_STR: str = _get_yaml_value('app', 'api_prefixs', 'admin')
    COMMON_API_V1_STR: str = _get_yaml_value('app', 'api_prefixs', 'common')

    # JWT Settings
    SECRET_KEY: str = _get_yaml_value('jwt', 'secret_key')
    ALGORITHM: str = _get_yaml_value('jwt', 'algorithm')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        _get_yaml_value('jwt', 'access_token_expire_minutes', '30'))

    # Database Settings
    POSTGRES_SERVER: str = _get_yaml_value('database', 'host')
    POSTGRES_USER: str = _get_yaml_value('database', 'user')
    POSTGRES_PASSWORD: str = _get_yaml_value('database', 'password')
    POSTGRES_DB: str = _get_yaml_value('database', 'database')
    POSTGRES_PORT: str = str(_get_yaml_value('database', 'port', '5432'))

    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = _get_yaml_value('openai', 'api_key')
    OPENAI_BASE_URL: Optional[str] = _get_yaml_value('openai', 'base_url')
    OPENAI_MODEL: str = _get_yaml_value('openai', 'model')
    OPENAI_TEMPERATURE: float = float(
        _get_yaml_value('openai', 'temperature', '0'))
    OPENAI_MAX_TOKENS: int = int(
        _get_yaml_value('openai', 'max_tokens', '16000'))
    OPENAI_MAX_RETRIES: int = int(
        _get_yaml_value('openai', 'max_retries', '2'))

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

    class Config:
        env_file = f".env.{os.getenv('ENV', 'local')}"


settings = Settings()

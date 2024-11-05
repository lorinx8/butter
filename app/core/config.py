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
            raise FileNotFoundError(f"Neither {config_file} nor {template_file} found")
    
    # Load and return config
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

class Settings(BaseSettings):
    # Load YAML config
    _yaml_config = load_yaml_config()
    
    # API Settings
    API_V1_STR: str = _yaml_config['app']['api_prefix']
    PROJECT_NAME: str = _yaml_config['app']['name']
    
    # JWT Settings
    SECRET_KEY: str = _yaml_config['jwt']['secret_key']
    ALGORITHM: str = _yaml_config['jwt']['algorithm']
    ACCESS_TOKEN_EXPIRE_MINUTES: int = _yaml_config['jwt']['access_token_expire_minutes']
    
    # Database Settings
    POSTGRES_SERVER: str = _yaml_config['database']['host']
    POSTGRES_USER: str = _yaml_config['database']['user']
    POSTGRES_PASSWORD: str = _yaml_config['database']['password']
    POSTGRES_DB: str = _yaml_config['database']['database']
    POSTGRES_PORT: str = str(_yaml_config['database']['port'])

    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = _yaml_config['openai']['api_key']
    OPENAI_BASE_URL: Optional[str] = _yaml_config['openai']['base_url']
    OPENAI_MODEL: str = _yaml_config['openai']['model']
    OPENAI_TEMPERATURE: float = _yaml_config['openai']['temperature']
    OPENAI_MAX_TOKENS: int = _yaml_config['openai']['max_tokens']
    OPENAI_MAX_RETRIES: int = _yaml_config['openai']['max_retries']

    @property
    def DATABASE_URL_PSYCOPG(self) -> str:
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}?sslmode=disable"

    class Config:
        env_file = f".env.{os.getenv('ENV', 'local')}"

settings = Settings() 
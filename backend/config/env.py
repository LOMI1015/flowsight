import argparse
import os
import sys
from dotenv import load_dotenv
from functools import lru_cache
from pydantic import computed_field
from pydantic_settings import BaseSettings
from typing import Literal


class AppSettings(BaseSettings):
    """
    应用配置
    """

    app_env: str = 'dev'
    app_name: str = 'art-work'
    app_root_path: str = '/dev-api'
    app_host: str = '0.0.0.0'
    app_port: int = 9099
    app_version: str = '1.0.0'
    app_reload: bool = True
    app_ip_location_query: bool = True
    app_same_time_login: bool = True


class JwtSettings(BaseSettings):
    """
    Jwt配置
    """

    jwt_secret_key: str = 'b01c66dc2c58dc6a0aabfe2144256be36226de378bf87f72c0c795dda67f4d55'
    jwt_algorithm: str = 'HS256'
    jwt_expire_minutes: int = 1440
    jwt_redis_expire_minutes: int = 30


class DataBaseSettings(BaseSettings):
    """
    数据库配置
    """

    db_type: Literal['mysql', 'postgresql'] = 'postgresql'
    db_host: str = '127.0.0.1'
    db_port: int = 3306
    db_username: str = 'root'
    db_password: str = 'root'
    db_database: str
    db_echo: bool = False
    db_max_overflow: int = 10
    db_pool_size: int = 50
    db_pool_recycle: int = 3600
    db_pool_timeout: int = 30

    @computed_field
    @property
    def sqlglot_parse_dialect(self) -> str:
        if self.db_type == 'postgresql':
            return 'postgres'
        return self.db_type


class TaskDataBaseSettings(BaseSettings):
    """
    定时任务数据存储数据库配置（默认 PostgreSQL）
    """

    task_db_type: Literal['postgresql'] = 'postgresql'
    task_db_host: str = '127.0.0.1'
    task_db_port: int = 5432
    task_db_username: str = 'postgres'
    task_db_password: str = 'postgres'
    task_db_database: str = 'task-data'
    task_db_echo: bool = False
    task_db_max_overflow: int = 10
    task_db_pool_size: int = 20
    task_db_pool_recycle: int = 3600
    task_db_pool_timeout: int = 30


class AdminSettings(BaseSettings):
    """
    超级管理员配置
    """

    app_super_account: str = 'admin'
    admin_nick_name: str = '超级管理员'
    app_super_password: str = 'admin123'
    admin_email: str = 'admin@example.com'
    admin_phonenumber: str = '15888888888'
    admin_sex: str = '0'  # 0男 1女 2未知
    admin_dept_id: int = 103  # 默认部门ID
    admin_role_id: int = 1  # 管理员角色ID


class RedisSettings(BaseSettings):
    """
    Redis配置
    """

    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    redis_username: str = ''
    redis_password: str = ''
    redis_database: int = 2


class MinioSettings(BaseSettings):
    """
    Minio配置
    """

    minio_host: str = '127.0.0.1'
    minio_port: int = 9000
    minio_access_key: str = 'minioadmin'
    minio_secret_key: str = 'minioadmin'
    minio_secure: bool = False
    minio_bucket: str = 'artwork'

class CrmTokenSettings(BaseSettings):
    """
    CRM token配置
    """
    crm_token_url: str
    crm_token_username: str
    crm_token_safetymark: str
    crm_token_clientid: str
    crm_token_secretkey: str
    crm_token_orgid: str

class GenSettings:
    """
    代码生成配置
    """

    author = 'insistence'
    package_name = 'module_admin.system'
    auto_remove_pre = False
    table_prefix = 'sys_'
    allow_overwrite = False

    GEN_PATH = 'vf_admin/gen_path'

    def __init__(self):
        if not os.path.exists(self.GEN_PATH):
            os.makedirs(self.GEN_PATH)


class UploadSettings:
    """
    上传配置
    """

    UPLOAD_PREFIX = '/profile'
    UPLOAD_PATH = 'vf_admin/upload_path'
    UPLOAD_MACHINE = 'A'
    DEFAULT_ALLOWED_EXTENSION = [
        # 图片
        'bmp',
        'gif',
        'jpg',
        'jpeg',
        'png',
        # word excel powerpoint
        'doc',
        'docx',
        'xls',
        'xlsx',
        'ppt',
        'pptx',
        'html',
        'htm',
        'txt',
        # 压缩文件
        'rar',
        'zip',
        'gz',
        'bz2',
        # 视频格式
        'mp4',
        'avi',
        'rmvb',
        # pdf
        'pdf',
    ]
    DOWNLOAD_PATH = 'vf_admin/download_path'

    def __init__(self):
        if not os.path.exists(self.UPLOAD_PATH):
            os.makedirs(self.UPLOAD_PATH)
        if not os.path.exists(self.DOWNLOAD_PATH):
            os.makedirs(self.DOWNLOAD_PATH)


class CachePathConfig:
    """
    缓存目录配置
    """

    PATH = os.path.join(os.path.abspath(os.getcwd()), 'caches')
    PATHSTR = 'caches'

class HttpSettings(BaseSettings):
    """
    HTTP配置
    """
    http_timeout: int = 30
    http_retries: int = 3


class GetConfig:
    """
    获取配置
    """

    def __init__(self):
        self.parse_cli_args()

    @lru_cache()
    def get_app_config(self):
        """
        获取应用配置
        """
        # 实例化应用配置模型
        return AppSettings()

    @lru_cache()
    def get_jwt_config(self):
        """
        获取Jwt配置
        """
        # 实例化Jwt配置模型
        return JwtSettings()

    @lru_cache()
    def get_database_config(self):
        """
        获取数据库配置
        """
        # 实例化数据库配置模型
        return DataBaseSettings()

    @lru_cache()
    def get_task_database_config(self):
        """
        获取定时任务数据数据库配置
        """
        return TaskDataBaseSettings()

    @lru_cache()
    def get_admin_config(self):
        """
        获取超级管理员配置
        """
        # 实例化超级管理员配置模型
        return AdminSettings()

    @lru_cache()
    def get_redis_config(self):
        """
        获取Redis配置
        """
        # 实例化Redis配置模型
        return RedisSettings()

    @lru_cache()
    def get_minio_config(self):
        """
        获取Minio配置
        """
        # 实例化Minio配置模型
        return MinioSettings()

    @lru_cache()
    def get_crm_token_config(self):
        """
        获取CRM token配置
        """
        # 实例化CRM token配置模型
        return CrmTokenSettings()

    @lru_cache()
    def get_gen_config(self):
        """
        获取代码生成配置
        """
        # 实例化代码生成配置
        return GenSettings()

    @lru_cache()
    def get_upload_config(self):
        """
        获取数据库配置
        """
        # 实例上传配置
        return UploadSettings()

    @lru_cache()
    def get_http_config(self):
        """
        获取HTTP配置
        """
        # 实例化HTTP配置模型
        return HttpSettings()

    @staticmethod
    def parse_cli_args():
        """
        解析命令行参数
        """
        if 'uvicorn' in sys.argv[0]:
            # 使用uvicorn启动时，命令行参数需要按照uvicorn的文档进行配置，无法自定义参数
            pass
        else:
            # 使用argparse定义命令行参数
            parser = argparse.ArgumentParser(description='命令行参数')
            parser.add_argument('--env', type=str, default='', help='运行环境')
            # 解析命令行参数
            args = parser.parse_args()
            # 设置环境变量，如果未设置命令行参数，默认APP_ENV为dev
            os.environ['APP_ENV'] = args.env if args.env else 'dev'
        # 读取运行环境
        run_env = os.environ.get('APP_ENV', '')
        # 运行环境未指定时默认加载.env.dev
        env_file = '.env.dev'
        # 运行环境不为空时按命令行参数加载对应.env文件
        if run_env != '':
            env_file = f'.env.{run_env}'
        # 加载配置
        load_dotenv(env_file)


# 实例化获取配置类
get_config = GetConfig()
# 应用配置
AppConfig = get_config.get_app_config()
# Jwt配置
JwtConfig = get_config.get_jwt_config()
# 数据库配置
DataBaseConfig = get_config.get_database_config()
# 定时任务数据数据库配置
TaskDataBaseConfig = get_config.get_task_database_config()
# 超级管理员配置
AdminConfig = get_config.get_admin_config()
# Redis配置
RedisConfig = get_config.get_redis_config()
# Minio配置
MinioConfig = get_config.get_minio_config()
# CRM token配置
CrmTokenConfig = get_config.get_crm_token_config()
# 代码生成配置
GenConfig = get_config.get_gen_config()
# 上传配置
UploadConfig = get_config.get_upload_config()
# HTTP配置
HttpConfig = get_config.get_http_config()
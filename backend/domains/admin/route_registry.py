from typing import List
from domains.types import RouteConfig
from module_admin.controller.cache_controller import cacheController
from module_admin.controller.captcha_controller import captchaController
from module_admin.controller.common_controller import commonController
from module_admin.controller.config_controller import configController
from module_admin.controller.dept_controller import deptController
from module_admin.controller.dict_controller import dictController
from module_admin.controller.log_controller import logController
from module_admin.controller.login_controller import loginController
from module_admin.controller.job_controller import jobController
from module_admin.controller.menu_controller import menuController
from module_admin.controller.notice_controller import noticeController
from module_admin.controller.online_controller import onlineController
from module_admin.controller.post_controler import postController
from module_admin.controller.role_controller import roleController
from module_admin.controller.server_controller import serverController
from module_admin.controller.user_controller import userController

API_V1_ADMIN_PREFIX = '/api/v1/admin'


def get_admin_routes() -> List[RouteConfig]:
    return [
        {'router': loginController, 'tags': ['登录模块'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': captchaController, 'tags': ['验证码模块'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': userController, 'tags': ['系统管理-用户管理'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': roleController, 'tags': ['系统管理-角色管理'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': menuController, 'tags': ['系统管理-菜单管理'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': deptController, 'tags': ['系统管理-部门管理'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': postController, 'tags': ['系统管理-岗位管理'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': dictController, 'tags': ['系统管理-字典管理'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': configController, 'tags': ['系统管理-参数管理'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': noticeController, 'tags': ['系统管理-通知公告管理'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': logController, 'tags': ['系统管理-日志管理'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': onlineController, 'tags': ['系统监控-在线用户'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': jobController, 'tags': ['系统监控-定时任务'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': serverController, 'tags': ['系统监控-菜单管理'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': cacheController, 'tags': ['系统监控-缓存监控'], 'prefix': API_V1_ADMIN_PREFIX},
        {'router': commonController, 'tags': ['通用模块'], 'prefix': API_V1_ADMIN_PREFIX},
    ]

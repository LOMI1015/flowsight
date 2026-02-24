from fastapi import APIRouter, Depends, Request
from module_bi.entity.vo.console_vo import ConsoleDataModel, ChartDataModel
from domains.bi.application.services import ConsoleService, LoginService
from utils.response_util import ResponseUtil
from utils.log_util import logger


consoleController = APIRouter(prefix='/data', dependencies=[Depends(LoginService.get_current_user)])


@consoleController.get(
    '/console',
    response_model=ConsoleDataModel,
    # 临时注释权限检查，用于测试
    # dependencies=[Depends(CheckUserInterfaceAuth('data:console:list'))]
)
async def get_console_data(request: Request):
    """
    获取工作台数据接口

    :param request: Request对象
    :return: 工作台数据
    """
    # 调用服务层获取数据
    console_data = await ConsoleService.get_console_data()

    # 将 Pydantic 模型转换为字典，确保使用别名（驼峰命名）
    data_dict = console_data.model_dump(by_alias=True)

    logger.info('获取工作台数据成功')

    return ResponseUtil.success(data=data_dict)


@consoleController.get(
    '/console/chart',
    response_model=ChartDataModel,
    # 临时注释权限检查，用于测试
    # dependencies=[Depends(CheckUserInterfaceAuth('data:console:chart'))]
)
async def get_chart_data(request: Request):
    """
    获取折线图数据接口（最近12天）

    :param request: Request对象
    :return: 折线图数据
    """
    # 调用服务层获取数据
    chart_data = await ConsoleService.get_chart_data()

    # 将 Pydantic 模型转换为字典，确保使用别名（驼峰命名）
    data_dict = chart_data.model_dump(by_alias=True)

    logger.info('获取折线图数据成功')

    return ResponseUtil.success(data=data_dict)


from __future__ import annotations

from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List


class ConsoleDataModel(BaseModel):
    """
    工作台数据模型
    """

    model_config = ConfigDict(from_attributes=True)

    date: Optional[datetime] = Field(default=None, description='日期', alias='date')
    robot_count: Optional[int] = Field(default=None, description='机器人会话数', alias='robot_count')
    agent_count: Optional[int] = Field(default=None, description='c端会话数', alias='agent_count')
    robot_rate: Optional[float] = Field(default=None, description='机器人会话率', alias='robot_rate')
    b_agent_count: Optional[int] = Field(default=None, description='B端客服数', alias='B_agent_count')
    create_return_count: Optional[int] = Field(default=None, description='创建退货工单数', alias='create_return_count')
    create_complain_count: Optional[int] = Field(default=None, description='创建投诉工单数', alias='create_complain_count')
    create_one_line_count: Optional[int] = Field(default=None, description='创建一线未解决', alias='create_one_line_count')
    create_two_line_count: Optional[int] = Field(default=None, description='创建二线未解决', alias='create_two_line_count')
    create_b_line_count: Optional[int] = Field(default=None, description='创建B端未解决', alias='create_B_line_count')
    approve_return_count: Optional[int] = Field(default=None, description='审批退货工单数', alias='approve_return_count')
    approve_complain_count: Optional[int] = Field(default=None, description='审批投诉工单数', alias='approve_complain_count')
    approve_one_line_count: Optional[int] = Field(default=None, description='审批一线未解决数', alias='approve_one_line_count')
    approve_two_line_count: Optional[int] = Field(default=None, description='审批二线未解决数', alias='approve_two_line_count')
    approve_b_line_count: Optional[int] = Field(default=None, description='审批B端未解决数', alias='approve_B_line_count')
    return_24_count: Optional[int] = Field(default=None, description='24小时退货数', alias='return_24_count')
    return_24_rate: Optional[float] = Field(default=None, description='24小时退货率', alias='return_24_rate')
    call_out_count: Optional[int] = Field(default=None, description='外呼预览数', alias='call_out_count')
    call_in_count: Optional[int] = Field(default=None, description='热线呼入数', alias='call_in_count')
    chat_5eval_count: Optional[int] = Field(default=None, description='聊天5星评价数', alias='chat_5eval_count')
    call_5eval_count: Optional[int] = Field(default=None, description='电话5星评价数', alias='call_5eval_count')
    chat_eval_count: Optional[int] = Field(default=None, description='聊天评价数', alias='chat_eval_count')
    call_eval_count: Optional[int] = Field(default=None, description='电话评价数', alias='call_eval_count')


class ChartDataItem(BaseModel):
    """
    折线图单日数据项
    """
    model_config = ConfigDict(from_attributes=True)

    date: Optional[datetime] = Field(description='日期', alias='date')
    robot_count: int = Field(default=0, description='机器人会话数', alias='robot_count')
    agent_count: int = Field(default=0, description='客服会话数', alias='agent_count')
    call_out_count: int = Field(default=0, description='外呼预览数', alias='call_out_count')
    call_in_count: int = Field(default=0, description='热线呼入数', alias='call_in_count')
    create_return_count: int = Field(default=0, description='创建退货工单数', alias='create_return_count')
    create_complain_count: int = Field(default=0, description='创建投诉工单数', alias='create_complain_count')
    create_one_line_count: int = Field(default=0, description='创建一线未解决', alias='create_one_line_count')
    create_two_line_count: int = Field(default=0, description='创建二线未解决', alias='create_two_line_count')
    create_b_line_count: int = Field(default=0, description='创建B端未解决', alias='create_B_line_count')
    approve_return_count: int = Field(default=0, description='审批退货工单数', alias='approve_return_count')
    approve_complain_count: int = Field(default=0, description='审批投诉工单数', alias='approve_complain_count')


class ChartDataModel(BaseModel):
    """
    折线图数据模型
    """
    model_config = ConfigDict(from_attributes=True)

    dates: List[str] = Field(description='日期列表（横轴）', alias='dates')
    data: List[ChartDataItem] = Field(description='数据列表', alias='data')

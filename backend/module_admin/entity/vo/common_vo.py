from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from typing import Any, Optional
from module_admin.annotation.pydantic_annotation import as_query


class CrudResponseModel(BaseModel):
    """
    操作响应模型
    """

    is_success: bool = Field(description='操作是否成功')
    message: str = Field(description='响应信息')
    result: Optional[Any] = Field(default=None, description='响应结果')


class UploadResponseModel(BaseModel):
    """
    上传响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    file_name: Optional[str] = Field(default=None, description='新文件映射路径')
    new_file_name: Optional[str] = Field(default=None, description='新文件名称')
    original_filename: Optional[str] = Field(default=None, description='原文件名称')
    url: Optional[str] = Field(default=None, description='新文件url')


class UploadRecordModel(BaseModel):
    """
    上传记录模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='唯一标识')
    upload_starttime: Optional[datetime] = Field(default=None, description='开始上传时间')
    upload_endtime: Optional[datetime] = Field(default=None, description='上传结束时间')
    upload_userid: Optional[int] = Field(default=None, description='上传用户id')
    upload_status: Optional[int] = Field(default=None, description='上传状态（0失败 1成功）')
    original_filename: Optional[str] = Field(default=None, description='原始文件名')
    new_file_name: Optional[str] = Field(default=None, description='新文件名')
    file_path: Optional[str] = Field(default=None, description='文件路径')
    file_size: Optional[int] = Field(default=None, description='文件大小（字节）')
    file_url: Optional[str] = Field(default=None, description='文件访问URL')
    # 关联用户信息
    user_name: Optional[str] = Field(default=None, description='上传者用户名')
    nick_name: Optional[str] = Field(default=None, description='上传者昵称')


@as_query
class UploadRecordPageQueryModel(BaseModel):
    """
    上传记录分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
    original_filename: Optional[str] = Field(default=None, description='原始文件名（模糊查询）')
    upload_userid: Optional[int] = Field(default=None, description='上传用户id')
    upload_status: Optional[int] = Field(default=None, description='上传状态（0失败 1成功）')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')

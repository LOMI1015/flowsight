from datetime import datetime
from sqlalchemy import Column, DateTime, BigInteger, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base


class SysUpload(Base):
    """
    文件上传记录表
    """

    __tablename__ = 'sys_upload'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='唯一标识')
    upload_starttime = Column(DateTime, comment='开始上传时间')
    upload_endtime = Column(DateTime, comment='上传结束时间')
    upload_userid = Column(Integer, ForeignKey('sys_user.user_id'), comment='上传用户id')
    upload_status = Column(Integer, default=1, comment='上传状态（0失败 1成功）')
    original_filename = Column(Text, comment='原始文件名')
    new_file_name = Column(Text, comment='新文件名（服务器存储的文件名）')
    file_path = Column(Text, comment='文件路径（相对路径）')
    file_size = Column(BigInteger, comment='文件大小（字节）')
    file_url = Column(Text, comment='文件访问URL')

    # 关联用户表（可选，如果需要关联查询）
    # user = relationship('SysUser', backref='uploads')


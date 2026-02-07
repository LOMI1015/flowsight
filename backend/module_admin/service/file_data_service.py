import logging
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from utils.file_process_util import FileProcessUtil
from fastapi import UploadFile
from io import BytesIO
from config.env import DataBaseConfig

logger = logging.getLogger(__name__)


class FileDataService:
    """
    文件数据处理服务层
    用于处理上传的文件数据并插入数据库
    """

    @classmethod
    async def process_and_insert_data(
        cls,
        db: AsyncSession,
        file: UploadFile,
        table_name: str,
        column_mapping: Optional[Dict[str, str]] = None,
        batch_size: int = 1000,
        schema_name: Optional[str] = None,
        only_mapped_columns: bool = True,
    ) -> Dict[str, Any]:
        """
        处理文件数据并插入到数据库

        :param db: 数据库会话
        :param file: 上传的文件对象
        :param table_name: 目标数据库表名
        :param column_mapping: 列名映射字典，将 Excel 列名映射到数据库字段名
        :param batch_size: 批量插入的大小
        :param schema_name: 数据库 schema 名称（可选，默认为 None，PostgreSQL 中 None 表示使用默认 schema，通常是 public）
        :param only_mapped_columns: 是否只插入已映射的列（默认 True），如果为 False，则插入所有列
        :return: 处理结果字典，包含成功数量、失败数量等信息
        """
        try:
            # 读取并处理文件
            data_list = await FileProcessUtil.process_upload_file(file, column_mapping)
            
            # 如果只插入已映射的列，过滤数据
            if only_mapped_columns and column_mapping:
                # 获取映射后的列名（数据库字段名）
                mapped_columns = set(column_mapping.values())
                # 过滤数据，只保留已映射的列
                filtered_data_list = []
                for row in data_list:
                    filtered_row = {k: v for k, v in row.items() if k in mapped_columns}
                    filtered_data_list.append(filtered_row)
                data_list = filtered_data_list

            if not data_list:
                return {
                    'success': False,
                    'message': '文件中没有有效数据',
                    'total': 0,
                    'success_count': 0,
                    'fail_count': 0,
                    'errors': [],
                }

            # 批量插入数据
            success_count = 0
            fail_count = 0
            errors = []

            # 分批处理数据
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i : i + batch_size]
                try:
                    await cls._batch_insert_data(db, batch, table_name, schema_name)
                    success_count += len(batch)
                except Exception as e:
                    logger.error(f'批量插入数据失败: {str(e)}')
                    fail_count += len(batch)
                    errors.append(f'第 {i + 1}-{min(i + batch_size, len(data_list))} 行: {str(e)}')

            # 提交事务
            await db.commit()

            return {
                'success': True,
                'message': f'成功处理 {success_count} 条数据，失败 {fail_count} 条',
                'total': len(data_list),
                'success_count': success_count,
                'fail_count': fail_count,
                'errors': errors,
            }

        except Exception as e:
            await db.rollback()
            logger.error(f'处理文件数据失败: {str(e)}')
            raise Exception(f'处理文件数据失败: {str(e)}')

    @classmethod
    async def _batch_insert_data(
        cls, db: AsyncSession, data_list: List[Dict[str, Any]], table_name: str, schema_name: Optional[str] = None
    ):
        """
        批量插入数据到数据库

        :param db: 数据库会话
        :param data_list: 数据列表
        :param table_name: 目标表名
        :param schema_name: 数据库 schema 名称（可选，PostgreSQL 中用于指定 schema）
        """
        if not data_list:
            return

        # 获取第一条数据的键作为列名
        columns = list(data_list[0].keys())

        # 构建列名到参数名的映射（处理特殊字符）
        # PostgreSQL 参数名不能包含点号等特殊字符，需要替换
        column_to_param = {}
        param_columns = []
        for col in columns:
            # 将列名中的特殊字符替换为下划线，用于参数名
            # 但保留原始列名用于 SQL 中的列名
            param_name = col.replace('.', '_').replace(' ', '_').replace('-', '_')
            # 确保参数名唯一
            if param_name in column_to_param.values():
                counter = 1
                original_param_name = param_name
                while param_name in column_to_param.values():
                    param_name = f'{original_param_name}_{counter}'
                    counter += 1
            column_to_param[col] = param_name
            param_columns.append(param_name)

        # 构建插入 SQL
        # 使用参数化查询防止 SQL 注入
        # PostgreSQL 使用双引号包裹表名和列名
        columns_str = ', '.join([f'"{col}"' for col in columns])
        placeholders = ', '.join([f':{param_name}' for param_name in param_columns])

        # 构建完整的表名（包含 schema）
        # 如果指定了 schema，格式为 "schema_name"."table_name"
        # 如果没有指定 schema，只使用表名（PostgreSQL 默认使用 search_path 中的 schema，通常是 public）
        if schema_name:
            full_table_name = f'"{schema_name}"."{table_name}"'
        else:
            full_table_name = f'"{table_name}"'

        # 使用 text() 构建 SQL，表名需要通过参数传入（但这里我们直接使用，因为表名是配置的）
        # 注意：在生产环境中，应该验证表名和 schema 名是否合法
        sql = text(f'INSERT INTO {full_table_name} ({columns_str}) VALUES ({placeholders})')

        # 准备数据，将 None 值转换为 NULL，空字符串也转换为 None
        # 同时将列名转换为参数名
        prepared_data = []
        for row in data_list:
            prepared_row = {}
            for col in columns:
                param_name = column_to_param[col]
                value = row.get(col)
                # 处理 None 值和空字符串
                if value is None or value == '':
                    prepared_row[param_name] = None
                else:
                    prepared_row[param_name] = value
            prepared_data.append(prepared_row)

        # 执行批量插入
        # 使用循环插入方式，对于大数据量可以考虑优化为批量插入
        # 注意：SQLAlchemy 的 text() 执行批量插入时，需要循环执行
        for row_data in prepared_data:
            await db.execute(sql, row_data)

    @classmethod
    async def process_file_with_custom_logic(
        cls,
        db: AsyncSession,
        file: UploadFile,
        column_mapping: Optional[Dict[str, str]] = None,
        data_processor: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        使用自定义逻辑处理文件数据

        :param db: 数据库会话
        :param file: 上传的文件对象
        :param column_mapping: 列名映射字典
        :param data_processor: 自定义数据处理函数，接收 (db, data_list) 参数
        :return: 处理结果
        """
        try:
            # 读取并处理文件
            data_list = await FileProcessUtil.process_upload_file(file, column_mapping)

            if not data_list:
                return {
                    'success': False,
                    'message': '文件中没有有效数据',
                    'total': 0,
                    'success_count': 0,
                    'fail_count': 0,
                }

            # 如果提供了自定义处理函数，使用它
            if data_processor:
                result = await data_processor(db, data_list)
                await db.commit()
                return result
            else:
                # 默认处理：直接返回数据列表
                return {
                    'success': True,
                    'message': f'成功读取 {len(data_list)} 条数据',
                    'total': len(data_list),
                    'data': data_list,
                }

        except Exception as e:
            await db.rollback()
            logger.error(f'处理文件数据失败: {str(e)}')
            raise Exception(f'处理文件数据失败: {str(e)}')

    @classmethod
    async def process_file_from_path(
        cls,
        db: AsyncSession,
        file_path: str,
        file_name: str,
        table_name: str,
        column_mapping: Optional[Dict[str, str]] = None,
        batch_size: int = 1000,
        schema_name: Optional[str] = None,
        only_mapped_columns: bool = True,
    ) -> Dict[str, Any]:
        """
        从文件路径读取文件并处理数据插入到数据库

        :param db: 数据库会话
        :param file_path: 文件路径
        :param file_name: 文件名
        :param table_name: 目标数据库表名
        :param column_mapping: 列名映射字典，将 Excel 列名映射到数据库字段名
        :param batch_size: 批量插入的大小
        :param schema_name: 数据库 schema 名称（可选，PostgreSQL 中用于指定 schema）
        :param only_mapped_columns: 是否只插入已映射的列（默认 True）
        :return: 处理结果字典
        """
        try:
            # 读取文件内容
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # 创建临时 UploadFile 对象
            temp_file = UploadFile(
                filename=file_name,
                file=BytesIO(file_content)
            )

            # 调用处理函数
            return await cls.process_and_insert_data(
                db=db,
                file=temp_file,
                table_name=table_name,
                column_mapping=column_mapping,
                batch_size=batch_size,
                schema_name=schema_name,
                only_mapped_columns=only_mapped_columns,
            )

        except Exception as e:
            await db.rollback()
            logger.error(f'从文件路径处理数据失败: {str(e)}')
            raise Exception(f'从文件路径处理数据失败: {str(e)}')


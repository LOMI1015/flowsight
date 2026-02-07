import io
import pandas as pd
from typing import List, Dict, Any, Optional
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)


class FileProcessUtil:
    """
    文件处理工具类
    用于读取和处理 Excel/CSV 文件
    """

    @classmethod
    async def read_file_to_dataframe(cls, file: UploadFile) -> pd.DataFrame:
        """
        读取上传的文件并转换为 DataFrame

        :param file: 上传的文件对象
        :return: pandas DataFrame
        """
        try:
            # 读取文件内容
            contents = await file.read()
            file_extension = file.filename.rsplit('.', 1)[-1].lower() if file.filename else ''

            # 根据文件类型读取
            if file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(io.BytesIO(contents), engine='openpyxl' if file_extension == 'xlsx' else 'xlrd')
            elif file_extension == 'csv':
                # 尝试不同的编码格式
                try:
                    df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        df = pd.read_csv(io.BytesIO(contents), encoding='gbk')
                    except UnicodeDecodeError:
                        df = pd.read_csv(io.BytesIO(contents), encoding='gb2312')
            else:
                raise ValueError(f'不支持的文件类型: {file_extension}')

            return df

        except Exception as e:
            logger.error(f'读取文件失败: {str(e)}')
            raise Exception(f'读取文件失败: {str(e)}')

    @classmethod
    def clean_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        清理 DataFrame 数据
        - 删除空行
        - 去除前后空格
        - 处理空值

        :param df: 原始 DataFrame
        :return: 清理后的 DataFrame
        """
        # 删除完全为空的行
        df = df.dropna(how='all')

        # 去除字符串列的前后空格
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
                # 将 'nan' 字符串替换为空字符串
                df[col] = df[col].replace('nan', '')

        return df

    @classmethod
    def dataframe_to_dict_list(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        将 DataFrame 转换为字典列表

        :param df: pandas DataFrame
        :return: 字典列表
        """
        # 清理数据
        df = cls.clean_dataframe(df)

        # 转换为字典列表，NaN 值转换为 None
        data_list = df.replace({pd.NA: None, pd.NaT: None}).to_dict('records')

        return data_list

    @classmethod
    async def process_upload_file(
        cls, file: UploadFile, column_mapping: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        处理上传的文件，返回处理后的数据列表

        :param file: 上传的文件对象
        :param column_mapping: 列名映射字典，用于将 Excel 列名映射到数据库字段名
        :return: 处理后的数据列表
        """
        # 读取文件
        df = await cls.read_file_to_dataframe(file)

        # 如果提供了列名映射，则重命名列
        if column_mapping:
            df.rename(columns=column_mapping, inplace=True)

        # 转换为字典列表
        data_list = cls.dataframe_to_dict_list(df)

        return data_list


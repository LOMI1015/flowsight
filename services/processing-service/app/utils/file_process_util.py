import pandas as pd
from typing import Dict, Any, List


class FileProcessUtil:
    @staticmethod
    def read_file_to_dataframe(file_path: str) -> pd.DataFrame:
        file_extension = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else ''
        if file_extension in ['xlsx', 'xls']:
            return pd.read_excel(file_path, engine='openpyxl' if file_extension == 'xlsx' else 'xlrd')
        if file_extension == 'csv':
            try:
                return pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    return pd.read_csv(file_path, encoding='gbk')
                except UnicodeDecodeError:
                    return pd.read_csv(file_path, encoding='gb2312')
        raise ValueError(f'unsupported file extension: {file_extension}')

    @classmethod
    def process_file(cls, file_path: str, column_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        df = cls.read_file_to_dataframe(file_path)
        df = df.dropna(how='all')
        if column_mapping:
            df.rename(columns=column_mapping, inplace=True)
            mapped_columns = set(column_mapping.values())
            filtered = []
            for row in df.to_dict('records'):
                filtered.append({k: v for k, v in row.items() if k in mapped_columns})
            return filtered
        return df.to_dict('records')

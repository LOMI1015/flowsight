# -*- coding: utf-8 -*-
"""
@author: peng
@file: ctx.py
@time: 2025/1/17  16:57
"""

import contextvars
from urllib.parse import parse_qs
from uuid import uuid4

CTX_REQUEST_ID: contextvars.ContextVar[str] = contextvars.ContextVar('request-id', default='')
CTX_USER_ID: contextvars.ContextVar[str] = contextvars.ContextVar('user-id', default='-')
CTX_DATASET_ID: contextvars.ContextVar[str] = contextvars.ContextVar('dataset-id', default='-')


class TraceCtx:
    @staticmethod
    def set_id():
        _id = uuid4().hex
        CTX_REQUEST_ID.set(_id)
        return _id

    @staticmethod
    def get_id():
        return CTX_REQUEST_ID.get()

    @staticmethod
    def set_user_id(user_id: str):
        value = '-' if user_id is None else str(user_id)
        CTX_USER_ID.set(value)
        return value

    @staticmethod
    def get_user_id():
        return CTX_USER_ID.get()

    @staticmethod
    def set_dataset_id(dataset_id: str):
        value = '-' if dataset_id is None else str(dataset_id)
        CTX_DATASET_ID.set(value)
        return value

    @staticmethod
    def get_dataset_id():
        return CTX_DATASET_ID.get()

    @classmethod
    def init_request_context(cls, scope: dict):
        """
        请求开始时初始化上下文字段，优先从header读取dataset_id，其次query参数。
        """
        cls.set_id()
        cls.set_user_id('-')
        cls.set_dataset_id('-')

        headers = {k.decode('latin-1').lower(): v.decode('latin-1') for k, v in scope.get('headers', [])}
        dataset_id = headers.get('x-dataset-id')
        if not dataset_id:
            query_string = scope.get('query_string', b'').decode('utf-8')
            dataset_id = parse_qs(query_string).get('dataset_id', [None])[0]
        if dataset_id:
            cls.set_dataset_id(dataset_id)

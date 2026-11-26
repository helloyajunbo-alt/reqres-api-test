"""
全局夹具：会话、接口地址、令牌的一次性获取与跨用例复用。

要点：
1. client 用 session 作用域，整轮只建一条连接池，避免每条用例重复握手；
2. token 用 session 作用域，登录一次全局复用，这是接口测试里最典型的 fixture 用法；
3. 接口地址从环境变量读取，改测试环境不需要改代码。
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.client import ReqResClient

BASE_URL = os.getenv('REQRES_BASE_URL', 'https://reqres.in/api')
VALID_EMAIL = os.getenv('REQRES_EMAIL', 'eve.holt@reqres.in')
VALID_PASSWORD = os.getenv('REQRES_PASSWORD', 'cityslicka')


@pytest.fixture(scope='session')
def client():
    return ReqResClient(BASE_URL)


@pytest.fixture(scope='session')
def token(client):
    """登录一次，取回令牌，整轮复用。"""
    resp = client.login({'email': VALID_EMAIL, 'password': VALID_PASSWORD})
    assert resp.status_code == 200, '前置失败：无法取得令牌，状态码 {}'.format(resp.status_code)
    return resp.json()['token']


@pytest.fixture(scope='session')
def authed_client(client, token):
    """已注入令牌的客户端，供需要鉴权的用例使用。"""
    client.set_token(token)
    yield client
    client.clear_token()

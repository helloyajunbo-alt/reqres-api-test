"""
接口层封装：只负责发请求，不做断言。

设计说明：
1. 用例层不直接写 requests.xxx，统一走这一层，接口地址或参数变化时只改这里。
2. 所有方法返回原始 Response 对象，断言交给用例层，避免"封装里已经判断过"导致用例看不出测了什么。
3. session 复用连接，token 通过 set_token 统一注入，不在每个方法里单独传头。
"""
import os
import time

import requests


class ReqResClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        # 公共演示环境有条数/频率限制，命中 429 时按 Retry-After 退避重试，避免误判为功能缺陷
        self.max_retries = 3
        api_key = os.getenv('REQRES_API_KEY')
        if api_key:
            self.session.headers.update({'x-api-key': api_key})

    def set_token(self, token: str):
        """设置 Bearer 令牌，集合级统一注入，后续所有请求继承。"""
        self.session.headers.update({'Authorization': 'Bearer {}'.format(token)})

    def clear_token(self):
        self.session.headers.pop('Authorization', None)

    def _url(self, path: str) -> str:
        return '{}{}'.format(self.base_url, path)

    def _send(self, method: str, path: str, **kwargs):
        """统一出口：限流退避、日志留痕都收敛在这里，用例层无需关心。"""
        url = self._url(path)
        resp = None
        for attempt in range(self.max_retries):
            resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
            if resp.status_code != 429:
                return resp
            wait = int(resp.headers.get('Retry-After', 2 * (attempt + 1)))
            time.sleep(min(wait, 10))
        return resp

    # ---------- 登录 ----------
    def login(self, payload: dict):
        return self._send('POST', '/login', json=payload)

    # ---------- 用户查询 ----------
    def list_users(self, page: int = 1, per_page: int = None):
        params = {'page': page}
        if per_page is not None:
            params['per_page'] = per_page
        return self._send('GET', '/users', params=params)

    def get_user(self, user_id):
        return self._send('GET', '/users/{}'.format(user_id))

    # ---------- 用户增改删 ----------
    def create_user(self, payload: dict):
        return self._send('POST', '/users', json=payload)

    def update_user(self, user_id, payload: dict):
        return self._send('PUT', '/users/{}'.format(user_id), json=payload)

    def patch_user(self, user_id, payload: dict):
        return self._send('PATCH', '/users/{}'.format(user_id), json=payload)

    def delete_user(self, user_id):
        return self._send('DELETE', '/users/{}'.format(user_id))

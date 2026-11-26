"""鉴权模块：RQ-14 ~ RQ-15（两条均为已知缺陷，用 xfail 锁定）"""
import os

import pytest

from api.client import ReqResClient

BASE_URL = os.getenv('REQRES_BASE_URL', 'https://reqres.in/api')


@pytest.mark.xfail(strict=True, reason='已知缺陷 D-03：未携带令牌仍返回 200 与完整用户数据，鉴权未拦截')
def test_rq14_access_without_token():
    """RQ-14 不携带 token 访问用户详情：预期 401，实际 200（缺陷 D-03）。

    xfail 不是放弃验证，而是把缺陷钉住：缺陷修好后这条会自动变红，提醒更新用例与缺陷单。
    """
    anonymous = ReqResClient(BASE_URL)
    resp = anonymous.get_user(2)

    assert resp.status_code == 401, '未鉴权请求返回了 {}，存在越权风险'.format(resp.status_code)


def test_rq15_access_with_tampered_token():
    """RQ-15 使用篡改的 token 访问：401，令牌被拒绝。

    与 RQ-14 形成对照：带非法令牌会被拒绝，缺令牌却直接放行，
    说明鉴权链条只校验了"令牌是否合法"，没有校验"是否必须携带"，这才是 D-03 的准确描述。
    """
    anonymous = ReqResClient(BASE_URL)
    anonymous.set_token('tampered-token-12345')
    resp = anonymous.get_user(2)

    assert resp.status_code == 401, '伪造令牌被接受，返回 {}'.format(resp.status_code)
    assert 'data' not in resp.json(), '401 场景仍返回了业务数据'
    anonymous.clear_token()

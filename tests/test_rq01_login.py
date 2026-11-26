"""登录模块：RQ-01 ~ RQ-03"""
import pytest
from jsonschema import validate

from schemas.contracts import LOGIN_OK


@pytest.mark.smoke
def test_rq01_login_success(client):
    """RQ-01 正确账号密码登录：返回 200 与可用 token。"""
    resp = client.login({'email': 'eve.holt@reqres.in', 'password': 'cityslicka'})

    # 通信层：状态码
    assert resp.status_code == 200, resp.text
    # 结构层：响应体符合登录契约
    body = resp.json()
    validate(instance=body, schema=LOGIN_OK)
    # 语义层：令牌可直接用于后续请求，而不是只有字段非空
    assert isinstance(body['token'], str) and body['token'].strip(), '令牌为空'


def test_rq02_login_missing_email(client):
    """RQ-02 缺少邮箱字段：返回 400 与明确错误提示，不返回令牌。"""
    resp = client.login({'password': 'cityslicka'})

    assert resp.status_code == 400, '实际 {}'.format(resp.status_code)
    body = resp.json()
    assert 'error' in body, '缺少 error 字段，前端无法提示具体原因'
    assert 'email' in body['error'].lower(), '错误提示未指明缺失字段：{}'.format(body['error'])
    assert 'token' not in body, '异常场景返回了令牌'


@pytest.mark.xfail(strict=True, reason='已知缺陷 D-01：密码错误仍返回 200 并下发令牌，未做口令校验')
def test_rq03_login_wrong_password(client):
    """RQ-03 密码错误：预期 400，实际返回 200 与 token（缺陷 D-01）。"""
    resp = client.login({'email': 'eve.holt@reqres.in', 'password': 'definitely_wrong'})

    assert resp.status_code == 400, '错误密码登录成功了，返回 {}'.format(resp.status_code)

"""用户详情模块：RQ-07 ~ RQ-08"""
import pytest
from jsonschema import validate

from schemas.contracts import USER_DETAIL


@pytest.mark.smoke
def test_rq07_get_existing_user(client):
    """RQ-07 查询存在的用户：200，返回 id 与请求一致，字段符合契约。"""
    user_id = 2
    resp = client.get_user(user_id)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    validate(instance=body, schema=USER_DETAIL)

    # 语义层：返回的 id 必须等于请求的 id，这是接口关联最关键的一条
    assert body['data']['id'] == user_id, '返回 id 与请求不一致'
    assert '@' in body['data']['email'], '邮箱格式异常'


def test_rq08_get_nonexistent_user(client):
    """RQ-08 查询不存在的用户：404，响应体为空对象，不返回脏数据。"""
    resp = client.get_user(9999)

    assert resp.status_code == 404, '实际 {}'.format(resp.status_code)
    assert resp.json() == {}, '404 场景返回了响应体，可能泄露内部信息'

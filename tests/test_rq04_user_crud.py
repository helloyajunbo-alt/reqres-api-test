"""用户增改删模块：RQ-09 ~ RQ-13（含数据驱动的创建用例）"""
import json
import os

import pytest
from jsonschema import validate

from schemas.contracts import USER_CREATE, USER_UPDATE

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'users.json')


def load_create_cases():
    with open(DATA_FILE, encoding='utf-8') as f:
        return json.load(f)


@pytest.mark.smoke
@pytest.mark.parametrize('payload', load_create_cases(), ids=lambda p: p['name'][:20])
def test_rq09_create_user(client, payload):
    """RQ-09 创建用户：201，返回 id 与创建时间，请求字段原样回显。

    数据驱动：正常值、中文、单字符、超长字符串四组数据共用一条用例脚本。
    """
    resp = client.create_user({'name': payload['name'], 'job': payload['job']})

    assert resp.status_code == payload['expect_status'], resp.text
    body = resp.json()
    validate(instance=body, schema=USER_CREATE)

    # 语义层：回显字段必须与请求一致，否则前端展示会用错数据
    assert body['name'] == payload['name'], 'name 回显与请求不一致'
    assert body['job'] == payload['job'], 'job 回显与请求不一致'


@pytest.mark.xfail(strict=True, reason='已知缺陷 D-02：创建接口未校验必填字段，缺 name 仍返回 201 并生成 id')
def test_rq10_create_user_missing_name(client):
    """RQ-10 创建用户缺必填字段：预期 400 参数校验失败，实际 201（缺陷 D-02）。"""
    resp = client.create_user({'job': 'QA'})

    assert resp.status_code == 400, '必填字段缺失仍创建成功，返回 {}'.format(resp.status_code)


def test_rq11_update_user_put(client):
    """RQ-11 全量更新用户：200，返回更新后的字段与 updatedAt。"""
    payload = {'name': 'junbo', 'job': 'QA Engineer'}
    resp = client.update_user(2, payload)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    validate(instance=body, schema=USER_UPDATE)

    assert body['name'] == payload['name'], 'PUT 未覆盖 name'
    assert body['job'] == payload['job'], 'PUT 未覆盖 job'


@pytest.mark.regression
def test_rq12_partial_update_user_patch(client):
    """RQ-12 局部更新用户：200，目标字段被正确接收，返回更新时间。"""
    resp = client.patch_user(2, {'job': 'Senior QA'})

    assert resp.status_code == 200, resp.text
    body = resp.json()
    # 该服务只回显本次提交的字段；未提交的 name 不参与覆盖，属于响应结构约定，
    # 与"局部更新是否只改目标字段"是两件事，因此这里只校验目标字段被正确接收。
    assert body['job'] == 'Senior QA', 'PATCH 未更新目标字段'
    assert 'updatedAt' in body, 'PATCH 响应缺少 updatedAt 字段'


def test_rq13_delete_user(client):
    """RQ-13 删除用户：204，无响应体。"""
    resp = client.delete_user(2)

    assert resp.status_code == 204, '实际 {}'.format(resp.status_code)
    assert resp.text == '', '204 响应体应为空，实际返回了 {}'.format(resp.text)

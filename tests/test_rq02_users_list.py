"""用户列表模块：RQ-04 ~ RQ-06（含分页边界）"""
import pytest
from jsonschema import validate

from schemas.contracts import USER_LIST


@pytest.mark.smoke
def test_rq04_user_list_first_page(client):
    """RQ-04 分页查询第一页：结构完整、数据非空、页码与请求一致。"""
    resp = client.list_users(page=1)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    validate(instance=body, schema=USER_LIST)

    # 语义层：返回的页码必须与请求页码一致，而不是"随便返回一页"
    assert body['page'] == 1
    assert len(body['data']) > 0, '第一页数据为空'
    assert len(body['data']) <= body['per_page'], '单页数据条数超过 per_page'
    # 语义层：总页数与总条数自洽
    expected_pages = -(-body['total'] // body['per_page'])  # 向上取整
    assert body['total_pages'] == expected_pages, '总页数与总条数不匹配'


def test_rq05_user_list_out_of_range_page(client):
    """RQ-05 页码越界（末页 + 1）：返回 200 与空数组，不报错、不返回上一页数据。"""
    last_page_resp = client.list_users(page=1)
    total_pages = last_page_resp.json()['total_pages']

    resp = client.list_users(page=total_pages + 1)

    assert resp.status_code == 200, '越界页码不应报错，实际 {}'.format(resp.status_code)
    body = resp.json()
    assert body['data'] == [], '越界页返回了数据，说明分页逻辑有误'
    assert body['page'] == total_pages + 1


@pytest.mark.regression
def test_rq06_user_list_per_page(client):
    """RQ-06 per_page 参数生效：返回条数等于 per_page，且 total_pages 同步变化。"""
    per_page = 3
    resp = client.list_users(page=1, per_page=per_page)

    assert resp.status_code == 200
    body = resp.json()
    validate(instance=body, schema=USER_LIST)

    assert body['per_page'] == per_page, 'per_page 未生效'
    assert len(body['data']) <= per_page, '返回条数超过 per_page'
    expected_pages = -(-body['total'] // per_page)
    assert body['total_pages'] == expected_pages

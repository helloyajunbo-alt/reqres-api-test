"""非功能观察：RQ-16 响应时间基线

说明：这不是性能测试，只做单请求响应时间的可用性观察，为后续引入 JMeter 做并发压测留一个对照基线。
"""
import os

import pytest

from api.client import ReqResClient

BASE_URL = os.getenv('REQRES_BASE_URL', 'https://reqres.in/api')
THRESHOLD_MS = 3000  # 基线：公共模拟服务单请求 3 秒内必须返回


@pytest.mark.regression
def test_rq16_response_time_baseline():
    """RQ-16 核心接口响应时间基线：登录与列表均在阈值内返回。"""
    c = ReqResClient(BASE_URL)

    login_resp = c.login({'email': 'eve.holt@reqres.in', 'password': 'cityslicka'})
    login_ms = login_resp.elapsed.total_seconds() * 1000
    assert login_resp.status_code == 200
    assert login_ms < THRESHOLD_MS, '登录接口耗时 {:.0f}ms，超过基线 {}ms'.format(login_ms, THRESHOLD_MS)

    list_resp = c.list_users(page=1)
    list_ms = list_resp.elapsed.total_seconds() * 1000
    assert list_resp.status_code == 200
    assert list_ms < THRESHOLD_MS, '列表接口耗时 {:.0f}ms，超过基线 {}ms'.format(list_ms, THRESHOLD_MS)

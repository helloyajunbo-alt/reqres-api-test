"""
本地 Mock 服务：用于在无网络或公共演示环境配额耗尽时自检框架与用例逻辑。

注意：它不是被测系统，只是保证"框架能跑通"的本地替身。
真实验证请把 REQRES_BASE_URL 指回官方地址（默认值即为官方）。

启动：python3 mock_server.py
用法：REQRES_BASE_URL=http://127.0.0.1:8765/api python3 -m pytest -q
"""
import json
import re
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

TOTAL = 12
ISSUED = set()


def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def user_item(i):
    return {
        'id': i,
        'email': 'user{}@reqres.in'.format(i),
        'first_name': 'First{}'.format(i),
        'last_name': 'Last{}'.format(i),
        'avatar': 'https://reqres.in/img/faces/{}-image.jpg'.format(i),
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _json(self, code, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get('Content-Length') or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode('utf-8'))
        except Exception:
            return {}

    def _authorized(self):
        auth = self.headers.get('Authorization')
        if not auth:
            return True  # 复刻官方行为：未携带令牌不拦截（已知缺陷 D-03）
        token = auth.replace('Bearer', '').strip()
        return token in ISSUED

    def _route(self, method):
        path = urlparse(self.path)
        route = path.path.replace('/api', '', 1)

        if route == '/login' and method == 'POST':
            data = self._body()
            if not data.get('email'):
                return self._json(400, {'error': 'Missing email or username'})
            token = uuid.uuid4().hex
            ISSUED.add(token)
            # 复刻官方行为：不校验密码（已知缺陷 D-01）
            return self._json(200, {'token': token})

        if not self._authorized():
            return self._json(401, {'error': 'invalid_token'})

        if route == '/users' and method == 'GET':
            q = parse_qs(path.query)
            page = int(q.get('page', ['1'])[0])
            per_page = int(q.get('per_page', ['6'])[0])
            start = (page - 1) * per_page
            items = [user_item(i) for i in range(1, TOTAL + 1)][start:start + per_page]
            total_pages = -(-TOTAL // per_page)
            return self._json(200, {
                'page': page, 'per_page': per_page,
                'total': TOTAL, 'total_pages': total_pages,
                'data': items,
            })

        m = re.match(r'/users/(\d+)$', route)
        if m and method == 'GET':
            uid = int(m.group(1))
            if 1 <= uid <= TOTAL:
                return self._json(200, {'data': user_item(uid)})
            return self._json(404, {})

        if route == '/users' and method == 'POST':
            data = self._body()
            # 复刻官方行为：不校验必填字段（已知缺陷 D-02）
            payload = dict(data)
            payload.update({'id': str(400 + len(ISSUED)), 'createdAt': now()})
            return self._json(201, payload)

        if m and method in ('PUT', 'PATCH'):
            data = self._body()
            payload = dict(data)
            payload['updatedAt'] = now()
            return self._json(200, payload)

        if m and method == 'DELETE':
            self.send_response(204)
            self.send_header('Content-Length', '0')
            self.end_headers()
            return None

        return self._json(404, {})

    def do_GET(self):
        self._route('GET')

    def do_POST(self):
        self._route('POST')

    def do_PUT(self):
        self._route('PUT')

    def do_PATCH(self):
        self._route('PATCH')

    def do_DELETE(self):
        self._route('DELETE')


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 8765), Handler)
    print('mock server on http://127.0.0.1:8765/api')
    server.serve_forever()

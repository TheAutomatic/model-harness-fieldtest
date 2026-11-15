"""Host-side offline checks. Do not expose this directory to candidates."""
import argparse
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def redirect_checks(workspace):
    sys.path.insert(0, str(workspace))
    import requests

    cases = [
        ('303_then_307', 'POST', [303, 307], ['POST', 'GET', 'GET'], True),
        ('302_then_307', 'POST', [302, 307], ['POST', 'GET', 'GET'], False),
        ('301_then_307', 'POST', [301, 307], ['POST', 'GET', 'GET'], False),
        ('direct_307', 'POST', [307], ['POST', 'POST'], False),
        ('head_chain', 'HEAD', [303, 307], ['HEAD', 'HEAD', 'HEAD'], False),
        ('get_chain', 'GET', [303, 307], ['GET', 'GET', 'GET'], False),
        ('auth_cross_host', 'GET', [307, 307], ['GET', 'GET', 'GET'], True),
    ]
    results = []
    for name, method, codes, expected, cross_host in cases:
        seen = []

        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.0'

            def handle_request(self):
                body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
                seen.append({'method': self.command, 'path': self.path,
                             'body': body.decode('ascii'),
                             'auth': self.headers.get('Authorization')})
                hop = len(seen) - 1
                self.send_response(codes[hop] if hop < len(codes) else 200)
                if hop < len(codes):
                    if cross_host and hop == 0:
                        location = 'http://localhost:%s/hop1' % self.server.server_port
                    else:
                        location = '/hop%s' % (hop + 1)
                    self.send_header('Location', location)
                self.send_header('Content-Length', '0')
                self.end_headers()

            do_POST = do_GET = do_HEAD = handle_request

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.01}, daemon=True)
        thread.start()
        error = None
        try:
            with requests.Session() as session:
                session.trust_env = False
                session.request(method, 'http://127.0.0.1:%s/start' % server.server_port,
                                data='payload' if method == 'POST' else None,
                                headers={'Authorization': 'Bearer offline-test'},
                                allow_redirects=True, timeout=3)
        except Exception as exc:
            error = repr(exc)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        methods_ok = [x['method'] for x in seen] == expected
        bodies_ok = bool(seen) and all(
            x['body'] == ('payload' if wanted == 'POST' else '')
            for x, wanted in zip(seen, expected))
        auth_ok = bool(seen) and all(
            x['auth'] == (None if cross_host and i else 'Bearer offline-test')
            for i, x in enumerate(seen))
        results.append({'case': name, 'pass': error is None and methods_ok and bodies_ok and auth_ok,
                        'seen': seen, 'error': error})
    return results


def brute(a, m):
    total = 0
    for left in range(len(a)):
        subtotal = 0
        for value in a[left:]:
            subtotal += value
            total += subtotal % m
    return total


def algorithm_checks(workspace):
    entry = workspace / 'main.py'
    if not entry.is_file():
        return [{'case': 'delivery', 'pass': False, 'error': 'main.py missing'}]
    cases = [('sample1', [2, 5, 0], 4, 10),
             ('sample2', [320, 578, 244, 604, 145, 839, 156, 857, 556, 400], 100, 2736)]
    for name, a, m in [('single_zero', [0], 1), ('single_large', [10**9], 199999),
                       ('equal_prefixes', [4, 0, 8, 0, 12], 4),
                       ('wraparound', [6, 6, 1, 6, 0], 7),
                       ('no_outer_mod', [1] * 30, 200000)]:
        cases.append((name, a, m, brute(a, m)))
    rng = random.Random(20261104)
    for i in range(32):
        a = [rng.randrange(10**9 + 1) for _ in range(rng.randrange(1, 24))]
        m = rng.randrange(1, 32)
        cases.append(('small_%02d' % i, a, m, brute(a, m)))
    for name, n, value, m in [('max_ones', 200000, 1, 200000),
                               ('max_large_values', 200000, 10**9, 199999)]:
        expected = sum((n - length + 1) * ((length * value) % m)
                       for length in range(1, n + 1))
        cases.append((name, [value] * n, m, expected))
    results = []
    env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
    for name, a, m, expected in cases:
        data = '%s %s\n%s\n' % (len(a), m, ' '.join(map(str, a)))
        start = time.perf_counter()
        try:
            proc = subprocess.run([sys.executable, '-B', str(entry)], cwd=workspace,
                                  input=data, text=True, capture_output=True, timeout=15, env=env)
            answer = proc.stdout.strip()
            ok = proc.returncode == 0 and answer == str(expected)
            results.append({'case': name, 'pass': ok, 'seconds': round(time.perf_counter()-start, 3),
                            'expected': expected, 'actual': answer[:200],
                            'error': proc.stderr[-500:] if proc.returncode else None})
        except subprocess.TimeoutExpired:
            results.append({'case': name, 'pass': False, 'error': '15 second timeout'})
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('task', choices=['B', 'C'])
    parser.add_argument('workspace', type=Path)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        parser.error('workspace is not a directory')
    results = redirect_checks(workspace) if args.task == 'B' else algorithm_checks(workspace)
    report = {'task': args.task, 'workspace': str(workspace), 'passed': sum(x['pass'] for x in results),
              'total': len(results), 'all_passed': all(x['pass'] for x in results), 'checks': results}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['all_passed'] else 1


if __name__ == '__main__':
    sys.exit(main())

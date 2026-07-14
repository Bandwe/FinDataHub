#!/usr/bin/env python3
"""Launch a desktop build and verify its embedded web application."""
import argparse
import json
import os
import platform
import re
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


def normalize_arch(value):
    aliases = {
        'amd64': 'x86_64',
        'x64': 'x86_64',
        'x86_64': 'x86_64',
        'aarch64': 'arm64',
        'arm64': 'arm64',
    }
    normalized = aliases.get(value.strip().lower())
    if not normalized:
        raise ValueError(f'Unsupported architecture: {value}')
    return normalized


def available_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def fetch(url, timeout=2):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.status, response.read()


def wait_until_ready(process, base_url, timeout):
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False, f'process exited with code {process.returncode}'
        try:
            status, body = fetch(f'{base_url}/health')
            payload = json.loads(body.decode('utf-8'))
            if status == 200 and payload.get('status') == 'ok':
                return True, None
        except (OSError, ValueError, urllib.error.URLError) as exc:
            last_error = exc
        time.sleep(0.5)
    return False, f'timed out waiting for health endpoint: {last_error}'


def verify_web_app(base_url):
    status, html_bytes = fetch(f'{base_url}/')
    html = html_bytes.decode('utf-8')
    if status != 200 or '<div id="app"></div>' not in html:
        raise RuntimeError('desktop home page did not return the frontend shell')

    asset_match = re.search(r'<script[^>]+src="([^"]*/assets/[^"]+\.js)"', html)
    if not asset_match:
        raise RuntimeError('desktop home page did not reference a JavaScript asset')

    asset_status, asset_body = fetch(f'{base_url}{asset_match.group(1)}')
    if asset_status != 200 or len(asset_body) < 1000:
        raise RuntimeError('desktop JavaScript asset is missing or unexpectedly small')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--executable', required=True)
    parser.add_argument('--expected-arch', choices=['x86_64', 'arm64'], required=True)
    parser.add_argument('--timeout', type=int, default=90)
    args = parser.parse_args()

    executable = Path(args.executable).resolve()
    if not executable.is_file():
        raise SystemExit(f'Desktop executable not found: {executable}')

    actual_arch = normalize_arch(platform.machine())
    if actual_arch != args.expected_arch:
        raise SystemExit(
            f'Runner architecture mismatch: expected {args.expected_arch}, got {actual_arch}'
        )

    port = available_port()
    base_url = f'http://127.0.0.1:{port}'
    with tempfile.TemporaryDirectory(prefix='findatahub-desktop-') as data_dir:
        env = os.environ.copy()
        env.update({
            'DISABLE_AUTO_OPEN': '1',
            'FINDATA_DATA_DIR': data_dir,
            'FINDATA_HOST': '127.0.0.1',
            'FINDATA_PORT': str(port),
        })
        process = subprocess.Popen(
            [str(executable)],
            cwd=executable.parent,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        started_at = time.monotonic()
        failure = None
        try:
            ready, error = wait_until_ready(process, base_url, args.timeout)
            if not ready:
                failure = error
            else:
                try:
                    verify_web_app(base_url)
                except Exception as exc:
                    failure = str(exc)
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
            output = process.stdout.read() if process.stdout else ''

        if failure:
            details = output[-8000:].strip()
            if details:
                failure = f'{failure}\nDesktop process output:\n{details}'
            raise RuntimeError(failure)

        elapsed = time.monotonic() - started_at
        print(f'Desktop smoke test passed in {elapsed:.1f}s: {base_url} ({actual_arch})')


if __name__ == '__main__':
    main()

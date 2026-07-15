#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""度小满原力 AI 平台 Workflow API 运行器。

用法:
    python run.py run   <agentId> <app_id> <workflow_id> [--params '{"k":"v"}'] [--async]
    python run.py stream <agentId> <app_id> <workflow_id> [--params '{"k":"v"}']
    python run.py init  --agent-id <id> --app-id <id> --workflow-id <id> [--env dev|prod]
    python run.py show
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib import error, request

# ── 环境配置 ─────────────────────────────────────────────────────
ENDPOINTS = {
    'prod': 'https://ai-force.duxiaoman-int.com',
    'dev':  'https://dxm-agent.duxiaoman-int.com',
}
WORKFLOW_RUN_PATH        = '/agent-force-gateway/workflow/run'
WORKFLOW_STREAM_RUN_PATH = '/agent-force-gateway/workflow/stream_run'
GET_TEST_KEY_PATH        = '/agent-force-store/agent/getTestKey'

CONFIG_PATH = Path.home() / '.force-workflow-runner' / 'config.json'
CONFIG_PATH.parent.mkdir(exist_ok=True)
TIMEOUT = 120

LINK_AGENT_RE    = re.compile(r'agentId=(\d{15,})')
LINK_BOT_RE      = re.compile(r'/bot/(\d{15,})')
LINK_APP_ID_RE   = re.compile(r'/project-ide/(\d{15,})')
LINK_WORKFLOW_RE = re.compile(r'/workflow/(\d{15,})')

# config.json 只存非敏感运行时状态
SENSITIVE_KEYS = {'APIKey', 'UUAP_COOKIE'}


# ── 配置读写 ─────────────────────────────────────────────────────

def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {}


def save_config(cfg: dict[str, Any]) -> None:
    persisted = {k: v for k, v in cfg.items() if k not in SENSITIVE_KEYS}
    CONFIG_PATH.write_text(json.dumps(persisted, ensure_ascii=False, indent=2), encoding='utf-8')
    try:
        os.chmod(CONFIG_PATH, 0o600)
    except Exception:
        pass


# ── 链接解析 ─────────────────────────────────────────────────────

def parse_link(url: str) -> dict[str, str]:
    out: dict[str, str] = {}
    if m := LINK_AGENT_RE.search(url):
        out['agentId'] = m.group(1)
    if m := LINK_BOT_RE.search(url):
        out['agentId'] = m.group(1)
    if m := LINK_APP_ID_RE.search(url):
        out['app_id'] = m.group(1)
    if m := LINK_WORKFLOW_RE.search(url):
        out['workflow_id'] = m.group(1)
    if 'dxm-agent.duxiaoman-int.com' in url:
        out['env'] = 'dev'
    elif 'ai-force.duxiaoman-int.com' in url:
        out['env'] = 'prod'
    return out


def resolve_config(
    *,
    link: str | None = None,
    agent_id: str | None = None,
    app_id: str | None = None,
    workflow_id: str | None = None,
    env: str | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    cfg = load_config()
    if link:
        cfg.update(parse_link(link))
    if agent_id:
        cfg['agentId'] = agent_id
    if app_id:
        cfg['app_id'] = app_id
    if workflow_id:
        cfg['workflow_id'] = workflow_id
    if env:
        cfg['env'] = env

    if not cfg.get('env'):
        cfg['env'] = 'prod'
    if not cfg.get('UUAP-ID'):
        if u := os.environ.get('UUAP_ID', '').strip():
            cfg['UUAP-ID'] = u

    if persist:
        save_config(cfg)
    return cfg


def base_url(cfg: dict[str, Any]) -> str:
    return ENDPOINTS.get(cfg.get('env', 'prod'), ENDPOINTS['prod'])


def require(cfg: dict[str, Any], *keys: str) -> None:
    miss = [k for k in keys if not cfg.get(k)]
    if not miss:
        return
    hints = []
    if 'UUAP-ID' in miss:
        hints.append('UUAP-ID 缺失：请确认 ForceClaw 已注入 UUAP_ID 环境变量。')
    if 'agentId' in miss:
        hints.append('agentId 缺失：请通过 --agent-id 或 init 命令设置。')
    if 'app_id' in miss:
        hints.append('app_id 缺失：请通过 --app-id 或 init 命令设置。')
    if 'workflow_id' in miss:
        hints.append('workflow_id 缺失：请通过 --workflow-id 或 init 命令设置。')
    raise SystemExit('配置缺失: ' + ', '.join(miss) + '\n' + '\n'.join(hints))


# ── HTTP ─────────────────────────────────────────────────────────

def http_request(method: str, url: str, headers: dict[str, str],
                 data: dict | None = None, stream: bool = False):
    body = json.dumps(data, ensure_ascii=False).encode('utf-8') if data is not None else None
    req = request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = request.urlopen(req, timeout=TIMEOUT)
    except error.HTTPError as e:
        text = e.read().decode('utf-8', errors='replace')
        raise SystemExit(f'HTTP {e.code} {e.reason}\n{text}')
    except error.URLError as e:
        raise SystemExit(f'网络错误: {e.reason}')
    if stream:
        return resp
    raw = resp.read().decode('utf-8', errors='replace')
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {'_raw': raw}


def check_code(j: dict) -> dict:
    if isinstance(j, dict) and 'code' in j and j['code'] not in (0, '0'):
        msg = j.get('msg') or j.get('message') or ''
        if 'not login' in str(msg).lower() or 'unauthorized' in str(msg).lower() or j.get('redirectUrl'):
            raise SystemExit(
                f'未登录/未授权 (code={j.get("code")})。APIKey 可能已失效，重试即可重新获取。\n'
                f'原始响应: {json.dumps(j, ensure_ascii=False)}'
            )
        raise SystemExit(f'接口错误 code={j.get("code")} msg={msg}\n{json.dumps(j, ensure_ascii=False)}')
    return j


# ── APIKey 实时获取 ───────────────────────────────────────────────

def _do_get_test_key(url: str, cookie: str, agent_id: str) -> str | None:
    """调用 getTestKey（固定 type=1），返回 key 或 None。"""
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Cookie': cookie,
    }
    payload = {'data': {'type': 1, 'agent_id': agent_id}, 'requestId': str(uuid.uuid4()).replace('-', '')}
    j = http_request('POST', url, headers, payload)
    d = j.get('data')
    if isinstance(d, str) and d:
        return d
    if isinstance(d, dict):
        return d.get('api_key') or d.get('apiKey') or d.get('key')
    return j.get('api_key') or j.get('apiKey')


def fetch_apikey(cfg: dict[str, Any]) -> str:
    """每次调用前实时从 getTestKey 接口获取 APIKey，不存盘。

    固定使用 type=1 + app_id。
    """
    cookie = os.environ.get('UUAP_COOKIE', '').strip()
    if not cookie:
        raise SystemExit('获取 APIKey 需要 UUAP_COOKIE 环境变量，请确认 ForceClaw 已注入。')

    app_id = cfg.get('app_id')
    if not app_id:
        raise SystemExit('获取 APIKey 需要 app_id，请先通过 init 或 --app-id 指定。')

    url = base_url(cfg) + GET_TEST_KEY_PATH
    key = _do_get_test_key(url, cookie, app_id)
    if not key:
        raise SystemExit(
            'getTestKey 未获取到 APIKey（type=1 + app_id）。\n'
            '请确认 app_id 正确，或该工作流是否已发布。'
        )
    return key


def with_apikey(cfg: dict[str, Any]) -> dict[str, Any]:
    """返回注入了实时 APIKey 的 cfg 副本，不写盘。"""
    return {**cfg, 'APIKey': fetch_apikey(cfg)}


def api_headers(cfg: dict[str, Any], extra: dict[str, str] | None = None) -> dict[str, str]:
    h = {
        'Authorization': f"Bearer {cfg['APIKey']}",
        'agentId': cfg.get('agentId', ''),
        'UUAP-ID': cfg.get('UUAP-ID', ''),
        'REQUEST-ID': str(uuid.uuid4()),
        'Content-Type': 'application/json',
    }
    if extra:
        h.update(extra)
    return h


# ── SSE 解析 ─────────────────────────────────────────────────────

def parse_sse(resp) -> str:
    """解析流式响应，返回最终输出内容。"""
    result_parts: list[str] = []
    debug_url = ''
    cur_event = ''
    cur_data: list[str] = []

    def flush():
        nonlocal cur_event, cur_data, debug_url
        if not cur_data:
            cur_event = ''
            return
        data_str = '\n'.join(cur_data).strip()
        cur_data = []
        if not data_str:
            cur_event = ''
            return
        try:
            obj = json.loads(data_str)
        except json.JSONDecodeError:
            cur_event = ''
            return
        ev = cur_event
        cur_event = ''

        if ev in ('message', ''):
            # 节点输出，拼接 content
            content = obj.get('content', '')
            if isinstance(content, str) and content:
                # content 可能是 JSON 字符串，尝试解析
                try:
                    inner = json.loads(content)
                    if isinstance(inner, dict):
                        out = inner.get('output') or inner.get('result') or content
                        result_parts.append(str(out))
                    else:
                        result_parts.append(content)
                except json.JSONDecodeError:
                    result_parts.append(content)
        elif ev == 'done':
            debug_url = obj.get('debug_url', '')
        elif ev == 'Error':
            code = obj.get('error_code', '')
            msg = obj.get('error_message', '')
            raise SystemExit(f'流式执行错误 code={code}: {msg}')

    for raw_line in resp:
        line = raw_line.decode('utf-8', errors='replace').rstrip('\r\n')
        if line == '':
            flush()
        elif line.startswith('event:'):
            cur_event = line[6:].strip()
        elif line.startswith('data:'):
            cur_data.append(line[5:].lstrip())
    flush()

    output = '\n'.join(result_parts).strip()
    if debug_url:
        print(f'[debug] {debug_url}', file=sys.stderr)
    return output


# ── API 操作 ─────────────────────────────────────────────────────

def api_run(cfg: dict[str, Any], params: dict, is_async: bool) -> dict:
    cfg = with_apikey(cfg)
    url = base_url(cfg) + WORKFLOW_RUN_PATH
    payload: dict[str, Any] = {
        'workflow_id': cfg['workflow_id'],
        'app_id': cfg['app_id'],
    }
    if params:
        payload['parameters'] = params
    if is_async:
        payload['is_async'] = True
    return check_code(http_request('POST', url, api_headers(cfg), payload))


def api_stream_run(cfg: dict[str, Any], params: dict) -> str:
    cfg = with_apikey(cfg)
    url = base_url(cfg) + WORKFLOW_STREAM_RUN_PATH
    payload: dict[str, Any] = {
        'workflow_id': cfg['workflow_id'],
        'app_id': cfg['app_id'],
    }
    if params:
        payload['parameters'] = params
    resp = http_request('POST', url, api_headers(cfg, {'Accept': 'text/event-stream'}), payload, stream=True)
    return parse_sse(resp)


# ── 命令 ─────────────────────────────────────────────────────────

def cmd_show(_: argparse.Namespace) -> None:
    print(json.dumps(load_config(), ensure_ascii=False, indent=2))


def cmd_init(args: argparse.Namespace) -> None:
    cfg = resolve_config(
        link=args.link, agent_id=args.agent_id,
        app_id=args.app_id, workflow_id=args.workflow_id,
        env=args.env, persist=True,
    )
    print('已写入 config:')
    print(json.dumps({k: v for k, v in cfg.items() if k not in SENSITIVE_KEYS}, ensure_ascii=False, indent=2))


def cmd_run(args: argparse.Namespace) -> None:
    cfg = resolve_config(
        link=getattr(args, 'link', None),
        agent_id=args.agent_id, app_id=args.app_id,
        workflow_id=args.workflow_id, persist=False,
    )
    require(cfg, 'agentId', 'app_id', 'workflow_id', 'UUAP-ID')
    params = json.loads(args.params) if args.params else {}
    j = api_run(cfg, params, args.is_async)
    if args.is_async:
        print(f'[异步] execute_id={j.get("execute_id")}')
        if j.get('debug_url'):
            print(f'[debug] {j["debug_url"]}')
    else:
        data = j.get('data', '')
        # data 可能是 JSON 字符串
        try:
            inner = json.loads(data) if isinstance(data, str) else data
            output = inner.get('output') or inner.get('result') or data if isinstance(inner, dict) else data
        except (json.JSONDecodeError, AttributeError):
            output = data
        print(output)
        if j.get('debug_url'):
            print(f'[debug] {j["debug_url"]}', file=sys.stderr)


def cmd_stream(args: argparse.Namespace) -> None:
    cfg = resolve_config(
        link=getattr(args, 'link', None),
        agent_id=args.agent_id, app_id=args.app_id,
        workflow_id=args.workflow_id, persist=False,
    )
    require(cfg, 'agentId', 'app_id', 'workflow_id', 'UUAP-ID')
    params = json.loads(args.params) if args.params else {}
    output = api_stream_run(cfg, params)
    print(output or '[警告] 流式响应未解析出内容。')


# ── 参数解析 ─────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='run.py', description='度小满原力 AI 平台 Workflow API 运行器')
    sub = p.add_subparsers(dest='cmd', required=True)

    # run（非流式）
    s = sub.add_parser('run', help='非流式执行 workflow（同步或异步）')
    s.add_argument('--link', help='工作流链接（自动解析 agentId/app_id/workflow_id/env）')
    s.add_argument('--agent-id', help='agentId（覆盖 config）')
    s.add_argument('--app-id', help='app_id（覆盖 config）')
    s.add_argument('--workflow-id', help='workflow_id（覆盖 config）')
    s.add_argument('--params', help='JSON 格式的 parameters，如 \'{"input":"你好"}\'')
    s.add_argument('--async', dest='is_async', action='store_true', help='异步执行')
    s.set_defaults(fn=cmd_run)

    # stream（流式）
    s = sub.add_parser('stream', help='流式执行 workflow（SSE）')
    s.add_argument('--link', help='工作流链接（自动解析 agentId/app_id/workflow_id/env）')
    s.add_argument('--agent-id', help='agentId（覆盖 config）')
    s.add_argument('--app-id', help='app_id（覆盖 config）')
    s.add_argument('--workflow-id', help='workflow_id（覆盖 config）')
    s.add_argument('--params', help='JSON 格式的 parameters，如 \'{"input":"你好"}\'')
    s.set_defaults(fn=cmd_stream)

    # init
    s = sub.add_parser('init', help='保存常用配置，不发起请求')
    s.add_argument('--link', help='链接（自动解析 agentId/env）')
    s.add_argument('--agent-id')
    s.add_argument('--app-id')
    s.add_argument('--workflow-id')
    s.add_argument('--env', choices=['prod', 'dev'])
    s.set_defaults(fn=cmd_init)

    sub.add_parser('show', help='查看当前配置').set_defaults(fn=cmd_show)

    return p


if __name__ == '__main__':
    args = build_parser().parse_args()
    args.fn(args)

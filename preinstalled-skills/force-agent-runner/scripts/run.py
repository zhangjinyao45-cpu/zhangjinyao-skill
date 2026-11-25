#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""度小满原力 AI 平台智能体 API 运行器。

用法:
    python run.py auto <链接或bot_id> "问题"
    python run.py init [--link <url>] [--agent-id <id>] [--bot-id <id>] [--env dev|prod]
    python run.py create
    python run.py chat "下一句话"
    python run.py list
    python run.py conversations
    python run.py clear
    python run.py delete
    python run.py show
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib import error, request

# ── 环境配置 ─────────────────────────────────────────────────────
ENDPOINTS = {
    'prod': 'https://ai-force.duxiaoman-int.com',
    'dev':  'https://dxm-agent.duxiaoman-int.com',
}
API_PATH = '/agent-force-gateway/proxy/studio'
GET_TEST_KEY_PATH = '/agent-force-store/agent/getTestKey'

CONFIG_PATH = Path.home() / '.force-agent-runner' / 'config.json'
CONFIG_PATH.parent.mkdir(exist_ok=True)
TIMEOUT = 120

LINK_AGENT_RE = re.compile(r'agentId=(\d{15,})')
LINK_BOT_RE   = re.compile(r'/bot/(\d{15,})')
LINK_SPACE_RE = re.compile(r'/space/(\d{15,})')

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


def parse_link(url: str) -> dict[str, str]:
    out: dict[str, str] = {}
    if m := LINK_AGENT_RE.search(url):
        out['agentId'] = m.group(1)
    if m := LINK_BOT_RE.search(url):
        out['bot_id'] = m.group(1)
    if m := LINK_SPACE_RE.search(url):
        out['space_id'] = m.group(1)
    if 'dxm-agent.duxiaoman-int.com' in url:
        out['env'] = 'dev'
    elif 'ai-force.duxiaoman-int.com' in url:
        out['env'] = 'prod'
    return out


def resolve_config(
    *,
    link: str | None = None,
    agent_id: str | None = None,
    bot_id: str | None = None,
    env: str | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    """合并链接/参数/已存配置，补全 UUAP-ID。APIKey 不在此处理。"""
    cfg = load_config()
    if link:
        cfg.update(parse_link(link))
    if agent_id:
        cfg['agentId'] = agent_id
    if bot_id:
        cfg['bot_id'] = bot_id
    if env:
        cfg['env'] = env

    if not cfg.get('env'):
        cfg['env'] = 'prod'
    if not cfg.get('UUAP-ID'):
        if u := os.environ.get('UUAP_ID', '').strip():
            cfg['UUAP-ID'] = u
    if not cfg.get('agentId') and cfg.get('bot_id'):
        cfg['agentId'] = cfg['bot_id']

    if persist:
        save_config(cfg)
    return cfg


def base_url(cfg: dict[str, Any]) -> str:
    return ENDPOINTS.get(cfg.get('env', 'prod'), ENDPOINTS['prod']) + API_PATH


def require(cfg: dict[str, Any], *keys: str) -> None:
    miss = [k for k in keys if not cfg.get(k)]
    if not miss:
        return
    hints = []
    if 'UUAP-ID' in miss:
        hints.append('UUAP-ID 缺失：请确认 ForceClaw 已注入 UUAP_ID 环境变量。')
    if 'bot_id' in miss:
        hints.append('bot_id 缺失：请提供调试链接或 --bot-id <id>。')
    if 'UUAP_COOKIE' in miss:
        hints.append('UUAP_COOKIE 缺失：请确认 ForceClaw 已注入 UUAP_COOKIE 环境变量。')
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


# ── SSE 解析 ─────────────────────────────────────────────────────

def parse_sse(resp) -> str:
    full_delta: list[str] = []
    final_completed = ''
    cur_event = ''
    cur_data: list[str] = []

    def flush():
        nonlocal cur_event, cur_data, final_completed
        if not cur_data:
            cur_event = ''
            return
        data_str = '\n'.join(cur_data).strip()
        cur_data = []
        if data_str in ('', '[DONE]'):
            cur_event = ''
            return
        try:
            obj = json.loads(data_str)
        except json.JSONDecodeError:
            cur_event = ''
            return
        ev = cur_event
        cur_event = ''
        role = obj.get('role')
        msg_type = obj.get('type') or obj.get('message_type')
        content = obj.get('content', '')
        if 'delta' in ev and role == 'assistant' and msg_type in (None, 'answer'):
            if isinstance(content, str):
                full_delta.append(content)
        elif 'completed' in ev and role == 'assistant' and msg_type in (None, 'answer'):
            if isinstance(content, str) and content:
                final_completed = content

    for raw_line in resp:
        line = raw_line.decode('utf-8', errors='replace').rstrip('\r\n')
        if line == '':
            flush()
        elif line.startswith('event:'):
            cur_event = line[6:].strip()
        elif line.startswith('data:'):
            cur_data.append(line[5:].lstrip())
    flush()
    return (''.join(full_delta).strip()) or final_completed.strip()


# ── APIKey 实时获取 ───────────────────────────────────────────────

def fetch_apikey(cfg: dict[str, Any]) -> str:
    """每次调用前实时从 getTestKey 接口获取 APIKey，不存盘。"""
    # 优先用 bot_id，因为 getTestKey 接口需要 bot_id 而非 agentId
    agent_id = cfg.get('bot_id') or cfg.get('agentId')
    if not agent_id:
        raise SystemExit('获取 APIKey 需要 agent_id，请先通过链接或 --agent-id 指定智能体。')
    cookie = os.environ.get('UUAP_COOKIE', '').strip()
    if not cookie:
        raise SystemExit('获取 APIKey 需要 UUAP_COOKIE 环境变量，请确认 ForceClaw 已注入。')
    env = cfg.get('env', 'prod')
    url = ENDPOINTS.get(env, ENDPOINTS['prod']) + GET_TEST_KEY_PATH
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Cookie': cookie,
    }
    payload = {'data': {'type': 0, 'agent_id': agent_id}, 'requestId': '1780907677834'}
    j = http_request('POST', url, headers, payload)
    d = j.get('data')
    # data 可能直接是 key 字符串，也可能是嵌套对象
    if isinstance(d, str) and d:
        key = d
    elif isinstance(d, dict):
        key = d.get('api_key') or d.get('apiKey') or d.get('key')
    else:
        key = None
    key = key or j.get('api_key') or j.get('apiKey')
    if not key:
        raise SystemExit(
            f'getTestKey 响应中未找到 APIKey。\n'
            f'原始响应:\n{json.dumps(j, ensure_ascii=False, indent=2)}'
        )
    return key


def with_apikey(cfg: dict[str, Any]) -> dict[str, Any]:
    """返回注入了实时 APIKey 的 cfg 副本（不修改原 cfg，不写盘）。"""
    key = fetch_apikey(cfg)
    return {**cfg, 'APIKey': key}


def api_headers(cfg: dict[str, Any], extra: dict[str, str] | None = None) -> dict[str, str]:
    h = {
        'Authorization': f"Bearer {cfg['APIKey']}",
        'agentId': cfg.get('agentId', cfg.get('bot_id', '')),
        'UUAP-ID': cfg.get('UUAP-ID', ''),
        'Content-Type': 'application/json',
    }
    if extra:
        h.update(extra)
    return h


# ── API 操作 ─────────────────────────────────────────────────────

def api_create(cfg: dict[str, Any]) -> str:
    cfg = with_apikey(cfg)
    url = f"{base_url(cfg)}/v1/conversation/create"
    j = check_code(http_request('POST', url, api_headers(cfg), {'bot_id': cfg['bot_id']}))
    conv_id = j['data']['id']
    cfg_saved = load_config()
    cfg_saved['conversation_id'] = conv_id
    save_config(cfg_saved)
    return conv_id


def api_chat(cfg: dict[str, Any], user_text: str) -> str:
    cfg = with_apikey(cfg)
    url = f"{base_url(cfg)}/v3/chat?conversation_id={cfg['conversation_id']}"
    payload = {
        'bot_id': cfg['bot_id'],
        'user_id': '3218123123',
        'stream': True,
        'additional_messages': [{'role': 'user', 'content': user_text, 'content_type': 'text'}],
    }
    resp = http_request('POST', url, api_headers(cfg, {'Accept': 'text/event-stream'}), payload, stream=True)
    return parse_sse(resp)


def api_list(cfg: dict[str, Any]) -> dict:
    cfg = with_apikey(cfg)
    url = f"{base_url(cfg)}/v1/conversation/message/list?conversation_id={cfg['conversation_id']}"
    return check_code(http_request('POST', url, api_headers(cfg), {}))


def api_conversations(cfg: dict[str, Any]) -> dict:
    cfg = with_apikey(cfg)
    url = f"{base_url(cfg)}/v1/conversations?bot_id={cfg['bot_id']}"
    return check_code(http_request('GET', url, api_headers(cfg)))


def api_clear(cfg: dict[str, Any]) -> dict:
    cfg = with_apikey(cfg)
    url = f"{base_url(cfg)}/v1/conversations/{cfg['conversation_id']}/clear"
    return check_code(http_request('POST', url, api_headers(cfg)))


def api_delete(cfg: dict[str, Any]) -> None:
    cfg = with_apikey(cfg)
    url = f"{base_url(cfg)}/v1/conversations/{cfg['conversation_id']}"
    check_code(http_request('DELETE', url, api_headers(cfg)))


# ── 命令 ─────────────────────────────────────────────────────────

def cmd_show(_: argparse.Namespace) -> None:
    print(json.dumps(load_config(), ensure_ascii=False, indent=2))


def cmd_init(args: argparse.Namespace) -> None:
    cfg = resolve_config(
        link=args.link, agent_id=args.agent_id,
        bot_id=args.bot_id, env=args.env, persist=True,
    )
    print('已写入 config.json:')
    print(json.dumps({k: v for k, v in cfg.items() if k not in SENSITIVE_KEYS}, ensure_ascii=False, indent=2))


def cmd_create(_: argparse.Namespace) -> None:
    cfg = resolve_config(persist=False)
    require(cfg, 'bot_id', 'UUAP-ID')
    print(f'会话已创建: {api_create(cfg)}')


def cmd_chat(args: argparse.Namespace) -> None:
    cfg = resolve_config(persist=False)
    require(cfg, 'bot_id', 'UUAP-ID', 'conversation_id')
    print(api_chat(cfg, args.text) or '[警告] 未解析出答案，请执行 list 查看原始消息。')


def cmd_auto(args: argparse.Namespace) -> None:
    link = args.url if ('/' in args.url or 'http' in args.url) else None
    agent_id = args.url if not link else None
    cfg = resolve_config(link=link, agent_id=agent_id, persist=True)
    require(cfg, 'bot_id', 'UUAP-ID')
    if not cfg.get('conversation_id'):
        print(f'[会话] {api_create(cfg)}', file=sys.stderr)
        cfg = load_config()
    print(api_chat(cfg, args.text) or '[警告] 未解析出答案，请执行 list 查看原始消息。')


def cmd_list(_: argparse.Namespace) -> None:
    cfg = resolve_config(persist=False)
    require(cfg, 'UUAP-ID', 'conversation_id')
    print(json.dumps(api_list(cfg), ensure_ascii=False, indent=2))


def cmd_conversations(_: argparse.Namespace) -> None:
    cfg = resolve_config(persist=False)
    require(cfg, 'UUAP-ID', 'bot_id')
    print(json.dumps(api_conversations(cfg), ensure_ascii=False, indent=2))


def cmd_clear(_: argparse.Namespace) -> None:
    cfg = resolve_config(persist=False)
    require(cfg, 'UUAP-ID', 'conversation_id')
    print(json.dumps(api_clear(cfg), ensure_ascii=False, indent=2))


def cmd_delete(_: argparse.Namespace) -> None:
    cfg = resolve_config(persist=False)
    require(cfg, 'UUAP-ID', 'conversation_id')
    api_delete(cfg)
    saved = load_config()
    saved.pop('conversation_id', None)
    save_config(saved)
    print('会话已删除。')


# ── 参数解析 ─────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='run.py', description='度小满原力 AI 平台智能体 API 运行器')
    sub = p.add_subparsers(dest='cmd', required=True)

    s = sub.add_parser('auto', help='一键：解析链接/ID → 创建会话 → chat')
    s.add_argument('url', help='调试链接、广场链接，或直接输入 bot_id')
    s.add_argument('text', help='发送的问题')
    s.set_defaults(fn=cmd_auto)

    s = sub.add_parser('init', help='保存配置，不发起请求')
    s.add_argument('--link', help='链接（自动解析 agentId/bot_id/env）')
    s.add_argument('--agent-id')
    s.add_argument('--bot-id')
    s.add_argument('--env', choices=['prod', 'dev'])
    s.set_defaults(fn=cmd_init)

    sub.add_parser('create', help='创建会话').set_defaults(fn=cmd_create)

    s = sub.add_parser('chat', help='向当前会话发一句话')
    s.add_argument('text')
    s.set_defaults(fn=cmd_chat)

    sub.add_parser('list', help='查询历史消息').set_defaults(fn=cmd_list)
    sub.add_parser('conversations', help='查询 bot 的所有会话').set_defaults(fn=cmd_conversations)
    sub.add_parser('clear', help='清空当前会话').set_defaults(fn=cmd_clear)
    sub.add_parser('delete', help='删除当前会话').set_defaults(fn=cmd_delete)
    sub.add_parser('show', help='查看 config.json').set_defaults(fn=cmd_show)

    return p


if __name__ == '__main__':
    args = build_parser().parse_args()
    args.fn(args)

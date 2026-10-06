#!/usr/bin/env python3
"""Validate semantic SVGs and safely fill a new, empty Lark whiteboard."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

WHITEBOARD = ['npx', '-y', '@larksuite/whiteboard-cli@0.2.13']


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def run_json(argv, cwd=None, stdin=None):
    env = dict(os.environ, LARKSUITE_CLI_NO_UPDATE_NOTIFIER='1',
               LARKSUITE_CLI_NO_SKILLS_NOTIFIER='1')
    result = subprocess.run(argv, input=stdin, text=True, capture_output=True,
                            cwd=cwd, env=env, timeout=240)
    payload = result.stdout if result.returncode == 0 else result.stderr
    try:
        obj = json.loads(payload)
    except ValueError:
        raise RuntimeError('命令未返回 JSON：' + (result.stderr or result.stdout)[-1200:])
    if result.returncode or obj.get('ok') is False or obj.get('code', 0) != 0:
        raise RuntimeError(json.dumps(obj.get('error', obj), ensure_ascii=False))
    return obj


def local_name(tag):
    return tag.rsplit('}', 1)[-1]


def normalized(text):
    return re.sub(r'\s+', '', text)


def normalize_icons(source, target):
    """Isolate transformed icon paths so fallback cannot rasterize module text."""
    root = ET.parse(source).getroot()
    namespace = '{http://www.w3.org/2000/svg}'
    ET.register_namespace('', namespace[1:-1])
    changed = 0
    for parent in list(root.iter()):
        for element in list(parent):
            if local_name(element.tag) == 'path' and 'transform' in element.attrib:
                group = ET.Element(namespace + 'g', {'transform': element.attrib.pop('transform')})
                index = list(parent).index(element)
                parent.remove(element)
                parent.insert(index, group)
                group.append(element)
                changed += 1
    Path(target).write_text(ET.tostring(root, encoding='unicode'))
    return changed


def editable_text_check(spec, nodes):
    text = normalized(''.join(n.get('text', {}).get('text', '') for n in nodes))
    required = [value for node in spec['nodes'] for value in
                [node['title'], *node.get('detail', [])]]
    required.extend(edge['label'] for edge in spec.get('edges', [])
                    if isinstance(edge.get('label'), str) and edge['label'])
    missing = [value for value in required if normalized(value) not in text]
    if missing:
        raise RuntimeError('以下业务文字未转成可编辑节点：' + json.dumps(missing, ensure_ascii=False))
    return {'required_text_missing': [], 'editable_text_check': 'passed'}


def semantic_check(spec, svg):
    raw = Path(svg).read_text()
    if '<!DOCTYPE' in raw.upper() or '<!ENTITY' in raw.upper():
        raise ValueError('SVG 禁止 DTD/实体定义')
    root = ET.fromstring(raw)
    errors = []
    if local_name(root.tag) != 'svg' or not root.get('viewBox'):
        errors.append('必须是带 viewBox 的 SVG')
    banned = {'script', 'foreignObject', 'image', 'filter', 'mask', 'clipPath', 'pattern', 'style'}
    nodes, edges = {}, {}
    for e in root.iter():
        if local_name(e.tag) in banned:
            errors.append('不支持元素：' + local_name(e.tag))
        for key, value in e.attrib.items():
            if local_name(key).lower().startswith('on'):
                errors.append('禁止 SVG 事件处理器')
            if local_name(key) == 'href' and not value.startswith('#'):
                errors.append('禁止 SVG 外部引用')
            for target in re.findall(r'url\(([^)]+)\)', value):
                if not target.strip(' \"\'').startswith('#'):
                    errors.append('禁止 SVG 外部资源')
        if e.get('data-node-id'):
            key = e.get('data-node-id')
            if key in nodes:
                errors.append('重复节点：' + key)
            nodes[key] = normalized(''.join(e.itertext()))
        if e.get('data-edge-id'):
            key = e.get('data-edge-id')
            if key in edges:
                errors.append('重复关系：' + key)
            edges[key] = (e.get('data-source'), e.get('data-target'))
    expected_nodes = {n['id']: n for n in spec['nodes']}
    expected_edges = {e['id']: (e['source'], e['target']) for e in spec['edges']}
    if len(expected_nodes) != len(spec['nodes']) or len(expected_edges) != len(spec['edges']):
        errors.append('规格包含重复 ID')
    if set(nodes) != set(expected_nodes):
        errors.append(f'节点不一致：缺少{set(expected_nodes)-set(nodes)}，多出{set(nodes)-set(expected_nodes)}')
    for key, node in expected_nodes.items():
        for value in [node['title'], *node.get('detail', [])]:
            if normalized(value) not in nodes.get(key, ''):
                errors.append(f'{key} 缺少文字：{value}')
    if edges != expected_edges:
        errors.append('关系 ID 或端点与结构不符')
    for source, target in expected_edges.values():
        if source not in expected_nodes or target not in expected_nodes:
            errors.append('规格关系指向不存在的节点')
    result = {'nodes': len(nodes), 'edges': len(edges), 'errors': errors}
    if errors:
        raise ValueError(json.dumps(result, ensure_ascii=False))
    return result


def check(args):
    svg, out = Path(args.svg).resolve(), Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    spec = json.loads(Path(args.spec).read_text())
    semantic = semantic_check(spec, svg)
    write_json(out / 'semantic.json', semantic)
    publish_svg = out / 'diagram.svg'
    normalize_icons(svg, publish_svg)
    svg = publish_svg
    converted = run_json(WHITEBOARD + ['-i', str(svg), '-f', 'svg', '--check'])
    write_json(out / 'geometry.json', converted)
    report = converted.get('data', {}).get('check')
    if not isinstance(report, dict) or report.get('errors', 0):
        raise RuntimeError('画板几何检查失败或返回结构未知，见 geometry.json')
    for target, argv in [
        ('render.json', ['-o', str(out / 'diagram.png'), '-s', '1']),
        ('convert.json', ['--to', 'openapi', '--format', 'json', '-o', str(out / 'openapi.json')])
    ]:
        write_json(out / target, run_json(WHITEBOARD + ['-i', str(svg), '-f', 'svg'] + argv))
    if not (out / 'diagram.png').is_file() or not (out / 'openapi.json').is_file():
        raise RuntimeError('转换未生成预期文件')
    native = json.loads((out / 'openapi.json').read_text())
    editable_text_check(spec, native['nodes'])
    return {'ok': True, **semantic, 'geometry_errors': report['errors'],
            'geometry_warnings': report.get('warnings', 0), 'out': str(out),
            'publish_svg': str(publish_svg), 'editable_text_check': 'passed',
            'next': '查看 PNG；本地通过不代表飞书远端已验证'}


def node_list(result):
    data = result.get('data')
    if result.get('ok') is True and data == {'msg': 'whiteboard is empty'}:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get('nodes'), list):
        return data['nodes']
    raise RuntimeError('无法确认远端节点格式；拒绝猜测空画板')


def publish(args):
    svg, state_path = Path(args.svg).resolve(), Path(args.state).resolve()
    digest = hashlib.sha256(svg.read_bytes()).hexdigest()
    previous = json.loads(state_path.read_text()) if state_path.exists() else None
    identity = {'board': args.board, 'profile': args.profile,
                'app_id': args.expected_app_id, 'svg_sha256': digest}
    if previous and any(previous.get(k) != v for k, v in identity.items()):
        raise RuntimeError('收据与本次输入不一致，请为新版本创建新画板和新收据')
    base = ['lark-cli', '--profile', args.profile]
    auth = run_json(base + ['auth', 'status', '--json', '--verify'])
    if auth.get('appId') != args.expected_app_id or not auth.get('identities', {}).get('user', {}).get('verified'):
        raise RuntimeError('应用 ID 或用户身份不匹配，未写入')
    query = base + ['whiteboard', '+query', '--whiteboard-token', args.board,
                    '--output_as', 'raw', '--as', 'user']
    remote = run_json(query)
    nodes = node_list(remote)
    if previous and previous.get('status') in ('written', 'complete'):
        if not nodes:
            raise RuntimeError('收据显示已写入但远端为空，需人工检查，不自动重写')
        receipt = previous
    else:
        if nodes:
            raise RuntimeError('画板已有内容；拒绝覆盖或追加重复版本。请核对未完成收据或使用新画板')
        key = 'arch-' + hashlib.sha256((args.board + digest).encode()).hexdigest()[:32]
        receipt = {**identity, 'idempotent_token': key, 'status': 'pending'}
        write_json(state_path, receipt)
        update = base + ['whiteboard', '+update', '--whiteboard-token', args.board,
                         '--input_format', 'svg', '--source', '-', '--as', 'user',
                         '--idempotent-token', key]
        run_json(update, stdin=svg.read_text())
        receipt['status'] = 'written'
        write_json(state_path, receipt)
        remote = run_json(query)
        nodes = node_list(remote)
    if not nodes:
        raise RuntimeError('写入返回成功但回读无节点')
    state_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(state_path.with_suffix('.remote.json'), remote)
    types = Counter(n.get('type', 'unknown') for n in nodes)
    if set(types) <= {'image', 'unknown'}:
        raise RuntimeError('没有验证到可编辑节点类型；请查看 raw，不宣称可编辑')
    preview = state_path.stem + '.remote.png'
    run_json(base + ['whiteboard', '+query', '--whiteboard-token', args.board,
                    '--output_as', 'image', '--output', preview, '--overwrite', '--as', 'user'],
             cwd=state_path.parent)
    receipt.update(status='complete', node_count=len(nodes), node_types=dict(types),
                   preview=str(state_path.parent / preview), visual_review='pending')
    write_json(state_path, receipt)
    return {'ok': True, **receipt, 'next': '查看远端 PNG，验证排版与连线'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    checker = subs.add_parser('check')
    checker.add_argument('--spec', required=True)
    checker.add_argument('--svg', required=True)
    checker.add_argument('--out', required=True)
    publisher = subs.add_parser('publish')
    for flag in ('svg', 'board', 'profile', 'expected-app-id', 'state'):
        publisher.add_argument('--' + flag, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(check(args) if args.command == 'check' else publish(args), ensure_ascii=False))
    except (OSError, ValueError, RuntimeError, ET.ParseError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

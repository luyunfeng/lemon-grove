"""Data relationships, UML, DFD, dependencies and explicit event subscriptions.

The established structure layouts remain the single implementation for ER/class/
dependency. DFD delegates to types_behavior; event_flow adds semantics to the
structure router without interpreting acknowledgements as new publications.
"""
from copy import deepcopy
import re

try:
    from .types_structure import render_er, render_class, render_dependency, _render
    from .types_behavior import render_dataflow
except ImportError:
    from types_structure import render_er, render_class, render_dependency, _render
    from types_behavior import render_dataflow

EVENT_NODES = {
    'publisher': (0, 'blue', '«publisher» 事件发布者'),
    'topic': (1, 'purple', '«topic» 事件主题'),
    'subscriber': (2, 'teal', '«subscriber» 独立订阅者'),
    'dead_letter': (3, 'rose', '«dead letter» 死信主题'),
}
EVENT_EDGES = {
    'publish': ('publisher', 'topic', 'blue'),
    'deliver': ('topic', 'subscriber', 'teal'),
    'ack': ('subscriber', 'topic', 'slate'),
    'dead_letter': ('subscriber', 'dead_letter', 'rose'),
}


def _known_type_family(declaration):
    """Conservative scalar families, not a SQL parser or DB compatibility test.

    Only recognized type spellings plus an optional known constraint suffix are
    compared. Unknown/custom/dialect-specific declarations return None. Length,
    precision and constraints are deliberately not foreign-key type evidence.
    """
    if not isinstance(declaration, str):
        return None
    value = ' '.join(declaration.lower().split())
    families = {
        'uuid': ('uuid',),
        'number': ('smallint', 'integer', 'int', 'bigint', 'decimal', 'numeric',
                   'real', 'float', 'double precision', 'serial', 'bigserial'),
        'text': ('character varying', 'varchar', 'character', 'char', 'text', 'str', 'string'),
        'boolean': ('boolean', 'bool'),
        'temporal': ('timestamp with time zone', 'timestamp without time zone',
                     'timestamp', 'timestamptz', 'datetime', 'date', 'time'),
        'binary': ('bytea', 'binary', 'varbinary', 'blob'),
    }
    constraint = r'(?:unique|not null|null|primary key|references|check|default|constraint|collate|generated)\b'
    for family, names in families.items():
        for name in sorted(names, key=len, reverse=True):
            match = re.match(re.escape(name) + r'(?:\s*\(\s*\d+(?:\s*,\s*\d+)?\s*\))?(?=\s|$)', value)
            if not match:
                continue
            suffix = value[match.end():].strip()
            if not suffix or re.match(constraint, suffix):
                return family
    return None


def _requires_edge_label(diagram, relationship):
    # UML relations and ER cardinalities already have a standard visual grammar.
    # Import/implements share the dependency glyph: their refinement needs text.
    return diagram in ('dataflow', 'event_flow') or (
        diagram == 'dependency' and relationship in ('import', 'implements'))


def inspect_data_extra(spec, layout):
    """Return additional errors; layout=None performs input-only checks.

    Error records follow semantic_rules.inspect's [{code, node?/edge?, ...}]
    contract. Calling with another diagram type is a no-op. This function never
    mutates spec/layout, writes files, or applies a visual score.
    """
    kind = spec.get('diagram_type')
    if kind not in ('er', 'class', 'dataflow', 'dependency', 'event_flow'):
        return []
    errors = []
    def fail(code, **detail):
        errors.append({'code': code, **detail})
    nodes = spec.get('nodes', [])
    edges = spec.get('edges', [])
    byid = {n['id']: n for n in nodes}
    byedge = {e['id']: e for e in edges}
    drawn = {e['id']: e for e in (layout or {}).get('edges', [])}
    if len(byid) != len(nodes): fail('data-duplicate-node-id')
    if len(byedge) != len(edges): fail('data-duplicate-edge-id')
    for e in edges:
        if e['source'] not in byid or e['target'] not in byid:
            fail('data-unknown-endpoint', edge=e['id'])
        if _requires_edge_label(kind, e.get('kind')) and not str(e.get('label') or '').strip():
            fail('data-edge-label-required', edge=e['id'])
    if any(e['source'] not in byid or e['target'] not in byid for e in edges):
        return errors
    if kind == 'er':
        for n in nodes:
            fields = n.get('fields', [])
            names = [f.get('name') for f in fields if isinstance(f, dict)]
            if len(names) != len(fields) or not names or len(set(names)) != len(names) or not all(names):
                fail('er-invalid-fields', node=n['id'])
        for e in edges:
            fields = {side: {f.get('name'): f for f in byid[e[side]].get('fields', []) if isinstance(f, dict)} for side in ('source', 'target')}
            a, b = fields['source'].get(e.get('source_field')), fields['target'].get(e.get('target_field'))
            if a and b:
                source_type = _known_type_family(a.get('type'))
                target_type = _known_type_family(b.get('type'))
                if source_type is not None and target_type is not None and source_type != target_type:
                    fail('er-reference-type-mismatch', edge=e['id'])
    elif kind == 'class':
        allowed = {'inheritance', 'realization', 'composition', 'aggregation', 'association', 'dependency'}
        for n in nodes:
            if not isinstance(n.get('fields'), list) or not isinstance(n.get('methods'), list):
                fail('class-compartments-required', node=n['id'])
        for e in edges:
            rel = e.get('kind')
            if rel not in allowed: fail('class-unsupported-relationship', edge=e['id'], kind=rel)
            if layout is not None:
                d = drawn.get(e['id'], {})
                if rel in ('inheritance', 'association', 'composition','aggregation') and d.get('dash'):
                    fail('class-solid-relationship-dashed', edge=e['id'])
                if rel == 'dependency' and (not d.get('dash') or d.get('marker') != 'open'):
                    fail('class-dependency-symbol', edge=e['id'])
    elif kind == 'dependency':
        for e in edges:
            if e.get('kind') not in ('import', 'dependency', 'implements'):
                fail('dependency-unsupported-relationship', edge=e['id'])
            if layout is not None:
                d = drawn.get(e['id'], {})
                if d.get('marker') != 'open' or not d.get('dash'):
                    fail('dependency-symbol', edge=e['id'])
                if d.get('role') != ('orange' if e.get('kind') == 'implements' else 'slate'):
                    fail('dependency-edge-color-role', edge=e['id'])
    elif kind == 'dataflow':
        for n in nodes:
            if n.get('kind') not in ('external', 'process', 'store'):
                fail('dfd-unknown-node-kind', node=n['id'])
            if n.get('kind') == 'process':
                if not any(e['target'] == n['id'] for e in edges): fail('dfd-process-without-input', node=n['id'])
                if not any(e['source'] == n['id'] for e in edges): fail('dfd-process-without-output', node=n['id'])
    elif kind == 'event_flow':
        for n in nodes:
            if n.get('kind') not in EVENT_NODES:
                fail('event-unknown-node-kind', node=n['id'])
            subscribable=n.get('kind')=='topic' or (n.get('kind')=='dead_letter' and any(e['source']==n['id'] and e.get('kind')=='deliver' for e in edges))
            if subscribable and (not n.get('event_type') or n.get('delivery_mode') != 'fanout'):
                fail('event-topic-contract-required', node=n['id'])
        for e in edges:
            rel = e.get('kind')
            contract = EVENT_EDGES.get(rel)
            if not contract:
                fail('event-unknown-edge-kind', edge=e['id']); continue
            a, b = byid[e['source']], byid[e['target']]
            pair=(a.get('kind'),b.get('kind'))
            valid=pair==contract[:2] or (rel=='deliver' and pair==('dead_letter','subscriber')) or (rel=='ack' and pair==('subscriber','dead_letter'))
            if not valid:
                fail('event-invalid-direction', edge=e['id'], kind=rel)
            if rel in ('publish', 'deliver'):
                topic = b if rel == 'publish' else a
                if not e.get('event_type') or e.get('event_type') != topic.get('event_type'):
                    fail('event-payload-mismatch', edge=e['id'])
            if rel == 'deliver' and not e.get('subscription'):
                fail('event-subscription-required', edge=e['id'])
            if rel == 'ack':
                delivery = byedge.get(e.get('acknowledges'), {})
                if delivery.get('kind') != 'deliver' or (delivery.get('source'), delivery.get('target')) != (e['target'], e['source']):
                    fail('event-ack-not-for-delivery', edge=e['id'])
            if rel == 'dead_letter':
                delivery = byedge.get(e.get('failed_delivery'), {})
                if delivery.get('kind') != 'deliver' or delivery.get('target') != e['source']:
                    fail('event-dead-letter-without-delivery', edge=e['id'])
                if not e.get('event_type') or e.get('event_type') != delivery.get('event_type'):
                    fail('event-dead-letter-payload-mismatch', edge=e['id'])
            if layout is not None:
                d = drawn.get(e['id'], {})
                if d.get('marker') != 'open' or bool(d.get('dash')) != (rel == 'ack'):
                    fail('event-edge-symbol', edge=e['id'])
                if d.get('role') != contract[2]: fail('event-edge-color-role', edge=e['id'])
        for n in nodes:
            if n.get('kind') in ('topic','dead_letter'):
                subscriptions = [e.get('subscription') for e in edges if e['source'] == n['id'] and e.get('kind') == 'deliver']
                if len(subscriptions) != len(set(subscriptions)):
                    fail('event-fanout-subscriptions-not-independent', node=n['id'])
            if n.get('kind') == 'subscriber' and not any(e['target'] == n['id'] and e.get('kind') == 'deliver' for e in edges):
                fail('event-subscriber-without-delivery', node=n['id'])
    return errors


def render_event_flow(spec, style):
    errors = inspect_data_extra(spec, None)
    if errors:
        raise ValueError('Invalid event flow: ' + repr(errors))
    prepared = deepcopy(spec)
    for n in prepared['nodes']:
        rank, role, label = EVENT_NODES[n['kind']]
        n['rank'] = rank
        n.setdefault('role', role)
        n['type_label'] = label
    # A dead-letter topic may have its own subscribers. Forward topology adds
    # downstream stages; acknowledgement edges never drive the layout ranks.
    ranks={n['id']:n['rank'] for n in prepared['nodes']}
    forward=[e for e in prepared['edges'] if e['kind']!='ack']
    for _ in range(len(ranks)):
        changed=False
        for e in forward:
            needed=ranks[e['source']]+1
            if ranks[e['target']]<needed:ranks[e['target']]=needed;changed=True
        if not changed:break
    if changed:raise ValueError('Forward event topology contains a cycle; model acknowledgement separately or split feedback view')
    for n in prepared['nodes']:n['rank']=ranks[n['id']]
    for e in prepared['edges']:
        e['role'] = EVENT_EDGES[e['kind']][2]
    prepared.setdefault('legend', [
        {'role': 'blue', 'label': '发布'}, {'role': 'purple', 'label': '主题'},
        {'role': 'teal', 'label': '独立订阅投递'}, {'role': 'slate', 'label': '虚线：消费确认'},
        {'role': 'rose', 'label': '死信转移'},
    ])
    return _render(prepared, style, 'event_flow')


RENDERERS = {
    'er': render_er, 'class': render_class, 'dataflow': render_dataflow,
    'dependency': render_dependency, 'event_flow': render_event_flow,
}

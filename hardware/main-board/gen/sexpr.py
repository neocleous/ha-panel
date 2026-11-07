"""Minimal S-expression reader/writer for KiCad files."""
import re

_TOKEN = re.compile(r'\s*(\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+)')


class Sym(str):
    """Bare (unquoted) atom."""


def parse(text):
    pos = 0
    stack = [[]]
    n = len(text)
    while pos < n:
        m = _TOKEN.match(text, pos)
        if not m:
            if text[pos:].strip() == '':
                break
            raise ValueError('parse error at %d: %r' % (pos, text[pos:pos + 40]))
        tok = m.group(1)
        pos = m.end()
        if tok == '(':
            stack.append([])
        elif tok == ')':
            lst = stack.pop()
            stack[-1].append(lst)
        elif tok.startswith('"'):
            stack[-1].append(tok[1:-1].replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\'))
        else:
            stack[-1].append(Sym(tok))
    return stack[0]


def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def dump(x, indent=0):
    """Serialise nested lists. Strings become quoted unless Sym; numbers formatted."""
    if isinstance(x, list):
        if not x:
            return '()'
        head = x[0]
        simple = all(not isinstance(e, list) for e in x)
        if simple:
            return '(' + ' '.join(atom(e) for e in x) + ')'
        parts = ['(' + atom(head)]
        for e in x[1:]:
            if isinstance(e, list):
                parts.append('\n' + '\t' * (indent + 1) + dump(e, indent + 1))
            else:
                parts.append(' ' + atom(e))
        parts.append('\n' + '\t' * indent + ')')
        return ''.join(parts)
    return atom(x)


def atom(e):
    if isinstance(e, Sym):
        return str(e)
    if isinstance(e, bool):
        return 'yes' if e else 'no'
    if isinstance(e, int):
        return str(e)
    if isinstance(e, float):
        s = ('%.4f' % e).rstrip('0').rstrip('.')
        return '0' if s in ('-0', '') else s
    return q(e)


def find(lst, key):
    for e in lst:
        if isinstance(e, list) and e and e[0] == key:
            return e
    return None


def findall(lst, key):
    return [e for e in lst if isinstance(e, list) and e and e[0] == key]

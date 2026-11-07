"""Programmatic KiCad 9 schematic generation (label-based connectivity)."""
import math
import os
import uuid as _uuid

import symlib
from sexpr import Sym, dump, find, findall

GRID = 1.27
FONT = [Sym('font'), [Sym('size'), 1.27, 1.27]]
KICAD_SCH_VERSION = 20250114
KICAD_SYM_VERSION = 20241209


def U(seed=None):
    if seed is None:
        return str(_uuid.uuid4())
    return str(_uuid.uuid5(_uuid.NAMESPACE_URL, 'ha-panel/' + seed))


def snap(v):
    return round(round(v / GRID) * GRID, 4)


def eff(justify=None, hide=False, size=1.27, bold=False):
    f = [Sym('font'), [Sym('size'), size, size]]
    if bold:
        f.append([Sym('bold'), Sym('yes')])
    e = [Sym('effects'), f]
    if justify:
        e.append([Sym('justify')] + [Sym(j) for j in justify.split()])
    if hide:
        e.append([Sym('hide'), Sym('yes')])
    return e


# ---------------------------------------------------------------- custom symbols
def box_symbol(name, ref, value, footprint='', datasheet='~', description='', left=(), right=(), top=(), bottom=(),
               width=None, pin_len=2.54, pitch=2.54, keywords=''):
    """Rectangular symbol. Side lists: (number, name, type) or None for a gap. Lib coords, y up."""
    nl, nr = len(left), len(right)
    nt, nb = len(top), len(bottom)
    h_rows = max(nl, nr, 1)
    if width is None:
        longest = max([len(p[1]) for p in list(left) + list(right) if p] + [4])
        width = max(snap(longest * 1.27 * 2 + 5.08), snap((max(nt, nb) + 1) * pitch))
        width = math.ceil(width / 2.54) * 2.54
    height = (h_rows + 1) * pitch
    if nt or nb:
        height += 2 * pitch
    height = math.ceil(height / 2.54) * 2.54
    x0, x1 = -width / 2, width / 2
    y1, y0 = height / 2, -height / 2  # top, bottom
    pins = []

    def addpin(num, pname, ptype, x, y, ang):
        pins.append([Sym('pin'), Sym(ptype), Sym('line'), [Sym('at'), x, y, ang], [Sym('length'), pin_len],
                     [Sym('name'), pname, eff()], [Sym('number'), str(num), eff()]])

    ystart = y1 - (2 * pitch if nt else pitch)
    for i, p in enumerate(left):
        if p:
            addpin(p[0], p[1], p[2], snap(x0 - pin_len), snap(ystart - i * pitch), 0)
    for i, p in enumerate(right):
        if p:
            addpin(p[0], p[1], p[2], snap(x1 + pin_len), snap(ystart - i * pitch), 180)
    for side, lst, yy, ang in (('t', top, y1 + pin_len, 270), ('b', bottom, y0 - pin_len, 90)):
        n = len(lst)
        xs0 = -(n - 1) * pitch / 2
        for i, p in enumerate(lst):
            if p:
                addpin(p[0], p[1], p[2], snap(xs0 + i * pitch), snap(yy), ang)
    sym = [Sym('symbol'), name,
           [Sym('pin_names'), [Sym('offset'), 1.016]],
           [Sym('exclude_from_sim'), Sym('no')], [Sym('in_bom'), Sym('yes')], [Sym('on_board'), Sym('yes')],
           [Sym('property'), 'Reference', ref, [Sym('at'), x0, y1 + 1.27, 0], eff('left')],
           [Sym('property'), 'Value', value, [Sym('at'), x0, y0 - 1.27, 0], eff('left top')],
           [Sym('property'), 'Footprint', footprint, [Sym('at'), 0, 0, 0], eff(hide=True)],
           [Sym('property'), 'Datasheet', datasheet, [Sym('at'), 0, 0, 0], eff(hide=True)],
           [Sym('property'), 'Description', description, [Sym('at'), 0, 0, 0], eff(hide=True)]]
    if keywords:
        sym.append([Sym('property'), 'ki_keywords', keywords, [Sym('at'), 0, 0, 0], eff(hide=True)])
    sym.append([Sym('symbol'), name + '_0_1',
                [Sym('rectangle'), [Sym('start'), snap(x0), snap(y1)], [Sym('end'), snap(x1), snap(y0)],
                 [Sym('stroke'), [Sym('width'), 0.254], [Sym('type'), Sym('default')]],
                 [Sym('fill'), [Sym('type'), Sym('background')]]]])
    sym.append([Sym('symbol'), name + '_1_1'] + pins)
    sym.append([Sym('embedded_fonts'), Sym('no')])
    return sym


def write_symbol_lib(path, symbols):
    root = [Sym('kicad_symbol_lib'), [Sym('version'), KICAD_SYM_VERSION], [Sym('generator'), 'ha_panel_gen'],
            [Sym('generator_version'), '9.0']] + symbols
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(dump(root) + '\n')


# ---------------------------------------------------------------- geometry
def xform(X, Y, rot, x, y):
    xs, ys = x, -y
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return (snap(X + xs * c + ys * s), snap(Y - xs * s + ys * c))


def outward(rot, ang):
    a = math.radians(ang + rot)
    return (-round(math.cos(a)), round(math.sin(a)))


# ---------------------------------------------------------------- schematic sheet
class Sheet:
    def __init__(self, name, filename, title, paper='A3', page=1, project=None):
        self.name, self.filename, self.title, self.paper, self.page = name, filename, title, paper, page
        self.project = project
        self.uuid = U('sheetfile/' + project.name + '/' + filename)
        self.items = []
        self.libsyms = {}
        self.syms = []          # (ref, lib_id, value, pinmap)
        self.inst_path = None   # set by project
        self.nets_used = {}

    # -- library management
    def _lib(self, lib_id):
        if lib_id not in self.libsyms:
            self.libsyms[lib_id] = symlib.load(lib_id)
        return self.libsyms[lib_id]

    # -- primitives
    def wire(self, a, b):
        self.items.append([Sym('wire'), [Sym('pts'), [Sym('xy'), a[0], a[1]], [Sym('xy'), b[0], b[1]]],
                           [Sym('stroke'), [Sym('width'), 0], [Sym('type'), Sym('default')]], [Sym('uuid'), U()]])

    def noconnect(self, p):
        self.items.append([Sym('no_connect'), [Sym('at'), p[0], p[1]], [Sym('uuid'), U()]])

    def text(self, s, x, y, size=1.27, bold=False):
        self.items.append([Sym('text'), s, [Sym('exclude_from_sim'), Sym('no')], [Sym('at'), snap(x), snap(y), 0],
                           eff('left top', size=size, bold=bold), [Sym('uuid'), U()]])

    def rect(self, x0, y0, x1, y1):
        self.items.append([Sym('rectangle'), [Sym('start'), snap(x0), snap(y0)], [Sym('end'), snap(x1), snap(y1)],
                           [Sym('stroke'), [Sym('width'), 0.1524], [Sym('type'), Sym('dash')]],
                           [Sym('fill'), [Sym('type'), Sym('none')]], [Sym('uuid'), U()]])

    def label(self, net, p, direction, is_global):
        ang = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[direction]
        just = 'left' if ang in (0, 90) else 'right'
        if is_global:
            self.items.append([Sym('global_label'), net, [Sym('shape'), Sym('bidirectional')],
                               [Sym('at'), p[0], p[1], ang], [Sym('fields_autoplaced'), Sym('yes')], eff(just),
                               [Sym('uuid'), U()],
                               [Sym('property'), 'Intersheetrefs', '${INTERSHEET_REFS}', [Sym('at'), p[0], p[1], ang],
                                eff(just, hide=True)]])
        else:
            self.items.append([Sym('label'), net, [Sym('at'), p[0], p[1], ang], [Sym('fields_autoplaced'), Sym('yes')],
                               eff(just + ' bottom'), [Sym('uuid'), U()]])

    def power(self, lib_id, p, direction):
        """Place a power symbol (GND/+5V/+3V3/PWR_FLAG) with its pin at p, body pointing along direction."""
        lib = self._lib(lib_id)
        name = lib_id.split(':')[1]
        if name.startswith('GND'):
            rot = {(0, 1): 0, (1, 0): 90, (0, -1): 180, (-1, 0): 270}[direction]
        else:  # rail symbols draw upward
            rot = {(0, -1): 0, (-1, 0): 90, (0, 1): 180, (1, 0): 270}[direction]
        props = {pr[1]: pr for pr in findall(lib, 'property')}
        ref = '#PWR' if name != 'PWR_FLAG' else '#FLG'
        idx = self.project.next_power(ref)
        refname = '%s%03d' % (ref, idx)
        txt_off = {(0, 1): (0, 3.81), (0, -1): (0, -3.81), (1, 0): (5.08, 0), (-1, 0): (-5.08, 0)}[direction]
        tp = (snap(p[0] + txt_off[0]), snap(p[1] + txt_off[1]))
        value = props['Value'][2]
        node = [Sym('symbol'), [Sym('lib_id'), lib_id], [Sym('at'), p[0], p[1], rot], [Sym('unit'), 1],
                [Sym('exclude_from_sim'), Sym('no')], [Sym('in_bom'), Sym('yes')], [Sym('on_board'), Sym('yes')],
                [Sym('dnp'), Sym('no')], [Sym('uuid'), U()],
                [Sym('property'), 'Reference', refname, [Sym('at'), tp[0], tp[1], rot % 180], eff(hide=True)],
                [Sym('property'), 'Value', value, [Sym('at'), tp[0], tp[1], rot % 180], eff(hide=name.startswith('GND'))],
                [Sym('property'), 'Footprint', '', [Sym('at'), p[0], p[1], 0], eff(hide=True)],
                [Sym('property'), 'Datasheet', '', [Sym('at'), p[0], p[1], 0], eff(hide=True)]]
        for pin in symlib.pins(lib):
            node.append([Sym('pin'), pin['number'], [Sym('uuid'), U()]])
        node.append(self._instances(refname, 1))
        self.items.append(node)

    def _instances(self, ref, unit):
        return [Sym('instances'), [Sym('project'), self.project.name,
                                   [Sym('path'), self.inst_path, [Sym('reference'), ref], [Sym('unit'), unit]]]]

    # -- components
    def comp(self, ref, lib_id, value, at, rot=0, nets=None, footprint='', fields=None, dnp=False, in_bom=True,
             stub=2.54, datasheet=None, value_pos=None, hide_value=False, ref_pos=None, unit=1):
        """Place a symbol; connect each pin (by number) to a net via stub + label/power symbol.
        nets: {pin_number: netname | None (no-connect) | '~' (leave open, no flag)}."""
        lib = self._lib(lib_id)
        nets = nets or {}
        X, Y = snap(at[0]), snap(at[1])
        props = {pr[1]: pr for pr in findall(lib, 'property')}
        ds = datasheet if datasheet is not None else (props['Datasheet'][2] if 'Datasheet' in props else '~')
        pins = symlib.pins(lib, unit=unit)
        # bbox of pins for field placement
        pts = [xform(X, Y, rot, p['x'], p['y']) for p in pins] or [(X, Y)]
        minx, maxx = min(q[0] for q in pts), max(q[0] for q in pts)
        miny, maxy = min(q[1] for q in pts), max(q[1] for q in pts)
        horiz2 = len(pins) == 2 and abs(pts[0][1] - pts[1][1]) < 0.01
        two = len(pins) == 2 and abs(abs(pins[0]['angle'] - pins[1]['angle']) - 180) < 1
        bb = symlib.body_bbox(lib, unit=unit)
        if bb is not None:
            corners = [xform(X, Y, rot, bx, by) for bx in (bb[0], bb[2]) for by in (bb[1], bb[3])]
            bminx, bmaxx = min(c[0] for c in corners), max(c[0] for c in corners)
            bminy, bmaxy = min(c[1] for c in corners), max(c[1] for c in corners)
        else:
            bminx, bmaxx, bminy, bmaxy = minx, maxx, miny, maxy
        just_ref = just_val = None
        if two or len(pins) <= 1:
            if ref_pos is None:
                ref_pos = (X, snap(miny - 2.54)) if horiz2 else (snap(maxx + 1.27), snap(miny - 1.27))
            if value_pos is None:
                value_pos = (X, snap(maxy + 3.81)) if horiz2 else (snap(maxx + 1.27), snap(maxy + 2.54))
            just_ref = just_val = None if horiz2 else 'left'
        else:
            # multi-pin: sides with pins (sheet coords)
            def side_has(test):
                return any(test(xform(X, Y, rot, p['x'], p['y'])) for p in pins)
            top_pins = side_has(lambda q: abs(q[1] - bminy) < 0.01)
            bot_pins = side_has(lambda q: abs(q[1] - bmaxy) < 0.01)
            top_off = 0 if not top_pins else 2.54
            just_ref = just_val = 'left'
            if ref_pos is None:
                ref_pos = (snap(bminx + 2.54), snap(bminy - top_off - (2.54 if not bot_pins else 5.08)))
                just_ref = 'left'
            if value_pos is None:
                if not bot_pins:
                    value_pos = (snap(bminx + 2.54), snap(bmaxy + 2.54))
                else:
                    value_pos = (snap(bminx + 2.54), snap(bminy - top_off - 2.54))
                just_val = 'left'
        node = [Sym('symbol'), [Sym('lib_id'), lib_id], [Sym('at'), X, Y, rot], [Sym('unit'), unit],
                [Sym('exclude_from_sim'), Sym('no')], [Sym('in_bom'), Sym('yes' if in_bom else 'no')],
                [Sym('on_board'), Sym('yes')], [Sym('dnp'), Sym('yes' if dnp else 'no')],
                [Sym('uuid'), U('sym/' + self.project.name + '/' + self.filename + '/' + ref)],
                [Sym('property'), 'Reference', ref, [Sym('at'), ref_pos[0], ref_pos[1], rot % 180], eff(just_ref)],
                [Sym('property'), 'Value', value, [Sym('at'), value_pos[0], value_pos[1], rot % 180],
                 eff(just_val, hide=hide_value)],
                [Sym('property'), 'Footprint', footprint, [Sym('at'), X, Y, 0], eff(hide=True)],
                [Sym('property'), 'Datasheet', ds or '~', [Sym('at'), X, Y, 0], eff(hide=True)]]
        for k, v in (fields or {}).items():
            node.append([Sym('property'), k, v, [Sym('at'), X, Y, 0], eff(hide=True)])
        for p in pins:
            node.append([Sym('pin'), p['number'], [Sym('uuid'), U()]])
        node.append(self._instances(ref, unit))
        self.items.append(node)
        self.syms.append((ref, lib_id, value, nets))
        drawn = {}
        for p in pins:
            num = p['number']
            if num not in nets:
                if p['type'] == 'no_connect':
                    continue
                raise KeyError('%s pin %s (%s) has no net assignment' % (ref, num, p['name']))
            net = nets[num]
            pp = xform(X, Y, rot, p['x'], p['y'])
            if pp in drawn:
                if drawn[pp] != net:
                    raise ValueError('%s stacked pins at %s on different nets %s/%s' % (ref, pp, drawn[pp], net))
                continue
            drawn[pp] = net
            if net is None:
                if p['type'] != 'no_connect':
                    self.noconnect(pp)
                continue
            if net == '~':
                continue
            d = outward(rot, p['angle'])
            end = (snap(pp[0] + d[0] * stub), snap(pp[1] + d[1] * stub))
            self.wire(pp, end)
            self.attach(net, end, d)

    def attach(self, net, end, d):
        self.nets_used.setdefault(net, 0)
        self.nets_used[net] += 1
        if net == 'GND':
            self.power('power:GND', end, d)
        elif net == '+5V':
            self.power('power:+5V', end, d)
        elif net == '+3V3':
            self.power('power:+3V3', end, d)
        elif net == '+20V':
            self.power('ha_panel:+20V', end, d)
        else:
            self.label(net, end, d, self.project.is_global(net))

    def pwr_flag(self, net, at, direction=(0, -1)):
        p = (snap(at[0]), snap(at[1]))
        self.power('power:PWR_FLAG', p, direction)
        # short stub to a label of the net, pointing the opposite way
        d = (-direction[0], -direction[1])
        end = (snap(p[0] + d[0] * 2.54), snap(p[1] + d[1] * 2.54))
        self.wire(p, end)
        self.attach(net, end, d)

    # -- output
    def sexpr(self, root=False):
        tb = [Sym('title_block'), [Sym('title'), self.title], [Sym('date'), self.project.date],
              [Sym('rev'), self.project.rev], [Sym('company'), self.project.company]]
        for i, c in enumerate(self.project.comments, 1):
            tb.append([Sym('comment'), i, c])
        out = [Sym('kicad_sch'), [Sym('version'), KICAD_SCH_VERSION], [Sym('generator'), 'eeschema'],
               [Sym('generator_version'), '9.0'], [Sym('uuid'), self.uuid], [Sym('paper'), self.paper], tb,
               [Sym('lib_symbols')] + list(self.libsyms.values())]
        out += self.items
        if root:
            out.append([Sym('sheet_instances'), [Sym('path'), '/', [Sym('page'), '1']]])
        out.append([Sym('embedded_fonts'), Sym('no')])
        return out


class Project:
    def __init__(self, name, outdir, title, date, rev, company, comments=()):
        self.name, self.outdir, self.title = name, outdir, title
        self.date, self.rev, self.company, self.comments = date, rev, company, list(comments)
        self._pwr = {}
        self.sheets = []
        self.root = Sheet('Root', name + '.kicad_sch', title, paper='A4', page=1, project=self)
        self.root.inst_path = '/' + self.root.uuid
        self.global_nets = set()

    def next_power(self, ref):
        self._pwr[ref] = self._pwr.get(ref, 0) + 1
        return self._pwr[ref]

    def is_global(self, net):
        return net in self.global_nets

    def add_sheet(self, name, filename, title, paper='A3'):
        sh = Sheet(name, filename, title, paper=paper, page=len(self.sheets) + 2, project=self)
        sh.sheet_sym_uuid = U('sheetsym/' + self.name + '/' + filename)
        sh.inst_path = '/' + self.root.uuid + '/' + sh.sheet_sym_uuid
        self.sheets.append(sh)
        return sh

    def _sheet_symbols(self):
        items = []
        x, y = 25.4, 50.8
        for i, sh in enumerate(self.sheets):
            sx, sy = x + (i % 3) * 63.5, y + (i // 3) * 40.64
            items.append([Sym('sheet'), [Sym('at'), sx, sy], [Sym('size'), 50.8, 25.4],
                          [Sym('exclude_from_sim'), Sym('no')], [Sym('in_bom'), Sym('yes')], [Sym('on_board'), Sym('yes')],
                          [Sym('dnp'), Sym('no')], [Sym('fields_autoplaced'), Sym('yes')],
                          [Sym('stroke'), [Sym('width'), 0.1524], [Sym('type'), Sym('solid')]],
                          [Sym('fill'), [Sym('color'), 0, 0, 0, 0.0]], [Sym('uuid'), sh.sheet_sym_uuid],
                          [Sym('property'), 'Sheetname', sh.name, [Sym('at'), sx, snap(sy - 0.7), 0], eff('left bottom')],
                          [Sym('property'), 'Sheetfile', sh.filename, [Sym('at'), sx, snap(sy + 25.4 + 0.6), 0],
                           eff('left top')],
                          [Sym('instances'), [Sym('project'), self.name,
                                              [Sym('path'), '/' + self.root.uuid, [Sym('page'), str(sh.page)]]]]])
        return items

    def write_project_files(self, sym_libs=(), fp_libs=()):
        """Minimal .kicad_pro plus project lib tables (paths relative to ${KIPRJMOD})."""
        import json
        pro = {'board': {}, 'boards': [], 'libraries': {'pinned_footprint_libs': [], 'pinned_symbol_libs': []},
               'meta': {'filename': self.name + '.kicad_pro', 'version': 1},
               'net_settings': {}, 'pcbnew': {}, 'schematic': {'legacy_lib_dir': '', 'legacy_lib_list': []},
               'sheets': [[self.root.uuid, 'Root']] + [[sh.sheet_sym_uuid, sh.name] for sh in self.sheets],
               'text_variables': {}}
        with open(os.path.join(self.outdir, self.name + '.kicad_pro'), 'w', encoding='utf-8') as f:
            json.dump(pro, f, indent=2)
            f.write('\n')
        for fn, head, libs in (('sym-lib-table', 'sym_lib_table', sym_libs), ('fp-lib-table', 'fp_lib_table', fp_libs)):
            lines = ['(%s' % head, '  (version 7)']
            for nick, rel, descr in libs:
                lines.append('  (lib (name "%s")(type "KiCad")(uri "${KIPRJMOD}/%s")(options "")(descr "%s"))'
                             % (nick, rel, descr))
            lines.append(')')
            with open(os.path.join(self.outdir, fn), 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')

    def write(self):
        os.makedirs(self.outdir, exist_ok=True)
        self.root.items = self._sheet_symbols() + self.root.items
        with open(os.path.join(self.outdir, self.root.filename), 'w', encoding='utf-8') as f:
            f.write(dump(self.root.sexpr(root=True)) + '\n')
        for sh in self.sheets:
            with open(os.path.join(self.outdir, sh.filename), 'w', encoding='utf-8') as f:
                f.write(dump(sh.sexpr()) + '\n')

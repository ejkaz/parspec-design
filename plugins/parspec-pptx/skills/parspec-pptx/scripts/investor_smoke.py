"""Independently verify local fictional investor / board gallery artifacts.

The oracle reads the caller's v4 fixture, never the gallery manifest or builder
calculations. It checks native chart caches against independently derived data,
their embedded workbooks, financial-table matrices, per-slide number provenance,
type floors, fiscal labels and public-repository staging. Mutation probes run by
default. This is a structural / data check, not visual or brand acceptance.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
import subprocess
import sys

from openpyxl import load_workbook
from openpyxl.utils.cell import range_boundaries
from pptx import Presentation
from pptx.oxml.ns import qn

SKILL = Path(__file__).resolve().parents[1]
REPO = SKILL.parents[3]
sys.path.insert(0, str(SKILL))
from assets.brand import load as load_brand
from assets.house import DEFAULT_PROFILE, TEMPLATE_DIR

D = Decimal
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}
BOARD_IDS = ['BD01', 'BD01a'] + [f'BD{i:02}' for i in range(2, 17)]
INVESTOR_IDS = [f'IN{i:02}' for i in range(1, 20)]
CHART_SLIDES = {'BD03', 'BD04', 'BD07', 'BD08', 'BD09', 'BD10',
                'IN03', 'IN05', 'IN07', 'IN08', 'IN10', 'IN14', 'BD16', 'IN19'}
TABLE_SLIDES = {'BD01a', 'BD02', 'BD05', 'BD06', 'BD07', 'BD08',
                'BD09', 'BD10', 'BD12', 'BD13', 'BD14', 'IN04',
                'IN09', 'IN12', 'IN14', 'IN15', 'IN16', 'IN18'}
NUMBER = re.compile(r'(?<![A-Za-z0-9_])\d+(?:,\d{3})*(?:\.\d+)?')
MONTH = re.compile(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+20\d{2}\b', re.I)
FONT = load_brand().font


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def rounded(value, places=2):
    return D(str(value)).quantize(D(1).scaleb(-places), rounding=ROUND_HALF_UP)


def fmt(value, places=1):
    if value is None:
        return '—'
    v = rounded(value, places)
    return f'({abs(v):.{places}f})' if v < 0 else f'{v:.{places}f}'


def pct(value, places=0):
    return fmt(value * 100, places) + '%'


def multiple(value):
    return fmt(value) + '×'


def independent(d):
    """Financial operands, Decimal rounding and inclusive statistics only."""
    p, f = d['pnl'], d['fy27_plan']
    gp = [rounded(rev * margin) for rev, margin in zip(p['revenue'], p['gross_margin'])]
    gp27 = [rounded(rev * margin) for rev, margin in zip(f['revenue'], f['gross_margin'])]
    ebitda = [rounded(g - o) for g, o in zip(gp, p['opex'])]
    cor = [rev - g for rev, g in zip(p['revenue'], gp)]
    weights = [rounded(row['amount'] * row['win_rate']) for row in d['pipeline_q4_fy26']['stages']]
    arr = d['arr_history']['arr']
    peer = sorted(row['valuation_arr'] for row in d['comps'])
    growths = sorted(row['growth'] for row in d['comps'])
    cv = d['customer_value']
    value_total = sum(row['value_k'] for row in cv['benefits'])
    require(value_total == cv['total_k'], 'v4 customer benefits do not reconcile to total')
    value_ratio = value_total / cv['parspec_cost_k']
    require(rounded(value_ratio, 1) == cv['roi_multiple'], 'v4 customer value / subscription ratio')
    bridge = d['ebitda_to_cash_q3_fy26']
    bridge_values = [bridge[key] for key in ('ebitda', 'working_capital', 'deferred_revenue', 'capex', 'interest', 'other')]
    bridge_total = sum(bridge_values)
    require(bridge_total == bridge['net_burn'], 'v4 EBITDA-to-cash bridge does not reconcile')
    require(bridge_total == -d['plan_vs_actual_q3_fy26'][4]['actual'], 'v4 cash bridge does not tie to BD05 net burn')
    require(bridge['ebitda'] == ebitda[2], 'v4 cash bridge does not tie to Q3 FY26 EBITDA')
    def quantile(frac):
        rank = D(len(peer) - 1) * frac
        lo = int(rank)
        return peer[lo] + (rank - lo) * (peer[min(lo + 1, len(peer) - 1)] - peer[lo])
    return dict(gp=gp, gp27=gp27, ebitda=ebitda, cor=cor, weights=weights,
                weighted=sum(weights), coverage=sum(weights) / d['pipeline_q4_fy26']['target_net_new'],
                median=(peer[3] + peer[4]) / 2, growth_median=(growths[3] + growths[4]) / 2,
                p25=quantile(D('.25')), p75=quantile(D('.75')),
                multiple=d['round']['pre_money'] / d['arr_bridge_q3_fy26']['end'],
                yoy=arr[8] / arr[4] - 1, two_year=arr[8] / arr[0],
                net_new=[arr[i] - arr[i - 1] for i in range(6, len(arr))],
                value_total=value_total, value_ratio=value_ratio,
                bridge_values=bridge_values + [bridge_total])


def numeric_allowances(d, c):
    """Per-page source branches plus named computations, never global values."""
    branch = {
        'BD01': [], 'BD01a': ['agenda', 'decisions'],
        'BD02': ['arr_bridge_q3_fy26', 'unit_economics', 'pnl', 'plan_vs_actual_q3_fy26', 'quarter_kpis'],
        'BD03': ['arr_bridge_q3_fy26', 'unit_economics'],
        'BD04': ['arr_history'], 'BD05': ['plan_vs_actual_q3_fy26'],
        'BD06': ['pnl'], 'BD07': ['cash_runway', 'plan_vs_actual_q3_fy26'],
        'BD08': ['cases'], 'BD09': ['headcount'],
        'BD10': ['pipeline_q4_fy26'], 'BD11': ['decisions'],
        'BD12': ['pnl'], 'BD13': ['cash_runway', 'decisions'],
        'BD14': ['risks'], 'BD15': ['agenda'], 'BD16': ['ebitda_to_cash_q3_fy26'],
        'IN01': [], 'IN02': ['arr_history', 'unit_economics', 'pnl', 'market'],
        'IN03': ['arr_history'], 'IN04': ['cohort_ndr', 'unit_economics'],
        'IN05': ['unit_economics'], 'IN06': ['market', 'arr_bridge_q3_fy26'],
        'IN07': ['competitive_2x2'], 'IN08': ['comps', 'round', 'arr_history'],
        'IN09': ['comps', 'round', 'arr_history'], 'IN10': ['round'],
        'IN11': ['round', 'arr_bridge_q3_fy26'], 'IN12': [],
        'IN13': [], 'IN14': ['arr_history', 'pnl', 'fy27_plan'],
        'IN15': ['customer_outcomes'], 'IN16': ['customer_value'], 'IN17': ['team'],
        'IN18': ['product_mechanism'], 'IN19': ['ebitda_to_cash_q3_fy26'],
    }
    allowed = {sid: set() for sid in branch}
    def add(sid, value, as_rate=False):
        if isinstance(value, dict):
            for key, item in value.items(): add(sid, item, as_rate or key in {'ndr', 'grr', 'gm', 'gross_margin', 'growth', 'win_rate', 'pct'})
        elif isinstance(value, (list, tuple)):
            for item in value: add(sid, item, as_rate)
        elif isinstance(value, (int, float, D)) and not isinstance(value, bool):
            v = abs(D(str(value)))
            for places in (0, 1, 2, 3): allowed[sid].add(abs(rounded(v, places)))
            allowed[sid].add(v)
            if as_rate or 0 <= v <= 1:
                for places in (0, 1, 2): allowed[sid].add(abs(rounded(v * 100, places)))
        elif isinstance(value, str):
            for match in NUMBER.finditer(value): allowed[sid].add(D(match.group().replace(',', '')))
    for sid, fields in branch.items():
        # Page indices, sequence numbers, fiscal quarter numbers, explicit
        # calendar years and Year-1 / two-year references are structural.
        add(sid, [1, 2, 3, 4, 2026, 2027])
        add(sid, BOARD_IDS.index(sid) + 1 if sid in BOARD_IDS else INVESTOR_IDS.index(sid) + 1)
        for field in fields: add(sid, d[field])
    b, cash, hc = d['arr_bridge_q3_fy26'], d['cash_runway'], d['headcount']
    add('BD01a', [sum(x['minutes'] for x in d['agenda']), list(range(1, len(d['agenda']) + 1))])
    for sid in ('BD02', 'BD03'):
        add(sid, [b['end'] - b['start'], b['new'] + b['expansion'], b['contraction'] + b['churn'],
                  d['plan_vs_actual_q3_fy26'][0]['plan'] - b['start']])
    add('BD04', [c['yoy'], (d['arr_history']['arr'][-1] / d['arr_history']['arr'][9] - 1),
                 d['arr_history']['arr'][-1] - d['arr_history']['arr'][9]])
    add('BD05', [r['actual'] - r['plan'] for r in d['plan_vs_actual_q3_fy26']])
    for sid in ('BD06', 'BD12'):
        add(sid, [c['gp'], c['ebitda'], c['cor'], sum(d['pnl']['revenue']), sum(c['gp']),
                  sum(d['pnl']['opex']), sum(c['ebitda']), sum(c['cor']),
                  d['pnl']['revenue'][-1] - d['pnl']['revenue'][0]])
        add(sid, [g / r for g, r in zip(c['gp'], d['pnl']['revenue'])])
        add(sid, [e / r for e, r in zip(c['ebitda'], d['pnl']['revenue'])], as_rate=True)
        add(sid, [sum(c['gp']) / sum(d['pnl']['revenue']), sum(c['ebitda']) / sum(d['pnl']['revenue'])], as_rate=True)
        add(sid, [d['pnl']['revenue'][j] / d['pnl']['revenue'][j - 1] - 1 for j in range(1, 4)])
    for sid in ('BD07', 'BD13'):
        add(sid, [sum(cash['net_burn']), sum(cash['net_burn']) / len(cash['net_burn']),
                  [v - cash['debt_draw']['amount'] for v in cash['cash_end'][3:]]])
    for field in ('start', 'joiners', 'leavers', 'end', 'plan_q4'): add('BD09', sum(hc[field]))
    add('BD09', [sum(hc['end']) - sum(hc['start']), sum(hc['plan_q4']) - sum(hc['end'])])
    add('BD10', [c['weights'], c['weighted'], c['coverage'], sum(c['weights'][2:]),
                 sum(s['amount'] for s in d['pipeline_q4_fy26']['stages'])])
    add('IN02', [c['two_year'], (d['unit_economics']['gross_margin_trend']['gm'][-1] - d['unit_economics']['gross_margin_trend']['gm'][0]) * 100,
                 d['market']['som'] * 1000])
    add('IN03', c['two_year'])
    add('IN05', (d['unit_economics']['gross_margin_trend']['gm'][-1] - d['unit_economics']['gross_margin_trend']['gm'][0]) * 100)
    m = d['market']
    add('IN06', [m['som'] * 1000, m['sam'] / m['tam'], b['end'] / (m['som'] * 1000)])
    for sid in ('IN08', 'IN09'):
        add(sid, [c['multiple'], c['median'], c['growth_median'], c['p25'], c['p75'], c['yoy'],
                  [row['valuation_arr'] - c['median'] for row in d['comps']], c['multiple'] - c['median']])
    r = d['round']
    add('IN10', [r['pre_money'] + r['raise'], r['raise'] / (r['pre_money'] + r['raise']),
                 [r['raise'] * use['pct'] for use in r['use_of_funds']]])
    add('IN14', [c['net_new'], sum(c['net_new'][:4]), sum(c['net_new'][4:]), c['gp'], c['gp27'],
                 sum(c['gp']), sum(c['gp27']), sum(d['pnl']['revenue']), sum(d['fy27_plan']['revenue'])])
    revenues = d['pnl']['revenue'] + d['fy27_plan']['revenue']
    profits = c['gp'] + c['gp27']
    add('IN14', [g / rev for g, rev in zip(profits, revenues)])
    add('IN14', [sum(c['gp']) / sum(d['pnl']['revenue']), sum(c['gp27']) / sum(d['fy27_plan']['revenue'])])
    add('BD03', 15)  # Explicit, labeled truncated value-axis minimum.
    add('BD09', 90)
    add('IN16', [c['value_total'], c['value_ratio']])
    for sid in ('BD16', 'IN19'): add(sid, c['bridge_values'])
    return allowed


def frames(slide):
    for shape in slide.shapes:
        if shape.has_text_frame:
            yield shape, shape.text_frame
        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    yield shape, cell.text_frame


def fiscal_contract(text, sid, nearby=''):
    for match in re.finditer(r'\bQ[1-4]\b', text):
        require(re.match(r'\s+FY\d{2,4}\b', text[match.end():]), f'{sid}: bare quarter in {text!r}')
    for match in MONTH.finditer(text):
        # Definitions may state the fiscal-year end in one sentence. Main
        # calendar-month labels must carry a fiscal-quarter label in that box.
        month_name, year_text = match.group().split()
        month = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'].index(month_name[:3].lower()) + 1
        year = int(year_text); fy = year if month >= 2 else year - 1
        quarter = ((month - 2) % 12) // 3 + 1
        expected = f'Q{quarter} FY{str(fy)[-2:]}'
        require(sid in {'BD12', 'IN12'} or expected in text + ' ' + nearby,
                f'{sid}: calendar month lacks fiscal quarter in {text!r}')


def text_contract(slide, sid, allowed):
    footer_found = False
    for shape, frame in frames(slide):
        text = frame.text
        if not text.strip(): continue
        footer = shape.top / 914400 * 128 >= 672
        footer_found |= footer and '©' in text
        floor = 11 if footer else 13 if sid in {'BD12', 'IN09'} else 14
        for paragraph in frame.paragraphs:
            for run in paragraph.runs:
                if not run.text: continue
                size = run.font.size or paragraph.font.size
                require(size is not None, f'{sid}: inherited font size is not measurable: {run.text!r}')
                require(run.font.name == FONT, f'{sid}: nonbrand text font {run.font.name!r}')
                require(size.pt * 128 / 72 + .02 >= floor,
                        f'{sid}: {size.pt * 128 / 72:.2f}px below {floor}px: {run.text!r}')
                if sid not in {'BD12', 'IN12'}:
                    require(not run._r.xpath('./a:rPr[@baseline>0]'), f'{sid}: superscript run')
        if not footer:
            # A tile may split its calendar value and fiscal context across
            # adjacent text boxes. Require the associated label in that region,
            # rather than accepting an unrelated fiscal label elsewhere.
            nearby = ' '.join(other.text for other in slide.shapes
                              if other.has_text_frame and other is not shape
                              and abs(other.top - shape.top) / 914400 * 128 <= 130
                              and other.left < shape.left + shape.width
                              and shape.left < other.left + other.width)
            if sid == 'BD07' and 'fiscal quarters shown above' in text.lower():
                nearby += ' ' + ' '.join(other.text for other in slide.shapes
                                        if other.has_text_frame and other.name.startswith('fiscal-band:'))
            fiscal_contract(text, sid, nearby)
            if sid not in {'BD12', 'IN12'}:
                require(not re.search(r'\bn\s*=|\bfootnote\b|\bmethodology\b|\bsource\s*:', text, re.I),
                        f'{sid}: main-slide footnote / methodology text')
        for token in NUMBER.findall(text):
            require(D(token.replace(',', '')) in allowed, f'{sid}: unsourced numeric token {token!r} in {text!r}')
    require(footer_found, f'{sid}: copyright footer missing')


def values_equal(actual, expected, context):
    require(len(actual) == len(expected), f'{context}: length {len(actual)} != {len(expected)}')
    for i, (a, e) in enumerate(zip(actual, expected)):
        if e is None:
            require(a is None, f'{context}[{i}]: expected blank, got {a}')
        else:
            require(a is not None and abs(D(str(a)) - D(str(e))) <= D('0.000000001'),
                    f'{context}[{i}]: {a} != {e}')


def chart_expected(sid, d, c):
    arr = d['arr_history']['arr']
    if sid in {'BD04', 'IN03', 'IN14'}:
        vs, actual = (arr, 9) if sid == 'IN03' else (arr[6:], 3)
        return [('Actual', [v if j < actual else None for j, v in enumerate(vs)]),
                ('Forecast', [v if j >= actual else None for j, v in enumerate(vs)])]
    if sid == 'BD07':
        vals = [d['plan_vs_actual_q3_fy26'][5]['actual']] + d['cash_runway']['cash_end']
        return [('Actual', [vals[0]] + [None] * (len(vals) - 1)), ('Forecast', [None] + vals[1:])]
    if sid in {'BD03', 'BD09', 'BD16', 'IN19'}:
        if sid == 'BD03':
            b = d['arr_bridge_q3_fy26']
            values = [b[k] for k in ('start', 'new', 'expansion', 'contraction', 'churn', 'end')]
            totals = {0, 5}
        elif sid == 'BD09':
            h = d['headcount']
            values = [sum(h['start']), sum(h['joiners']), -sum(h['leavers']), sum(h['end']), sum(h['plan_q4'])]
            totals = {0, 3, 4}
        else:
            values = c['bridge_values']; totals = {0, len(values) - 1}
        base, movement, running = [], [], D(0)
        for index, value in enumerate(values):
            if index in totals:
                base.append(D(0)); movement.append(value); running = value
            else:
                low, high = sorted((running, running + value))
                # OOXML stacks positive and negative series separately. Below
                # zero, the hidden base is the endpoint nearest zero and the
                # movement is negative, even for a favorable semantic delta.
                if high <= 0:
                    base.append(high); movement.append(low - high)
                else:
                    require(low >= 0, f'{sid}: cross-zero bridge needs a split-series oracle')
                    base.append(low); movement.append(high - low)
                running += value
        return [('Hidden base', base), ('Movement', movement)]
    if sid == 'BD08': return [('Value', [row['min_cash'] for row in d['cases']])]
    if sid == 'BD10': return [(s['stage'], [v]) for s, v in zip(d['pipeline_q4_fy26']['stages'], c['weights'])]
    if sid == 'IN05': return [('Gross margin', d['unit_economics']['gross_margin_trend']['gm'])]
    if sid == 'IN10': return [('Allocation', [row['pct'] for row in d['round']['use_of_funds']])]
    if sid == 'IN07': return [(p['name'], ([p['x']], [p['y']])) for p in d['competitive_2x2']['players']]
    if sid == 'IN08':
        rows = [(p['name'], ([p['growth']], [p['valuation_arr']])) for p in d['comps']]
        rows += [('Parspec', ([c['yoy']], [c['multiple']])),
                 ('Growth median', ([c['growth_median']] * 2, [D(0), D(20)])),
                 ('Valuation median', ([D('.15'), D('.95')], [c['median']] * 2))]
        return rows
    raise AssertionError('unexpected chart page ' + sid)


def category_expected(sid, d):
    if sid in {'BD04', 'IN14'}: return d['arr_history']['quarters'][6:]
    if sid == 'IN03': return d['arr_history']['quarters']
    if sid == 'BD03': return ['Start\nQ3 FY26', 'New logos', 'Expansion', 'Contraction', 'Churn', 'End\nQ3 FY26']
    if sid == 'BD09': return ['Start\nQ3 FY26', 'Joiners', 'Leavers', 'End\nQ3 FY26', 'Plan\nQ4 FY26']
    if sid in {'BD16', 'IN19'}: return ['EBITDA', 'Working capital', 'Deferred revenue', 'Software & capex', 'Interest', 'Other', 'Net burn']
    if sid == 'BD08': return [row['case'] for row in d['cases']]
    if sid == 'BD10': return ['Weighted pipeline']
    if sid == 'IN05': return d['unit_economics']['gross_margin_trend']['quarters']
    if sid == 'IN10': return [row['use'] for row in d['round']['use_of_funds']]
    if sid == 'BD07':
        return ['Oct'] + [label.split()[0] for label in d['cash_runway']['months']]
    return None


def workbook_contract(chart, sid):
    workbook = load_workbook(BytesIO(chart.part.chart_workbook.xlsx_part.blob), data_only=True)
    for ref in chart._chartSpace.xpath('.//c:numRef | .//c:strRef'):
        formula = ref.find(qn('c:f')).text
        sheet_name, area = formula.rsplit('!', 1)
        sheet_name = sheet_name.strip("'").replace("''", "'")
        x0, y0, x1, y1 = range_boundaries(area.replace('$', ''))
        values = [workbook[sheet_name].cell(y, x).value for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]
        cache = ref.find(qn('c:numCache'))
        numeric = cache is not None
        if cache is None: cache = ref.find(qn('c:strCache'))
        require(cache is not None, f'{sid}: cache missing for {formula}')
        cached = {int(pt.get('idx')): pt.find(qn('c:v')).text for pt in cache.findall(qn('c:pt'))}
        require(int(cache.find(qn('c:ptCount')).get('val')) == len(values), f'{sid}: cache/workbook point count')
        for index, value in enumerate(values):
            if value is None:
                require(index not in cached or cached[index] in {'', None}, f'{sid}: nonblank cache for workbook blank')
            elif numeric:
                values_equal([cached.get(index)], [value], f'{sid}: workbook {formula}[{index}]')
            else:
                require(cached.get(index) == str(value), f'{sid}: workbook text/cache mismatch {formula}')


def chart_contract(slide, sid, d, c, allowed):
    charts = [shape for shape in slide.shapes if shape.has_chart]
    require(len(charts) == (1 if sid in CHART_SLIDES else 0), f'{sid}: native chart count {len(charts)}')
    # Chart-looking names must actually reference editable chart objects.
    chart_primitives = {'column_actual_forecast', 'waterfall', 'line_trend',
                        'combo_bar_line', 'stacked_bar', 'scatter_labeled', 'doughnut', 'bar_ranked'}
    for shape in slide.shapes:
        if shape.name.startswith('native:') and shape.name.split(':', 1)[1] in chart_primitives:
            require(shape.has_chart, f'{sid}: chart primitive is not a native chart')
    for shape in charts:
        chart = shape.chart
        require(not chart.has_title, f'{sid}: internal chart title')
        require(len(chart._chartSpace.xpath('.//c:valAx/c:majorGridlines')) <= 1, f'{sid}: excessive horizontal gridlines')
        require(not chart._chartSpace.xpath('.//c:valAx/c:minorGridlines'), f'{sid}: minor horizontal gridlines')
        expected = chart_expected(sid, d, c)
        by_name = {series.name: series for series in chart.series}
        if sid in {'BD03', 'BD09', 'BD16', 'IN19'} and 'Label anchors' in by_name:
            base, moves = expected[0][1], expected[1][1]
            anchors = [max(b, b + v) for b, v in zip(base, moves)]
            expected.append(('Label anchors', anchors))
        categories = category_expected(sid, d)
        if categories is not None:
            actual_categories = [category.label for category in chart.plots[0].categories]
            require(actual_categories == categories, f'{sid}: chart category / fiscal label mismatch')
            for category in actual_categories: fiscal_contract(category, sid)
        require(len(chart.series) == len(expected), f'{sid}: series count')
        require(set(by_name) == {name for name, _ in expected}, f'{sid}: chart series names')
        if sid in {'BD16', 'IN19'}:
            movement = by_name['Movement']
            # LibreOffice ignores explicit negative dPt colors unless the
            # actual point has inversion disabled. A series-level flag alone
            # does not preserve fills when points override series formatting.
            for index, value in enumerate(movement.values):
                if value >= 0: continue
                points = movement._element.xpath(f'./c:dPt[c:idx[@val="{index}"]]')
                require(len(points) == 1 and points[0].xpath('./c:invertIfNegative[@val="0"]'),
                        f'{sid}: visible negative point {index} must explicitly disable fill inversion')
        for name, values in expected:
            series = by_name[name]
            if sid in {'IN07', 'IN08'}:
                x_cache = series._element.find(qn('c:xVal')).find(qn('c:numRef')).find(qn('c:numCache'))
                x_values = [None] * int(x_cache.find(qn('c:ptCount')).get('val'))
                for point in x_cache.findall(qn('c:pt')):
                    x_values[int(point.get('idx'))] = point.find(qn('c:v')).text
                values_equal(x_values, values[0], f'{sid}/{name}/x')
                values_equal(series.values, values[1], f'{sid}/{name}/y')
            else:
                values_equal(series.values, values, f'{sid}/{name}')
        for rp in chart._chartSpace.xpath('.//a:rPr[@sz] | .//a:defRPr[@sz]'):
            require(int(rp.get('sz')) / 100 * 128 / 72 + .02 >= 14, f'{sid}: chart font below 14px')
        require(all(name == FONT for name in chart._chartSpace.xpath('.//a:latin/@typeface')), f'{sid}: nonbrand chart font')
        require(chart._chartSpace.xpath('./c:txPr//a:defRPr[@sz]'), f'{sid}: chart text size not explicit')
        if sid not in {'BD12', 'IN12'}:
            require(not chart._chartSpace.xpath('.//a:rPr[@baseline>0]'), f'{sid}: chart superscript')
        require(chart._chartSpace.xpath('.//c:dLbls'), f'{sid}: native chart data labels missing')
        for text in chart._chartSpace.xpath('.//c:rich//a:t/text()'):
            for token in NUMBER.findall(text):
                require(D(token.replace(',', '')) in allowed, f'{sid}: unsourced chart-label number {token}')
        workbook_contract(chart, sid)


def table_matrix(shape):
    return [[cell.text.replace('\v', '\n') for cell in row.cells] for row in shape.table.rows]


def pnl_expected(d, c, detail=False):
    p = d['pnl']
    rows = [('Revenue', p['revenue']), ('Gross profit', c['gp']),
            ('Gross margin', [g / r for g, r in zip(c['gp'], p['revenue'])]),
            ('Operating expenses', p['opex']), ('EBITDA', c['ebitda'])]
    if detail:
        rows.insert(1, ('Revenue growth, QoQ', [None] + [p['revenue'][i] / p['revenue'][i - 1] - 1 for i in range(1, 4)]))
        rows.insert(2, ('Cost of revenue', c['cor']))
        rows.append(('EBITDA margin', [e / r for e, r in zip(c['ebitda'], p['revenue'])]))
    result = []
    for name, values in rows:
        if name == 'Gross margin': total = sum(c['gp']) / sum(p['revenue'])
        elif name == 'EBITDA margin': total = sum(c['ebitda']) / sum(p['revenue'])
        elif 'growth' in name: total = None
        else: total = sum(values)
        percent = 'margin' in name or 'growth' in name
        result.append([name] + [('—' if value is None else pct(value, 1 if 'growth' in name else 0) if percent else fmt(value, 2 if detail else 1)) for value in [*values, total]])
    return result


def table_contract(slide, sid, d, c):
    tables = [table_matrix(s) for s in slide.shapes if s.has_table]
    if sid != 'IN17':
        require(bool(tables) == (sid in TABLE_SLIDES), f'{sid}: native table presence')
    # Measure the supported native spacing rather than assuming Montserrat's
    # proportional default digits are tabular. Restrict to financial body cells.
    metrics = load_brand().investor['financial_digit_metrics']
    for shape in slide.shapes:
        if not shape.has_table: continue
        for row in list(shape.table.rows)[1:]:
            for cell in list(row.cells)[1:]:
                if not re.fullmatch(r'[+−()0-9.,%× pt—]+', cell.text): continue
                for paragraph in cell.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if len(run.text) == 1 and run.text in '0123456789':
                            widths = metrics['bold' if run.font.bold else 'regular']
                            expected = round((max(widths)-widths[int(run.text)]) / metrics['units_per_em'] * run.font.size.pt * 100)
                            require(int(run._r.get_or_add_rPr().get('spc', '0')) == expected,
                                    f'{sid}: digit does not have native tabular advance')

    def match_rows(expected, label):
        require(any(table[1:] == expected for table in tables), f'{sid}: {label} table differs from independent source calculation')
    if sid in {'BD06', 'BD12'}: match_rows(pnl_expected(d, c, sid == 'BD12'), 'P&L')
    if sid == 'BD01a':
        expected = [[str(i + 1), a['item'], a['owner'], str(a['minutes'])] for i, a in enumerate(d['agenda'])]
        expected.append(['', 'Total', '', str(sum(a['minutes'] for a in d['agenda']))])
        match_rows(expected, 'agenda')
    if sid == 'BD05':
        expected = []
        for i, row in enumerate(d['plan_vs_actual_q3_fy26']):
            delta = row['actual'] - row['plan']
            favorable = delta > 0 if i in {0, 1, 2, 5} else delta < 0
            expected.append([row['metric'], pct(row['plan']) if i == 2 else fmt(row['plan']),
                             pct(row['actual']) if i == 2 else fmt(row['actual']),
                             ('+' if delta > 0 else '−') + (fmt(abs(delta) * 100, 0) + ' pt' if i == 2 else fmt(abs(delta))),
                             '▲ Ahead' if favorable else '▼ Behind'])
        match_rows(expected, 'plan versus actual')
    if sid == 'BD09':
        hc = d['headcount']; expected = []
        for i, name in enumerate(hc['functions']):
            expected.append([name, str(hc['start'][i]), '+' + str(hc['joiners'][i]),
                             '(' + str(hc['leavers'][i]) + ')' if hc['leavers'][i] else '—', str(hc['end'][i]), str(hc['plan_q4'][i])])
        expected.append(['Total', str(sum(hc['start'])), '+' + str(sum(hc['joiners'])), '(' + str(sum(hc['leavers'])) + ')', str(sum(hc['end'])), str(sum(hc['plan_q4']))])
        match_rows(expected, 'headcount')
    if sid == 'BD10':
        stages = d['pipeline_q4_fy26']['stages']
        expected = [[s['stage'], fmt(s['amount']), pct(s['win_rate']), fmt(v)] for s, v in zip(stages, c['weights'])]
        expected.append(['Total', fmt(sum(s['amount'] for s in stages)), '—', fmt(c['weighted'])])
        match_rows(expected, 'weighted pipeline')
    if sid == 'BD07':
        burn = d['cash_runway']['net_burn']
        match_rows([['Net burn', fmt(sum(burn)), fmt(sum(burn) / len(burn))]], 'forward burn')
    if sid == 'BD08':
        match_rows([[row['case'], fmt(row['fy27_exit_arr']), fmt(row['fy27_revenue']), row['cash_out']] for row in d['cases']], 'named cases')
    if sid == 'BD13':
        cash = d['cash_runway']; draw = cash['debt_draw']['amount']; values = cash['cash_end']
        expected = [['Cash · Jan 2027 (Q4 FY26)', fmt(values[2]), fmt(values[2])],
                    ['Cash · Feb 2027 (Q1 FY27)', fmt(values[3] - draw), fmt(values[3])],
                    ['Cash · Oct 2027 (Q3 FY27)', fmt(values[-1] - draw), fmt(values[-1])],
                    ['Net burn · next twelve months', fmt(sum(cash['net_burn'])), fmt(sum(cash['net_burn']))]]
        match_rows(expected, 'debt cash comparison')
        match_rows([['Runway', str(cash['runway_months_without_debt']), str(cash['runway_months_with_debt'])]], 'runway units')
    if sid == 'IN04':
        co = d['cohort_ndr']
        expected = [[name] + ['' if v is None else pct(v) for v in values] for name, values in zip(co['cohorts'], co['ndr'])]
        match_rows(expected, 'cohort triangle')
    if sid == 'IN09':
        peers = [(s['name'], s['growth'], s['valuation_arr']) for s in d['comps']] + [('Parspec', c['yoy'], c['multiple'])]
        expected = [[name, pct(growth, 1 if name == 'Parspec' else 0), multiple(v), ('+' if v >= c['median'] else '−') + multiple(abs(v - c['median']))] for name, growth, v in sorted(peers, key=lambda row: row[1], reverse=True)]
        match_rows(expected, 'comparables / unrounded median deltas')
    if sid == 'IN14':
        p, f, arr = d['pnl'], d['fy27_plan'], d['arr_history']['arr']
        rev, gp, nn = p['revenue'] + f['revenue'], c['gp'] + c['gp27'], c['net_new']
        expected = [['Ending ARR'] + [fmt(v) for v in arr[6:]] + [fmt(arr[9]), fmt(arr[-1])],
                    ['Net new ARR'] + [fmt(v) for v in nn] + [fmt(sum(nn[:4])), fmt(sum(nn[4:]))],
                    ['Revenue'] + [fmt(v) for v in rev] + [fmt(sum(rev[:4])), fmt(sum(rev[4:]))],
                    ['Gross profit'] + [fmt(v) for v in gp] + [fmt(sum(gp[:4])), fmt(sum(gp[4:]))],
                    ['Gross margin'] + [pct(g / r) for g, r in zip(gp, rev)] + [pct(sum(gp[:4]) / sum(rev[:4])), pct(sum(gp[4:]) / sum(rev[4:]))]]
        match_rows(expected, 'financial plan')


def expanded_contract(slide, sid, d, c):
    """PASS2 composition and new evidence checks, independent of gallery code."""
    shapes = list(slide.shapes)
    text_boxes = [shape for shape in shapes if shape.has_text_frame and shape.text.strip()]
    tables = [shape for shape in shapes if shape.has_table]
    if sid == 'BD02':
        require(len(tables) == 1 and len(tables[0].table.rows) == 2 and len(tables[0].table.columns) == 3,
                'BD02: six KPIs must be a native 3×2 table')
        b = d['arr_bridge_q3_fy26']; p = d['plan_vs_actual_q3_fy26']
        labels = ['Ending ARR', 'Net new ARR', 'NDR · trailing year', 'Gross margin', 'Net burn', 'Cash']
        values = ['$' + fmt(b['end']) + 'M', '$' + fmt(b['end'] - b['start']) + 'M',
                  pct(d['unit_economics']['ndr']), pct(d['pnl']['gross_margin'][2]),
                  '$' + fmt(p[4]['actual']) + 'M', '$' + fmt(p[5]['actual']) + 'M']
        cells = [cell for row in tables[0].table.rows for cell in row.cells]
        for cell, label, value in zip(cells, labels, values):
            paragraphs = [para for para in cell.text_frame.paragraphs if para.text.strip()]
            require(len(paragraphs) == 3, 'BD02: each KPI needs label, value and comparator')
            require(paragraphs[0].text.casefold() == label.casefold(), f'BD02: KPI label {label}')
            require(paragraphs[1].text == value, f'BD02: KPI value {label}')
            require(all(run.font.color.rgb == load_brand().role('investor_text') for run in paragraphs[1].runs),
                    f'BD02: actual figure must be white: {label}')
        require(tables[0].left / 914400 * 128 < 100 and tables[0].width / 914400 * 128 <= 800,
                'BD02: metric grid must leave a right-side interpretation rail')
        rail = '\n'.join(shape.text for shape in text_boxes if shape.left / 914400 * 128 >= 820 and shape.top / 914400 * 128 < 672)
        require('WHAT CHANGED' in rail.upper(), 'BD02: what-changed rail missing')
        require(fmt(p[0]['plan'] - b['start']) in rail and fmt(b['end'] - b['start']) in rail,
                'BD02: net-new miss absent from change rail')
    if sid in {'BD03', 'BD09'}:
        chart_shape = next(shape for shape in shapes if shape.has_chart)
        minimum = D(15 if sid == 'BD03' else 90)
        require(D(str(chart_shape.chart.value_axis.minimum_scale)) == minimum,
                f'{sid}: movement visibility requires declared truncated axis')
        labels = [shape for shape in text_boxes if shape.name == 'waterfall:axis-start-label']
        require(len(labels) == 1 and str(minimum) in labels[0].text and 'start' in labels[0].text.lower(),
                f'{sid}: explicit axis-start label missing')
        label = labels[0]
        require(chart_shape.left <= label.left <= chart_shape.left + chart_shape.width and
                chart_shape.top <= label.top <= chart_shape.top + chart_shape.height,
                f'{sid}: axis-start label is outside chart area')
        require('Label anchors' in {series.name for series in chart_shape.chart.series}, f'{sid}: native labels-above anchors missing')
    if sid == 'BD07':
        # Fiscal-band labels must occur in chronological order directly above
        # the chart; exact short-month categories are checked by chart_contract.
        chart = next(shape for shape in shapes if shape.has_chart)
        bands = [shape for shape in text_boxes if shape.text.strip() in {'Q3 FY26', 'Q4 FY26', 'Q1 FY27', 'Q2 FY27', 'Q3 FY27'}
                 and shape.top < chart.top and (chart.top - shape.top) / 914400 * 128 <= 80]
        bands.sort(key=lambda shape: shape.left)
        require([shape.text.strip() for shape in bands] == ['Q3 FY26', 'Q4 FY26', 'Q1 FY27', 'Q2 FY27', 'Q3 FY27'],
                'BD07: fiscal band missing / out of order')
        require([shape.name for shape in bands] == [f'fiscal-band:{start}:{count}:{period}' for start, count, period in
                [(0, 1, 'Q3 FY26'), (1, 3, 'Q4 FY26'), (4, 3, 'Q1 FY27'), (7, 3, 'Q2 FY27'), (10, 3, 'Q3 FY27')]],
                'BD07: fiscal bands do not map the short-month sequence')
    if sid == 'IN07':
        chart = next(shape for shape in shapes if shape.has_chart)
        require(chart.chart._chartSpace.xpath('.//c:scatterChart'), 'IN07: native XY scatter missing')
        rects = [shape for shape in shapes if shape._element.xpath('.//a:prstGeom[@prst="rect"]')
                 and shape.width / 914400 * 128 >= 500 and shape.height / 914400 * 128 >= 200]
        require(rects, 'IN07: editable outer quadrant frame missing')
        frame = min(rects, key=lambda shape: shape.width * shape.height)
        # Center rules can be native connectors or one-pixel rectangles.
        horizontal = [shape for shape in shapes if shape is not frame and shape.width >= frame.width * .7 and shape.height / 914400 * 128 <= 3
                      and abs(shape.top - (frame.top + frame.height / 2)) / 914400 * 128 <= 12]
        vertical = [shape for shape in shapes if shape is not frame and shape.height >= frame.height * .7 and shape.width / 914400 * 128 <= 3
                    and abs(shape.left - (frame.left + frame.width / 2)) / 914400 * 128 <= 12]
        require(horizontal and vertical, 'IN07: editable center cross lines missing')
        text = ' '.join(shape.text for shape in text_boxes)
        require(len(re.findall(r'\bHIGH\b', text)) >= 2 and len(re.findall(r'\bLOW\b', text)) >= 2,
                'IN07: HIGH/LOW axis ends missing')
    if sid == 'IN15':
        require(len(tables) == 1, 'IN15: native customer-outcome table required')
        matrix = table_matrix(tables[0]); rows = matrix[1:]
        require(len(rows) == len(d['customer_outcomes']) and len(matrix[0]) == 5, 'IN15: three ruled rows / five columns')
        for row, outcome in zip(rows, d['customer_outcomes']):
            require(outcome['customer'] in row[0], 'IN15: customer identity')
            require(all(outcome[key] in row[1] for key in ('metric', 'before', 'after')), 'IN15: source before/after metric')
            require(row[2] == outcome['period'] and row[3] == outcome['status'] and row[4] == outcome['attribution'],
                    'IN15: period, measured status or attribution changed')
    if sid == 'IN16':
        require(len(tables) == 1, 'IN16: native customer-value table required')
        rows = table_matrix(tables[0])[1:]
        require(len(rows) == len(d['customer_value']['benefits']) + 1 and all(len(row) == 4 for row in rows),
                'IN16: benefit/mechanism/value/status rows')
        for row, benefit in zip(rows, d['customer_value']['benefits']):
            require(row[0] == benefit['benefit'] and row[1] == benefit['mechanism'], 'IN16: benefit mechanism changed')
            require(fmt(benefit['value_k']) in row[2] and row[3] == benefit['status'], 'IN16: value or measured/estimated status changed')
        require(fmt(c['value_total']) in rows[-1][2], 'IN16: benefit total must sum source rows')
        require(rows[-1][0] == 'Total annual value' and rows[-1][1] == '' and rows[-1][3] == 'Mixed',
                'IN16: total scope and mixed measured/estimated status')
        text = '\n'.join(shape.text for shape in text_boxes)
        require(multiple(c['value_ratio']) in text, 'IN16: value/subscription ratio missing')
        cost = fmt(d['customer_value']['parspec_cost_k'])
        require(cost in text, 'IN16: annual subscription denominator missing')
    if sid == 'IN17':
        portraits = [shape for shape in shapes if shape._element.xpath('.//a:prstGeom[@prst="ellipse"]')]
        require(len(portraits) == len(d['team']) == 6, 'IN17: six editable portrait placeholders required')
        require(len({(shape.width, shape.height) for shape in portraits}) == 1 and all(shape.width == shape.height for shape in portraits),
                'IN17: equal circular portrait placeholders required')
        text = '\n'.join(shape.text for shape in text_boxes) + '\n' + '\n'.join(cell.text for table in tables for row in table.table.rows for cell in row.cells)
        for person in d['team']:
            require(person['role'] in text and person['name'] in text and person['credential'] in text, 'IN17: name/role/credential placeholder missing')
    if sid == 'IN18':
        require(len(tables) == 3, 'IN18: three native mechanism bands required')
        all_rows = [row for table in tables for row in table_matrix(table)]
        for group in ('inputs', 'engine', 'outputs'):
            for item in d['product_mechanism'][group]:
                cells = [cell for row in all_rows for cell in row if item in cell]
                require(len(cells) == 1, f'IN18: mechanism item coverage {item}')
                status = d['product_mechanism']['status'].get(item, 'Live')
                require(status in cells[0], f'IN18: {item} status must be {status}')
        connectors = [shape for shape in shapes if shape._element.tag == qn('p:cxnSp')]
        require(len(connectors) >= 2, 'IN18: editable connectors between bands missing')
    if sid in {'BD16', 'IN19'}:
        chart = next(shape.chart for shape in shapes if shape.has_chart)
        by_name = {series.name: series for series in chart.series}
        series = by_name.get('Label anchors', by_name['Movement'])
        labels = {int(label.find(qn('c:idx')).get('val')): ''.join(label.xpath('.//c:rich//a:t/text()'))
                  for label in series._element.findall(qn('c:dLbls'))[0].findall(qn('c:dLbl'))}
        expected = [('+' + fmt(value, 2)) if value > 0 else fmt(value, 2) for value in c['bridge_values']]
        require(labels == dict(enumerate(expected)), f'{sid}: native signed two-decimal cash-bridge labels')


def staging_contract():
    def git(*args): return subprocess.check_output(['git', *args], cwd=REPO, text=True).splitlines()
    changed = set(git('diff', '--cached', '--name-only')) | set(git('diff', '--name-only', '--diff-filter=A', 'HEAD'))
    for path in changed:
        require(Path(path).suffix.lower() not in {'.pptx', '.ppt', '.png', '.pdf', '.jpg', '.jpeg', '.webp', '.key'}, f'public repo artifact staged/added: {path}')
        require(not re.search(r'(^|/)(?:_refs|templates|renders|seriesb_story)(/|$)|real_content', path, re.I), f'public repo private asset path: {path}')
    return len(changed)


def mutation_probes(prs, ids, d, c, allowances, investor):
    """Mutate in-memory slide copies and require each guard to reject them."""
    from pptx.slide import Slide
    sid = 'BD04'; source = prs.slides[ids.index(sid)]
    def altered():
        # python-pptx shape proxies keep the copied XML editable; relationships
        # remain valid for read-only chart inspection on the original slide part.
        return Slide(deepcopy(source._element), source.part)
    probes = []
    def rejected(name, slide, checker):
        try: checker(slide)
        except AssertionError: probes.append(name)
        else: raise AssertionError('mutation survived: ' + name)
    slide = altered()
    box = next(shape for shape in slide.shapes if shape.has_text_frame and shape.top / 914400 * 128 < 672 and shape.text.strip())
    box.text_frame.paragraphs[0].runs[0].text = '999999.9'
    rejected('unsourced number', slide, lambda s: text_contract(s, sid, allowances[sid]))
    slide = altered(); box = next(shape for shape in slide.shapes if shape.has_text_frame and shape.top / 914400 * 128 < 672 and shape.text.strip())
    from pptx.util import Pt
    box.text_frame.paragraphs[0].runs[0].font.size = Pt(5)
    rejected('font floor', slide, lambda s: text_contract(s, sid, allowances[sid]))
    slide = altered(); box = next(shape for shape in slide.shapes if shape.has_text_frame and shape.top / 914400 * 128 < 672 and shape.text.strip())
    box.text_frame.paragraphs[0].runs[0]._r.get_or_add_rPr().set('baseline', '30000')
    rejected('superscript', slide, lambda s: text_contract(s, sid, allowances[sid]))
    slide = altered(); box = next(shape for shape in slide.shapes if shape.has_text_frame and shape.top / 914400 * 128 < 672 and shape.text.strip())
    box.text_frame.paragraphs[0].runs[0].text = 'Q3 performance'
    rejected('bare fiscal quarter', slide, lambda s: text_contract(s, sid, allowances[sid]))
    slide = altered(); chart = next(shape for shape in slide.shapes if shape.has_chart)
    chart._element.getparent().remove(chart._element)
    rejected('missing native chart', slide, lambda s: chart_contract(s, sid, d, c, allowances[sid]))
    # A source-plausible number still fails when it occupies the wrong table
    # cell; this guards against a permissive numeric-token whitelist.
    table_sid = 'BD05'
    table_slide = Slide(deepcopy(prs.slides[ids.index(table_sid)]._element), prs.slides[ids.index(table_sid)].part)
    table = next(shape.table for shape in table_slide.shapes if shape.has_table)
    table.cell(1, 2).text = fmt(d['plan_vs_actual_q3_fy26'][0]['plan'])
    rejected('wrong source-plausible financial cell', table_slide, lambda s: table_contract(s, table_sid, d, c))
    # A copied slide retains chart-part relationships. Restore this in-memory
    # chart cache immediately after the negative probe; no file is written.
    slide = altered()
    chart = next(shape.chart for shape in slide.shapes if shape.has_chart)
    value = chart._chartSpace.xpath('.//c:ser[1]/c:val/c:numRef/c:numCache/c:pt[1]/c:v')[0]
    original = value.text
    try:
        value.text = '999999.9'
        rejected('corrupt native chart cache', slide, lambda s: chart_contract(s, sid, d, c, allowances[sid]))
    finally:
        value.text = original
    wrong_total = deepcopy(d)
    wrong_total['customer_value']['total_k'] += D('.1')
    rejected('customer value source sum', wrong_total, independent)
    wrong_bridge = deepcopy(d)
    wrong_bridge['ebitda_to_cash_q3_fy26']['other'] -= D('.1')
    rejected('cash bridge source reconciliation', wrong_bridge, independent)
    outcome_source = investor.slides[INVESTOR_IDS.index('IN15')]
    wrong_status = Slide(deepcopy(outcome_source._element), outcome_source.part)
    table = next(shape.table for shape in wrong_status.shapes if shape.has_table)
    table.cell(1, 3).text = 'Estimated'
    rejected('customer outcome status', wrong_status, lambda s: expanded_contract(s, 'IN15', d, c))
    value_source = investor.slides[INVESTOR_IDS.index('IN16')]
    wrong_sum = Slide(deepcopy(value_source._element), value_source.part)
    table = next(shape.table for shape in wrong_sum.shapes if shape.has_table)
    table.cell(len(table.rows) - 1, 2).text = fmt(d['customer_value']['benefits'][0]['value_k'])
    rejected('customer value displayed sum', wrong_sum, lambda s: expanded_contract(s, 'IN16', d, c))
    product_source = investor.slides[INVESTOR_IDS.index('IN18')]
    wrong_product = Slide(deepcopy(product_source._element), product_source.part)
    for shape in wrong_product.shapes:
        if not shape.has_table: continue
        for row in shape.table.rows:
            for cell in row.cells:
                if 'Track orders' in cell.text: cell.text = cell.text.replace('Planned', 'Live')
    rejected('planned capability promoted to live', wrong_product, lambda s: expanded_contract(s, 'IN18', d, c))
    bridge_slide = prs.slides[ids.index('BD16')]
    bridge_chart = next(shape.chart for shape in bridge_slide.shapes if shape.has_chart)
    movement = next(series for series in bridge_chart.series if series.name == 'Movement')
    point = movement._element.xpath('./c:dPt[c:idx[@val="0"]]')[0]
    inversion = point.find(qn('c:invertIfNegative'))
    position = point.index(inversion)
    try:
        point.remove(inversion)
        rejected('negative point fill inversion omitted', bridge_slide,
                 lambda s: chart_contract(s, 'BD16', d, c, allowances['BD16']))
    finally:
        point.insert(position, inversion)
    return probes


def verify(path, ids, d, c, allowances, sha):
    prs = Presentation(path)
    require(len(prs.slides) == len(ids), f'{path.name}: slide count')
    charts = tables = 0
    for slide, sid in zip(prs.slides, ids):
        notes = slide.notes_slide.notes_text_frame.text
        require(f'Slide: {sid}' in notes, f'{path.name}: ID/order mismatch {sid}')
        require(sha in notes, f'{sid}: fixture hash provenance missing')
        text_contract(slide, sid, allowances[sid])
        chart_contract(slide, sid, d, c, allowances[sid])
        table_contract(slide, sid, d, c)
        expanded_contract(slide, sid, d, c)
        charts += sum(shape.has_chart for shape in slide.shapes)
        tables += sum(shape.has_table for shape in slide.shapes)
    return prs, dict(path=str(path), slides=len(ids), native_charts=charts, native_tables=tables,
                     sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def render_contract(root, board, investor, d):
    """Check actual rendered evidence only when --render-root is supplied.

    Native OOXML and an editable workbook can both be correct while a renderer
    drops every negative fill. Count role-colored pixels inside the native chart
    frame, excluding the slide header, footer and callout. PDF text additionally
    catches wrapped cash-month labels that structural category checks cannot.
    """
    from PIL import Image
    brand = load_brand()
    checks, errors = [], []
    minimums = {'accent': 1000, 'positive': 100, 'negative': 100}
    colors = {role: tuple(brand.role('investor_' + role)) for role in minimums}
    for name, prs, ids, sid in [('board', board, BOARD_IDS, 'BD16'), ('investor', investor, INVESTOR_IDS, 'IN19')]:
        index = ids.index(sid)
        directory = root / f'{name}_gallery_png'
        stem = f'parspec_{name}_gallery'
        candidates = [path for path in directory.glob(stem + '-*.png')
                      if path.stem.rsplit('-', 1)[-1].isdigit() and int(path.stem.rsplit('-', 1)[-1]) == index + 1]
        if len(candidates) != 1:
            errors.append(f'{sid}: exactly one rendered PNG required for slide {index + 1}')
            checks.append(dict(slide=sid, check='waterfall_fills', result='FAIL', reason=errors[-1]))
            continue
        path = candidates[0]
        shape = next(shape for shape in prs.slides[index].shapes if shape.has_chart)
        with Image.open(path) as image:
            image = image.convert('RGB')
            box = (int(shape.left / prs.slide_width * image.width),
                   int(shape.top / prs.slide_height * image.height),
                   int((shape.left + shape.width) / prs.slide_width * image.width),
                   int((shape.top + shape.height) / prs.slide_height * image.height))
            cropped = image.crop(box)
            histogram = cropped.getcolors(maxcolors=cropped.width * cropped.height)
            counts = {role: sum(count for count, pixel in histogram
                                if max(abs(a - b) for a, b in zip(pixel, rgb)) <= 2)
                      for role, rgb in colors.items()}
        failed = {role: count for role, count in counts.items() if count < minimums[role]}
        if failed:
            errors.append(f'{sid}: rendered waterfall fills missing / too small: {failed}; minimums {minimums}')
        checks.append(dict(slide=sid, check='waterfall_fills', result='FAIL' if failed else 'PASS',
                           png=str(path), png_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                           chart_crop_px=list(box), role_pixels=counts, minimum_role_pixels=minimums,
                           rgb_tolerance=2))
    pdf = root / 'board_gallery_png' / 'parspec_board_gallery.pdf'
    if pdf.exists():
        import fitz
        index = BOARD_IDS.index('BD07')
        chart = next(shape for shape in board.slides[index].shapes if shape.has_chart)
        # Native EMUs convert directly to PDF points. The bottom 15% of the
        # chart contains category ticks, and excludes the range caption below.
        rect = fitz.Rect(chart.left / 12700, (chart.top + chart.height * .85) / 12700,
                         (chart.left + chart.width) / 12700, (chart.top + chart.height) / 12700)
        with fitz.open(pdf) as document:
            require(len(document) == len(BOARD_IDS), 'rendered board PDF slide count')
            page = document[index]
            lines = [line for block in page.get_text('dict', clip=rect)['blocks'] if 'lines' in block for line in block['lines']]
            records = []
            fiscal_wrap = []
            month_pattern = re.compile(r'^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)$')
            for line in lines:
                text = ''.join(span['text'] for span in line['spans']).strip()
                if re.search(r'\bFY\d{2,4}\b|\bQ[1-4]\b', text): fiscal_wrap.append(text)
                if month_pattern.fullmatch(text):
                    records.append(dict(text=text, bbox=list(line['bbox'])))
            records.sort(key=lambda record: record['bbox'][0])
        expected = category_expected('BD07', d)
        matched = [record['text'] for record in records] == expected
        centers = [(record['bbox'][1] + record['bbox'][3]) / 2 for record in records]
        single_line = bool(centers) and max(centers) - min(centers) <= 1.5
        passed = matched and single_line and not fiscal_wrap
        if not passed:
            errors.append(f'BD07: rendered month labels must be thirteen single-line categories; found {[record["text"] for record in records]}, fiscal wrap={fiscal_wrap}')
        checks.append(dict(slide='BD07', check='cash_month_labels', result='PASS' if passed else 'FAIL',
                           pdf=str(pdf), pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
                           clip_points=list(rect), labels=records, fiscal_wrap=fiscal_wrap))
    else:
        checks.append(dict(slide='BD07', check='cash_month_labels', result='NOT_AVAILABLE', reason='Rendered board PDF absent'))
    return dict(result='FAIL' if errors else 'PASS', root=str(root), checks=checks, errors=errors)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--story', type=Path, nargs='+', help='Check only the supplied Series B story decks against the incubation fixture')
    ap.add_argument('--board', type=Path, default=TEMPLATE_DIR / 'parspec_board_gallery.pptx')
    ap.add_argument('--investor', type=Path, default=TEMPLATE_DIR / 'parspec_investor_gallery.pptx')
    ap.add_argument('--evidence', type=Path, help='Optional private JSON verification receipt')
    ap.add_argument('--render-root', type=Path, help='Explicit local Templates directory: verify waterfall PNG fills and cash-label PDF text')
    ap.add_argument('--self-test', action='store_true', help='Mutation probes also run by default')
    args = ap.parse_args()
    if args.story:
        from story_smoke import run
        run(args.data,args.story,args.evidence)
        return
    raw = args.data.read_bytes(); d = json.loads(raw, parse_float=D)
    require('FICTIONAL' in d.get('_note', '') and 'v4' in d.get('_note', ''), 'explicit fictional v4 fixture required')
    require(DEFAULT_PROFILE == 'master', 'master must remain the default')
    sha = hashlib.sha256(raw).hexdigest(); c = independent(d)
    allowances = numeric_allowances(d, c)
    board, b = verify(args.board, BOARD_IDS, d, c, allowances, sha)
    investor, i = verify(args.investor, INVESTOR_IDS, d, c, allowances, sha)
    mutations = mutation_probes(board, BOARD_IDS, d, c, allowances, investor)
    staged = staging_contract()
    rendered = render_contract(args.render_root, board, investor, d) if args.render_root else dict(result='NOT_RUN', reason='--render-root not supplied')
    receipt = dict(result='FAIL' if rendered['result'] == 'FAIL' else 'PASS', fixture_sha256=sha, decks=[b, i], mutation_probes=mutations,
                   render_checks=rendered,
                   staged_or_added_paths_checked=staged,
                   limitations='Structural/data verification; visual review, PowerPoint fidelity and PM/brand acceptance are separate.')
    if args.evidence:
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(json.dumps(receipt, indent=2) + '\n')
    require(rendered['result'] != 'FAIL', '\n'.join(rendered.get('errors', [])))
    print(f'PASS: {b["slides"] + i["slides"]} slides; {b["native_charts"] + i["native_charts"]} native charts with source-exact caches and coherent workbooks; financial tables; per-slide numeric provenance; text/fiscal/source guards; {len(mutations)} rejected mutations; staging guard')
    print('Rendered checks: ' + rendered['result'])


if __name__ == '__main__':
    main()

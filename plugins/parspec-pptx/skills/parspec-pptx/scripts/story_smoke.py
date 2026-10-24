"""Independent story-deck oracle; saved OOXML, embedded workbooks and fixtures."""
from copy import deepcopy
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.slide import Slide
from pptx.util import Pt
from investor_smoke import require, frames, workbook_contract, values_equal, staging_contract, FONT

IDS=['IN-20','IN-21','IN-22','INCUBATION']+[f'IN-{i}' for i in range(23,32)]
CHARTS={'IN-23':1,'IN-24':1,'IN-27':1,'IN-28':2,'IN-31':3}
CHIP='ILLUSTRATIVE · DUMMY NUMBERS'
FOOTER='Illustrative — dummy numbers, not Parspec data'


def matrix(slide):
    return [[[c.text for c in r.cells] for r in t.table.rows] for t in slide.shapes if t.has_table]


def text(slide):
    return '\n'.join(f.text for _,f in frames(slide))


def chart_values(chart):
    return [list(s.values) for s in chart.series]


def floating(steps,totals):
    base=[];movement=[];value=0
    for j,v in enumerate(steps):
        if j in totals:base.append(0);movement.append(v);value=v
        else:base.append(min(value,value+v));movement.append(abs(v));value+=v
    return base,movement


def check_slide(slide,sid,d):
    t=text(slide);inc=sid not in ('IN-20','IN-21','IN-22')
    require(t.count(CHIP)==int(inc),sid+': illustrative boundary')
    require((FOOTER in t)==inc,sid+': incubation footer')
    for shape,frame in frames(slide):
        floor=11 if shape.top/914400*128>=680 else 14
        for p in frame.paragraphs:
            for r in p.runs:
                if not r.text:continue
                require(r.font.size is not None,sid+': inherited font')
                require(r.font.size.pt*128/72+.02>=floor,sid+': type floor')
                require(r.font.name==FONT,sid+': font family')
        require(shape.left>=0 and shape.top>=0 and shape.left+shape.width<=9144000+100 and shape.top+shape.height<=5143500+100,sid+': text off canvas')
    charts=[s.chart for s in slide.shapes if s.has_chart]
    require(len(charts)==CHARTS.get(sid,0),sid+': native chart count')
    if sid not in ('INCUBATION','IN-21','IN-28'):require(matrix(slide),sid+': native table missing')
    for ch in charts:
        workbook_contract(ch,sid)
        for axis in ch._chartSpace.xpath('.//c:valAx/c:scaling/c:min'):
            require(float(axis.get('val'))==0,sid+': zero axis required')
        for sz in ch._chartSpace.xpath('.//a:rPr/@sz | .//a:defRPr/@sz'):
            require(float(sz)/100*128/72+.02>=14,sid+': chart text floor')
    if sid=='IN-20':
        require(len(slide._element.xpath('.//p:cxnSp'))>=2,'IN20: connectors')
    if sid=='IN-21':
        require(len(slide._element.xpath('.//p:cxnSp'))>=2,'IN21: connectors')
    if sid=='IN-23':
        rows=d['IN23']['rows'];total=sum(D(r['parents'])*(D(str(r['platform_fee']))+D(r['units_per_parent'])*D(str(r['net_unit_price']))) for r in rows)/1000000
        require(total.quantize(D('.1'))==D('301.2'),'IN23: operand total')
        values_equal(chart_values(charts[0])[0],[total,d['IN23']['expansion_scenario_m']],'IN23 values')
        require(matrix(slide)[0][-1][-1]=='301.2','IN23: displayed total')
        require(charts[0]._chartSpace.xpath('.//c:barChart/c:grouping[@val="clustered"]'),'IN23: clustered columns')
    if sid=='IN-24':
        steps=d['IN24']['steps'];running=0
        for r in steps:
            if r['type']=='total':
                if running:require(r['value']==running,'IN24 total endpoint')
                running=r['value']
            else:running+=r['value']
        require(steps[0]['value']==4000 and running==300,'IN24: 4000 to 300')
        expected=floating([r['value'] for r in steps],{j for j,r in enumerate(steps) if r['type']=='total'})
        for got,want in zip(chart_values(charts[0])[:2],expected):values_equal(got,want,'IN24 waterfall')
        require(charts[0].series[0]._element.xpath('./c:spPr/a:noFill'),'IN24 hidden base')
    if sid=='IN-25':
        tables=matrix(slide);require(len(tables)==2,'IN25 marketplace separation')
        require('Marketplace' in tables[1][1][0] and 'EXCLUDED FROM EVERY TOTAL' in t,'IN25 marketplace excluded')
    if sid=='IN-26':require(any(f.text.startswith('Proposed pilot package') for _,f in frames(slide)),'IN26 title')
    if sid=='IN-27':
        p=d['IN27']['per_accepted_output'];ch=charts[0]
        require(ch._chartSpace.xpath('.//c:barChart/c:grouping[@val="clustered"]'),'IN27 columns must be adjacent')
        require(len(ch.series)==1,'IN27: single series, three categories')
        values_equal(chart_values(ch)[0],[p['customer_benefit'],p['net_price'],p['full_cost']],'IN27 values')
        require(len(slide._element.xpath('.//p:cxnSp'))>=6,'IN27 editable brackets')
        require('$15.00' in t and '$1.80' in t,'IN27 bracket differences')
    if sid=='IN-28':
        rows=d['IN28']['waterfall_k'];gp=sum(r['value'] for r in rows[:-1]);require(gp==522==rows[-1]['value'],'IN28 GP')
        expected=floating([r['value'] for r in rows],{0,len(rows)-1})
        for got,want in zip(chart_values(charts[0])[:2],expected):values_equal(got,want,'IN28 waterfall')
        p=d['IN28']['payback'];cum=[];v=0
        for n in p['monthly_gp_k']:v+=n;cum.append(v)
        month=next(j+1 for j,n in enumerate(cum) if n>=p['deploy_cost_k'])
        require(month==13==p['payback_month'],'IN28 payback month')
        values_equal(chart_values(charts[1])[0],cum,'IN28 cumulative GP')
        values_equal(chart_values(charts[1])[1],[p['deploy_cost_k']]*len(cum),'IN28 deployment cost')
        require('month 13' in t and charts[1]._chartSpace.xpath('.//a:t[text()="Month 13"]'),'IN28 payback marked')
    if sid=='IN-29':require('UNKNOWN' in t,'IN29 unknown renewals')
    if sid=='IN-30':
        require(len(matrix(slide)[0])==len(d['IN30'])+1,'IN30 evidence coverage')
    if sid=='IN-31':
        ch=charts[0];require(ch._chartSpace.xpath('.//c:barChart/c:grouping[@val="percentStacked"]'),'IN31 100% stacked')
        values=chart_values(ch)
        for j,row in enumerate(d['IN31']):
            require(sum(row[k] for k in ('accepted_no_review_pct','accepted_with_review_pct','failed_pct'))==100,'IN31 fixture sums')
            require(abs(sum(v[j] for v in values)-1)<1e-8,'IN31 chart sums')
        for j,key in enumerate(('accepted_no_review_pct','accepted_with_review_pct','failed_pct')):
            values_equal(values[j],[D(r[key])/100 for r in d['IN31']],'IN31 outcomes')
        for ch,key in zip(charts[1:],('review_min_per_output','full_cost_per_output')):
            values_equal(chart_values(ch)[0],[r[key] for r in d['IN31']],'IN31 line')
        require('TBD' in t,'IN31 unsupported period / defects stay unknown')


def probes(prs,d):
    results=[]
    def reject(sid,name,mutate):
        source=prs.slides[IDS.index(sid)];s=Slide(deepcopy(source._element),source.part)
        restore=mutate(s)
        try:
            try:check_slide(s,sid,d)
            except AssertionError:results.append(name)
            else:raise AssertionError('mutation survived: '+name)
        finally:
            if restore:restore()
    def remove_chip(s):
        shape=next(s for s in s.shapes if s.has_text_frame and s.text==CHIP);shape._element.getparent().remove(shape._element)
    reject('IN-23','missing illustrative chip',remove_chip)
    def wrong_boundary(s):
        chip=next(sh for sh in prs.slides[4].shapes if sh.has_text_frame and sh.text==CHIP)
        s.shapes._spTree.append(deepcopy(chip._element))
    reject('IN-20','dummy chip on real-content slide',wrong_boundary)
    def small(s):
        shape=next(s for s in s.shapes if s.has_text_frame and s.text==CHIP);shape.text_frame.paragraphs[0].runs[0].font.size=Pt(5)
    reject('IN-23','font floor',small)
    def stacked(s):
        ch=next(s.chart for s in s.shapes if s.has_chart);g=ch._chartSpace.xpath('.//c:barChart/c:grouping')[0];old=g.get('val');g.set('val','stacked')
        return lambda:g.set('val',old)
    reject('IN-27','stacked overlapping economics',stacked)
    for sid in ('IN-24','IN-28','IN-31'):
        def corrupt(s):
            ch=next(s.chart for s in s.shapes if s.has_chart);v=ch._chartSpace.xpath('.//c:numCache/c:pt/c:v')[0];old=v.text;v.text='99999'
            return lambda:setattr(v,'text',old)
        reject(sid,sid+' corrupt chart cache',corrupt)
    return results


def run(data,paths,evidence=None):
    raw=Path(data).read_bytes();d=json.loads(raw);sha=hashlib.sha256(raw).hexdigest();decks=[];mutations=[]
    for path in paths:
        prs=Presentation(path);require(len(prs.slides)==13,'story count')
        for sid,s in zip(IDS,prs.slides):
            require('Slide: '+sid in s.notes_slide.notes_text_frame.text,sid+': ID/order')
            if sid.startswith('IN-') and int(sid[3:])>=23:require(sha in s.notes_slide.notes_text_frame.text,sid+': fixture provenance')
            check_slide(s,sid,d)
        mutations+=probes(prs,d)
        decks.append(dict(path=str(path),slides=13,native_charts=sum(sh.has_chart for s in prs.slides for sh in s.shapes),sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest()))
    staged=staging_contract()
    receipt=dict(result='PASS',decks=decks,fixture_sha256=sha,rejected_mutations=mutations,staged_paths_checked=staged,limitations='Structural/data check. Render inspection and external readiness are separate.')
    if evidence:Path(evidence).write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'PASS: {len(decks)*13} story slides; {sum(d["native_charts"] for d in decks)} native charts; {len(mutations)} rejected mutations; fixture arithmetic, workbooks, incubation boundary and staging guard')
    return receipt

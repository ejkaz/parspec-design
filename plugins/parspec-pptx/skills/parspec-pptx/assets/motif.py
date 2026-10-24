"""Proposed sales-register motifs, composed from editable PowerPoint objects.

Coordinates and explicit text sizes use the 1280 x 720 design canvas. The
conversion is 128 px/in and 72 pt/in (CSS screen DPI is deliberately irrelevant).
No client data or local template assets are distributed with these primitives.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

from . import shapes as sh


class Motif:
    """Data-driven sales compositions bound to a :class:`HouseDeck`.

    The caller creates the slide with ``deck.slide('plain', keep=())``. All
    geometry is in source-canvas px; typography and colors resolve through the
    proposed ``sales_register`` in design-model.yaml. Existing profiles are
    unaffected. Inputs are strings, lists and dictionaries, never HTML.
    """

    def __init__(self, deck):
        self.deck = deck
        self.brand = deck.brand
        self.spec = self.brand.sales
        self.geo = self.spec['geometry']
        self.types = self.spec['type']
        self.ppi = self.geo['px_per_in']
        self.font = self.brand.font

    def inch(self, value):
        return value / self.ppi

    def color(self, role):
        role = {'orange': 'accent', 'ink_muted': 'muted', 'ink': 'text',
                'hairline': 'line', 'positive': 'status_good'}.get(role, role)
        return self.brand.colors['sales_' + role]

    def size(self, kind):
        return self.types[kind]['size_px']

    def text(self, slide, x, y, w, h, text, *, size=None, kind='body', color='text',
             bold=None, align='l', anchor='t', line_spacing=None, italic=False, style=None):
        """Editable text; ``size`` is source px, never points."""
        kind = style or kind
        spec = self.types[kind]
        if bold is None:
            bold = spec['weight'] >= 600
        native_font = spec.get('font_face', spec['family']) if not bold else spec['family']
        points = (size if size is not None else spec['size_px']) * 72 / self.ppi
        box = sh.text(slide, *[self.inch(v) for v in (x, y, w, h)], text,
                       size=points,
                       color=self.color(color) if isinstance(color, str) else color,
                       bold=bold, font=native_font, align=align, anchor=anchor,
                       italic=italic)
        # Exact point leading preserves CSS em spacing in PowerPoint, whose
        # proportional leading otherwise also includes intrinsic font leading.
        for para in box.text_frame.paragraphs:
            para.space_before = para.space_after = Pt(0)
            para.line_spacing = Pt(points * (line_spacing or spec['line_height']))
        return box

    txt = text

    def rect(self, slide, x, y, w, h, *, fill='card', line=None, lw=1):
        return sh.shape(slide, MSO_SHAPE.RECTANGLE,
                        *[self.inch(v) for v in (x, y, w, h)],
                        fill=self.color(fill) if fill else None,
                        line=self.color(line) if line else None, lw=lw * 72 / self.ppi)

    def rule(self, slide, x, y, w, *, h=1, color='line'):
        return self.rect(slide, x, y, w, h, fill=color)

    def header(self, slide, eyebrow, title, dek=''):
        """S04–S09: untracked eyebrow, bold mixed-case title, optional dek."""
        x, w = self.geo['inset_px'], self.geo['width_px']
        self.text(slide, x, self.geo['eyebrow_y_px'], w, 25, eyebrow.upper(), kind='eyebrow', color='accent')
        self.text(slide, x, 70, w, 104 if not dek else 57, title,
                  kind='title', line_spacing=1.15)
        if dek:
            self.text(slide, x, 128, w, 47, dek, kind='subtitle',
                      color='muted', line_spacing=1.35)

    def top_rule_card(self, slide, x, y, w, h, heading='', body='', label='', *,
                      padding=None):
        """Default square card: one top rule, no outline/internal rule."""
        p = padding if padding is not None else self.geo['padding_px']
        self.rect(slide, x, y, w, h)
        self.rule(slide, x, y, w, h=self.geo['top_rule_px'], color='top_rule')
        yy = y + p
        if label:
            self.text(slide, x + p, yy, w - 2*p, 24, label.upper(), kind='label', color='accent')
            yy += 32
        if heading:
            self.text(slide, x + p, yy, w - 2*p, 62, heading,
                      kind='card_heading', line_spacing=1.25)
            yy += 70
        if body:
            self.text(slide, x + p, yy, w - 2*p, y + h - p - yy, body,
                      color='subtle', line_spacing=1.45)

    def stat_tile(self, slide, x, y, w, h, label, value, caption='', source='', *, hero=False):
        """S04: compact label/value/caption tile; each metric can carry a marker."""
        p = self.geo['padding_px']
        self.top_rule_card(slide, x, y, w, h)
        self.text(slide, x+p, y+p+4, w-2*p, 35, label.upper(), kind='label', color='accent')
        self.text(slide, x+p, y+61, w-2*p, 83, str(value), kind='stat',
                  color='accent' if hero else 'text', line_spacing=1)
        if source:
            # A separate marker keeps the full-height metric at its intended scale.
            self.text(slide, x+w-p-13, y+58, 16, 19, str(source), kind='footnote', color='muted')
        if caption:
            self.text(slide, x+p, y+165, w-2*p, h-179, caption,
                      kind='caption', bold=False, color='subtle', line_spacing=1.4)

    def bracket_card(self, slide, x, y, w, h, number, heading, body):
        """S05 only: TL/BR ticks and aligned heading/body field."""
        p, tick, thick = 28, 26, self.geo['top_rule_px']
        self.rect(slide, x, y, w, h)
        self.rule(slide, x, y-4, tick, h=thick, color='accent')
        self.rect(slide, x, y-4, thick, tick, fill='accent')
        self.rule(slide, x+w-tick, y+h, tick, h=thick, color='accent')
        self.rect(slide, x+w-thick, y+h-tick+4, thick, tick, fill='accent')
        self.text(slide, x+p, y+28, w-2*p, 39, str(number), kind='small_numeral',
                  color='accent', bold=False, line_spacing=1)
        self.text(slide, x+p, y+84, w-2*p, 61, heading, kind='card_heading',
                  color='accent', line_spacing=1.25)
        self.rule(slide, x+p, y+158, w-2*p)
        self.text(slide, x+p, y+176, w-2*p, h-192, body,
                  kind='body', color='subtle', line_spacing=1.55)

    def callout_bar(self, slide, x, y, w, h, text, label=''):
        """One distinct takeaway; optional label, one orange left bar."""
        self.rect(slide, x, y, w, h, fill='band')
        self.rect(slide, x, y, self.geo['top_rule_px'], h, fill='accent')
        if label:
            self.text(slide, x+28, y+16, w-52, 21, label.upper(), kind='label', color='accent')
        self.text(slide, x+28, y+(42 if label else 15), w-52,
                  h-(51 if label else 27), text, kind='subtitle', bold=True,
                  line_spacing=1.35, anchor='m' if not label else 't')

    def ask_band(self, slide, x, y, w, h, text, label='DECISION NEEDED'):
        """Umber decision context; no gratuitous border."""
        self.rect(slide, x, y, w, h, fill='umber')
        if label:
            self.text(slide, x+24, y+16, w-48, 22, label.upper(), kind='label', color='accent')
        self.text(slide, x+24, y+(42 if label else 16), w-48,
                  h-(52 if label else 30), text, kind='body', bold=True, line_spacing=1.4)

    def highlight_table(self, slide, headers, rows, chosen=3, *, x=56, y=184, w=1168,
                        row_h=68, header_h=60, widths=None, gap=12, chip='RECOMMENDED'):
        """S08. Headers include the row-label column; rows are plain cell lists.

        Chosen is a zero-based column index. Numerics and prices right-align;
        prose remains centred. The outline and one header label are the only
        recommendation treatment. Table cells remain independently editable.
        """
        n = len(headers)
        if not widths:
            widths = [400] + [(w-400-gap*(n-1))/(n-1)]*(n-1)
        scale = (w-gap*(n-1))/sum(widths)
        widths = [v*scale for v in widths]
        xs = [x]
        for cw in widths[:-1]:
            xs.append(xs[-1]+cw+gap)
        for c, head in enumerate(headers):
            if not head:
                continue
            self.rect(slide, xs[c], y, widths[c], header_h, fill='band')
            if c == chosen and chip:
                self.text(slide, xs[c]+10, y+8, widths[c]-20, 20, chip,
                          kind='label', color='accent', align='c')
                hy, hh = y+30, 25
            else:
                hy, hh = y, header_h
            self.text(slide, xs[c]+10, hy, widths[c]-20, hh, str(head).upper(),
                      kind='table_header', color='accent' if c==chosen else 'text',
                      align='c', anchor='m')
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                yy = y+header_h+r*row_h
                self.rect(slide, xs[c], yy, widths[c], row_h,
                          fill='row_alt' if r%2==0 else 'ground_master')
                v = str(val)
                numeric = c>0 and (v.startswith('$') or v.replace(',','').replace('.','').isdigit())
                self.text(slide, xs[c]+20, yy+7, widths[c]-40, row_h-14, v,
                          kind='table_price' if v.startswith('$') else 'table',
                          bold=c==0 or c==chosen or v.startswith('$'),
                          color='accent' if c==chosen and v.startswith('$') else
                                ('text' if c in (0,chosen) else 'subtle'),
                          align='l' if c==0 else ('r' if numeric else 'c'), anchor='m',
                          line_spacing=1.3)
        if chosen is not None:
            self.rect(slide, xs[chosen], y, widths[chosen], header_h+row_h*len(rows),
                      fill=None, line='accent', lw=1)
        return xs, widths

    def rail_steps(self, slide, steps, *, x=56, y=182, w=1168, card_y=236, card_h=280, gap=24):
        """S07. Steps: [{title, subtitle, bullets}]; last node is the target."""
        n, d = len(steps), 36
        cw = (w-gap*(n-1))/n
        self.rule(slide, x, y+d/2-1, w, h=2, color='accent')
        for i, step in enumerate(steps):
            xx, last = x+i*(cw+gap), i==n-1
            cx = xx+cw/2
            sh.shape(slide, MSO_SHAPE.OVAL,
                     *[self.inch(v) for v in (cx-d/2,y,d,d)],
                     fill=self.color('ownership_fill' if last else 'ground_master'),
                     line=self.color('accent'), lw=2*72/self.ppi)
            self.text(slide, cx-d/2, y, d, d, f'{i+1:02d}', kind='label',
                      color='ownership_text' if last else 'accent', align='c', anchor='m')
            self.rect(slide, cx-.5, y+d, 1, card_y-y-d, fill='accent')
            self.rect(slide, xx, card_y, cw, card_h, line='accent' if last else None)
            self.text(slide, xx+24, card_y+22, cw-48, 58, step['title'],
                      kind='subtitle', bold=True, line_spacing=1.25)
            self.text(slide, xx+24, card_y+53, cw-48, 42, step.get('subtitle',''),
                      kind='label', color='accent', line_spacing=1.3)
            by = card_y+100
            for bullet in step.get('bullets',[]):
                # Small literal bullets are text, not status icons.
                self.text(slide, xx+24, by, 12, 25, '•', kind='label', color='subtle')
                self.text(slide, xx+40, by, cw-64, 60, bullet, kind='label',
                          bold=False, color='subtle', line_spacing=1.4)
                by += 60

    def kpi_tile(self, slide, x, y, w, h, label, value, delta, *, hero=False, positive=True):
        """S09. One orange hero value; delta retains a triangle AND a word."""
        self.top_rule_card(slide, x,y,w,h)
        self.text(slide, x+16,y+20,w-32,32,label.upper(),kind='label',color='accent')
        self.text(slide, x+16,y+52,w-32,49,str(value),kind='kpi',
                  color='accent' if hero else 'text', line_spacing=1)
        self.text(slide, x+16,y+h-33,w-32,23,delta,kind='label',
                  color='positive' if positive else 'muted', line_spacing=1.2)

    def donut_callouts(self, slide, items, *, total=None, unit='HOURS', basis='PER $100K SOLD',
                       x=106, y=184, d=340, callout_x=540, callout_w=684, h=356):
        """S06: editable data-driven block-arc segments and matching callout rows.

        Items: ``{label, value, detail='', color='chart_1', text_color='text'}``.
        All slices have equal-scale value labels. A PowerPoint Block Arc has
        native start/end/thickness handles; the geometry is calculated directly
        from each value, with a small angular gutter matching the picked chart.
        """
        total = sum(i['value'] for i in items) if total is None else total
        if not items or any(not math.isfinite(i['value']) or i['value'] <= 0 for i in items):
            raise ValueError('donut slices must be finite positive values')
        if total<=0 or not math.isclose(sum(i['value'] for i in items), total):
            raise ValueError('donut total must equal the positive sum of its slices')
        cx,cy,r = x+d/2,y+d/2,d/2
        outer = d*150/340
        ring = d*56/340
        inner = outer-ring
        angle=-90
        for i,item in enumerate(items):
            sweep=item['value']/total*360
            start,end=angle+.9,angle+sweep-.9
            arc=sh.shape(slide,MSO_SHAPE.BLOCK_ARC,
                         *[self.inch(v) for v in (cx-outer,cy-outer,2*outer,2*outer)],
                         fill=self.color(item.get('color',f'chart_{i+1}')),
                         adj=[(start%360)*.6,(end%360)*.6,ring/(2*outer)])
            arc.name=f"Sales donut {item['label']}: {item['value']} / {total}"
            a=math.radians(angle+sweep/2)
            lr=(outer+inner)/2
            self.text(slide,cx+math.cos(a)*lr-22,cy+math.sin(a)*lr-12,44,24,
                      str(item['value']),kind='body',bold=True,align='c',anchor='m',
                      color=item.get('text_color','ownership_text' if i<3 else 'text'),
                      line_spacing=1)
            angle+=sweep
        self.text(slide,cx-90,cy-56,180,70,str(total),kind='chart_total',bold=True,align='c',line_spacing=1)
        self.text(slide,cx-90,cy+16,180,24,unit,kind='label',align='c')
        self.text(slide,cx-100,cy+42,200,25,basis,kind='label',bold=False,color='muted',align='c')
        rh=h/len(items)
        for i,item in enumerate(items):
            yy=y+i*rh
            clr=item.get('color',f'chart_{i+1}')
            self.rect(slide,callout_x,yy+12,14,14,fill=clr)
            self.text(slide,callout_x+26,yy+9,callout_w-140,25,item['label'].upper(),
                      kind='label')
            self.text(slide,callout_x+callout_w-95,yy+9,95,25,f"{item['value']} hrs",
                      kind='caption',bold=True,color='accent' if i==0 else 'text',align='r')
            if item.get('detail'):
                self.text(slide,callout_x+26,yy+35,callout_w-26,rh-35,item['detail'],
                          kind='chart_detail',bold=False,color='subtle',line_spacing=1.4)
            if i<len(items)-1:
                self.rule(slide,callout_x,yy+rh-1,callout_w)
        return total

    def quarter_arcs(self, slide, *, x=986, y=466, d=468, step=32):
        """Native concentric circles bleed off bottom-right, clipped by slide."""
        # Inner umber disc, then two thin outlines, all at one common centre.
        cx,cy=x+d/2,y+d/2
        inner=d-4*step
        sh.shape(slide,MSO_SHAPE.OVAL,*[self.inch(v) for v in
                 (cx-inner/2,cy-inner/2,inner,inner)],fill=self.color('umber_deep'))
        for dd in (d-2*step,d):
            sh.shape(slide,MSO_SHAPE.OVAL,*[self.inch(v) for v in
                     (cx-dd/2,cy-dd/2,dd,dd)],line=self.color('accent'),lw=2*72/self.ppi)

    def cover_lockup(self, slide, customer, title_lines, *, subtitle='', date='', byline=''):
        """S01: real logo, customer lockup, two-line title, restrained arcs."""
        self.deck.logo(slide,x=self.inch(56),y=self.inch(48),w=self.inch(160))
        self.rect(slide,237,48,1,30,fill='line')
        self.text(slide,258,48,900,34,customer,kind='body',bold=True,color='subtle',anchor='m')
        lines=list(title_lines) if not isinstance(title_lines,str) else title_lines.split('\n')
        if len(lines)!=2:
            raise ValueError('sales cover requires exactly two explicit title lines')
        self.text(slide,56,214,950,143,'\n'.join(lines),kind='cover',line_spacing=1.05)
        self.rule(slide,56,368,self.geo['title_rule_width_px'],h=self.geo['title_rule_px'],color='accent')
        if subtitle:
            self.text(slide,56,395,900,34,subtitle,kind='cover_subtitle',color='accent')
        if date:
            self.text(slide,56,436,900,27,date,kind='body',color='muted')
        if byline:
            self.text(slide,56,478,850,30,byline,kind='body',color='muted')
        self.quarter_arcs(slide)

    def divider(self, slide, title, sections='', *, section='02', glow=None):
        """S03 single register; optional supplied glow image, never generated CSS."""
        if glow:
            slide.shapes.add_picture(str(Path(glow)),Inches(self.inch(720)),0,
                                     width=Inches(self.inch(560)),height=Inches(self.inch(410)))
        self.deck.logo(slide,x=self.inch(56),y=self.inch(48),w=self.inch(160))
        prefix = re.match(r'^([0-9]{2})\s*·\s*(.+)$', title)
        if prefix:
            section, title = prefix.groups()
        # Runs keep chapter orange without creating a competing oversized numeral.
        head=[[(section+'  ',{'color':self.color('accent')}),
               ('·  ',{'color':self.color('muted'),'bold':False}),(title,{})]]
        self.text(slide,56,272,1168,82,head,kind='cover',line_spacing=1.05)
        self.rule(slide,56,363,self.geo['title_rule_width_px'],h=self.geo['title_rule_px'],color='accent')
        if sections:
            self.text(slide,56,398,1168,25,'IN THIS SECTION',kind='label',color='accent')
            self.text(slide,56,430,1168,50,sections,kind='caption',bold=False,color='muted',line_spacing=1.4)

    def contact_ring(self, slide, x, y, d, name, title, email='', *, image=None, initials=''):
        """S10 full ring. With no photo, initials are visibly template content."""
        ring=sh.shape(slide,MSO_SHAPE.OVAL,*[self.inch(v) for v in (x,y,d,d)],
                      fill=self.color('band'),line=self.color('accent'),lw=4*72/self.ppi)
        if image:
            # Native circular picture fill avoids a square headshot obscuring ring.
            pic=slide.shapes.add_picture(str(image),Inches(self.inch(x+4)),Inches(self.inch(y+4)),
                                         width=Inches(self.inch(d-8)),height=Inches(self.inch(d-8)))
            geom=pic._element.spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}prstGeom')
            if geom is not None:
                geom.set('prst','ellipse')
        else:
            self.text(slide,x,y,d,d,initials or '…',kind='small_numeral',bold=True,color='muted',align='c',anchor='m')
        tx=x+d+24
        self.text(slide,tx,y+7,400,31,name,kind='contact_name',line_spacing=1.2)
        self.text(slide,tx,y+43,400,29,title,kind='contact_detail',bold=False,color='muted',line_spacing=1.3)
        if email:
            self.text(slide,tx,y+70,400,29,email,kind='contact_detail',bold=False,color='accent',line_spacing=1.3)
        return ring

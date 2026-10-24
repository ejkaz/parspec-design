"""Native, editable charts and financial tables for the investor register.

Coordinates and sizes use the 1280 x 720 design canvas (128 px/in). Every
chart contains a native PowerPoint plot and an embedded editable workbook.
No chart title is inserted. Labels are on, gridlines are off, and the font
and palette resolve exclusively through the supplied deck's Brand object.

Series arguments are lists of ``{name, values, color?, forecast?}`` dictionaries.
Scatter points are ``{name, x, y}``. Tables accept plain cell values; callers
may supply already formatted strings for percentages, periods and variance.
"""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
import math

from pptx.chart.data import CategoryChartData, XyChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_MARKER_STYLE, XL_TICK_MARK
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

from . import shapes as sh


def _el(tag, **attrs):
    e = OxmlElement(tag)
    for name, value in attrs.items():
        e.set(name, str(value))
    return e


def financial(value, decimals=1):
    """Half-up boundary formatting with parentheses for negative values."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    d = Decimal(str(value)).quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    result = f"{abs(d):,.{decimals}f}"
    return f"({result})" if d < 0 else result


class Charts:
    """Investor chart palette bound to an existing HouseDeck.

    ``font_px`` uses source pixels. The default 16 px yields 9 pt on the
    ten-inch canvas. Tables use 18 px by default; 13 px is an explicit appendix
    exception that must be selected by the caller.
    """

    def __init__(self, deck):
        self.deck = deck
        self.brand = deck.brand
        self.font = self.brand.font
        self.ppi = self.brand.investor['geometry']['px_per_in']

    def color(self, role):
        if not isinstance(role, str):
            return role
        return self.brand.role("investor_" + role)

    def pt(self, px):
        return Pt(math.ceil(px * 72 / self.ppi * 100) / 100)

    def rect(self, slide, x, y, w, h, *, fill=None, line=None, lw=1):
        return sh.shape(slide, MSO_SHAPE.RECTANGLE, *[v / self.ppi for v in (x, y, w, h)],
                        fill=self.color(fill) if fill else None,
                        line=self.color(line) if line else None, lw=lw * 72 / self.ppi)

    def text(self, slide, x, y, w, h, text, *, font_px=16, color="text", bold=False, align="l"):
        return sh.text(slide, *[v / self.ppi for v in (x, y, w, h)], str(text),
                       size=self.pt(font_px).pt, font=self.font, color=self.color(color),
                       bold=bold, align=align, anchor="m")

    def act_forecast_chips(self, slide, actual, forecast, *, x, y, w=500, h=28):
        """Editable, paired status bands; accepts full dated status strings."""
        gap = 12
        cw = (w - gap) / 2
        for i, (label, forecast_flag) in enumerate(((actual, False), (forecast, True))):
            xx = x + i * (cw + gap)
            self.rect(slide, xx, y, cw, h, fill="accent" if forecast_flag else "band")
            self.text(slide, xx + 9, y, cw - 18, h, label, font_px=14,
                      color="ground" if forecast_flag else "text", bold=True)

    actual_forecast_chips = act_forecast_chips

    def _font(self, font, px=16, color="text", bold=False):
        font.name = self.font
        font.size = self.pt(px)
        font.bold = bold
        font.color.rgb = self.color(color)

    def _txpr(self, px=16, color="text"):
        tx = _el("c:txPr")
        tx.append(_el("a:bodyPr"))
        tx.append(_el("a:lstStyle"))
        p = _el("a:p")
        pp = _el("a:pPr")
        rp = _el("a:defRPr", sz=int(round(self.pt(px).pt * 100)))
        fill = _el("a:solidFill")
        fill.append(_el("a:srgbClr", val=str(self.color(color))))
        rp.append(fill)
        rp.append(_el("a:latin", typeface=self.font))
        pp.append(rp)
        p.append(pp)
        p.append(_el("a:endParaRPr", lang="en-US"))
        tx.append(p)
        return tx

    def _new(self, slide, kind, data, x, y, w, h, name, *, font_px=16, legend=False):
        shape = slide.shapes.add_chart(kind, *[Inches(v / self.ppi) for v in (x, y, w, h)], data)
        shape.name = "native:" + name
        chart = shape.chart
        chart.has_title = False
        chart.has_legend = legend
        chart.chart_style = None
        existing_tx = chart._chartSpace.find(qn("c:txPr"))
        if existing_tx is not None:
            chart._chartSpace.replace(existing_tx, self._txpr(font_px))
        else:
            chart._chartSpace.insert(list(chart._chartSpace).index(chart._chartSpace.chart) + 1,
                                     self._txpr(font_px))
        sp = chart._chartSpace.find(qn("c:spPr"))
        if sp is None:
            sp = _el("c:spPr")
            chart._chartSpace.insert(list(chart._chartSpace).index(chart._chartSpace.find(qn("c:txPr"))), sp)
        sp.append(_el("a:noFill"))
        ln = _el("a:ln")
        ln.append(_el("a:noFill"))
        sp.append(ln)
        if legend:
            chart.legend.position = XL_LEGEND_POSITION.BOTTOM
            chart.legend.include_in_layout = False
            self._font(chart.legend.font, font_px, "muted")
        self._axes(chart, font_px=font_px)
        return shape

    def _axes(self, chart, *, font_px=16, minimum=None, maximum=None, number_format="0.0", x_format=None):
        for axis_name in ("category_axis", "value_axis"):
            try:
                axis = getattr(chart, axis_name)
            except (ValueError, AttributeError):
                continue
            axis.has_major_gridlines = False
            axis.has_minor_gridlines = False
            axis.has_title = False
            axis.major_tick_mark = XL_TICK_MARK.NONE
            axis.minor_tick_mark = XL_TICK_MARK.NONE
            axis.format.line.fill.background()
            self._font(axis.tick_labels.font, font_px, "muted")
            if axis_name == "value_axis":
                axis.tick_labels.number_format = number_format
                axis.tick_labels.number_format_is_linked = False
                if minimum is not None:
                    axis.minimum_scale = minimum
                if maximum is not None:
                    axis.maximum_scale = maximum
            elif x_format:
                axis.tick_labels.number_format = x_format
                axis.tick_labels.number_format_is_linked = False

    def _labels(self, plot, *, fmt="0.0;(0.0);0.0", font_px=16, color="text", position=XL_LABEL_POSITION.OUTSIDE_END):
        plot.has_data_labels = True
        labels = plot.data_labels
        labels.show_value = True
        labels.show_legend_key = False
        labels.show_category_name = False
        labels.show_series_name = False
        labels.number_format = fmt
        labels.number_format_is_linked = False
        try:
            labels.position = position
        except ValueError:
            pass
        self._font(labels.font, font_px, color)

    def _paint(self, series, role, *, fill=None, outline=None):
        series.format.fill.solid()
        series.format.fill.fore_color.rgb = self.color(fill or role)
        series.format.line.color.rgb = self.color(outline or role)
        series.format.line.width = self.pt(1.5)

    def _custom_label(self, series, index, text, *, color="text", font_px=16, position="outEnd", format_code="0.0;(0.0);0.0"):
        """A real chart data label with explicit text, no overlaid text box."""
        ser = series._element
        labels = ser.find(qn("c:dLbls"))
        if labels is None:
            labels = _el("c:dLbls")
            # dLbls precedes trendline / errBars / category and value refs.
            before = next((e for e in ser if e.tag in (qn("c:cat"), qn("c:val"), qn("c:xVal"), qn("c:yVal"))), None)
            if before is None:
                ser.append(labels)
            else:
                ser.insert(ser.index(before), labels)
        lab = _el("c:dLbl")
        lab.append(_el("c:idx", val=index))
        if text is not None:
            tx = _el("c:tx")
            rich = _el("c:rich")
            rich.append(_el("a:bodyPr"))
            rich.append(_el("a:lstStyle"))
            p = _el("a:p")
            r = _el("a:r")
            rp = _el("a:rPr", lang="en-US", sz=int(round(self.pt(font_px).pt * 100)))
            fill = _el("a:solidFill")
            fill.append(_el("a:srgbClr", val=str(self.color(color))))
            rp.append(fill)
            rp.append(_el("a:latin", typeface=self.font))
            r.append(rp)
            t = _el("a:t")
            t.text = str(text)
            r.append(t)
            p.append(r)
            rich.append(p)
            tx.append(rich)
            lab.append(tx)
        lab.append(_el("c:numFmt", formatCode=format_code, sourceLinked=0))
        lab.append(self._txpr(font_px, color))
        lab.append(_el("c:dLblPos", val=position))
        for option in ("showLegendKey", "showVal", "showCatName", "showSerName", "showPercent", "showBubbleSize"):
            lab.append(_el("c:" + option, val=1 if option == "showVal" and text is None else 0))
        labels.append(lab)

    def column_actual_forecast(self, slide, categories, values, actual_count, *, x, y, w, h,
                               number_format="0.0", font_px=16, maximum=None, legend=True):
        """One aligned column per category, actual solid / forecast outlined.

        Distinct Actual/Forecast series share the category axis and overlap 100%,
        so their columns retain exactly the same centers across the boundary.
        """
        if len(categories) != len(values) or not 0 <= actual_count <= len(values):
            raise ValueError("category/value length or actual_count mismatch")
        data = CategoryChartData(number_format=number_format)
        data.categories = categories
        data.add_series("Actual", [v if i < actual_count else None for i, v in enumerate(values)])
        data.add_series("Forecast", [v if i >= actual_count else None for i, v in enumerate(values)])
        shape = self._new(slide, XL_CHART_TYPE.COLUMN_CLUSTERED, data, x, y, w, h,
                          "column_actual_forecast", font_px=font_px, legend=legend)
        chart = shape.chart
        plot = chart.plots[0]
        plot.overlap = 100
        plot.gap_width = 55
        self._paint(chart.series[0], "accent")
        self._paint(chart.series[1], "accent", fill="forecast_fill", outline="accent")
        self._labels(plot, fmt=number_format, font_px=font_px)
        for i, value in enumerate(values):
            self._custom_label(chart.series[0 if i < actual_count else 1], i,
                               None, color="text" if i < actual_count else "accent", font_px=font_px, format_code=number_format)
        self._axes(chart, font_px=font_px, minimum=0, maximum=maximum, number_format=number_format)
        return shape

    def waterfall(self, slide, labels, values, *, x, y, w, h, total_indices=(0, -1),
                  font_px=16, maximum=None, number_format="0.0", plan_index=None):
        """Floating stacked columns: values at total_indices are absolute totals.

        Intermediate entries are signed changes. An optional plan_index is an
        absolute total drawn with a neutral outline. Invisible base-series labels
        are explicitly disabled; visible labels show changes, not hidden bases.
        """
        n = len(values)
        totals = {i % n for i in total_indices}
        bases, steps, roles = [], [], []
        running = 0
        for i, value in enumerate(values):
            if i in totals or i == plan_index:
                base, height = 0, value
                running = value
                role = "muted" if i == plan_index else "accent"
            else:
                base, height = min(running, running + value), abs(value)
                running += value
                role = "positive" if value >= 0 else "negative"
            bases.append(base)
            steps.append(height)
            roles.append(role)
        data = CategoryChartData(number_format=number_format)
        data.categories = labels
        data.add_series("Hidden base", bases)
        data.add_series("Movement", steps)
        shape = self._new(slide, XL_CHART_TYPE.COLUMN_STACKED, data, x, y, w, h,
                          "waterfall", font_px=font_px)
        chart, plot = shape.chart, shape.chart.plots[0]
        plot.gap_width = 75
        base, movement = chart.series
        base.format.fill.background()
        base.format.line.fill.background()
        base_labels = _el("c:dLbls")
        for option in ("showLegendKey", "showVal", "showCatName", "showSerName", "showPercent", "showBubbleSize"):
            base_labels.append(_el("c:" + option, val=0))
        base._element.insert(list(base._element).index(base._element.find(qn("c:cat"))), base_labels)
        self._labels(plot, fmt=number_format, font_px=font_px)
        for i, (value, role) in enumerate(zip(values, roles)):
            point = movement.points[i]
            point.format.fill.solid()
            point.format.fill.fore_color.rgb = self.color("ground" if i == plan_index else role)
            point.format.line.color.rgb = self.color(role)
            point.format.line.width = self.pt(1.5)
            self._custom_label(movement, i, financial(value, 0 if number_format == "0" else 1), font_px=font_px)
        self._axes(chart, font_px=font_px, minimum=0, maximum=maximum, number_format=number_format)
        return shape

    def line_trend(self, slide, categories, series, *, x, y, w, h, font_px=16,
                   number_format="0.0", minimum=0, maximum=None, legend=False):
        """Native line chart; forecast=True selects a dashed line."""
        data = CategoryChartData(number_format=number_format)
        data.categories = categories
        for item in series:
            data.add_series(item["name"], item["values"])
        shape = self._new(slide, XL_CHART_TYPE.LINE_MARKERS, data, x, y, w, h,
                          "line_trend", font_px=font_px, legend=legend)
        chart = shape.chart
        for i, item in enumerate(series):
            ser = chart.series[i]
            role = item.get("color", "accent" if i == 0 else "muted")
            ser.format.line.color.rgb = self.color(role)
            ser.format.line.width = self.pt(3)
            if item.get("forecast"):
                ser.format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
            ser.marker.style = XL_MARKER_STYLE.CIRCLE
            ser.marker.size = 4
            ser.marker.format.fill.solid()
            ser.marker.format.fill.fore_color.rgb = self.color(role)
            ser.marker.format.line.fill.background()
        self._labels(chart.plots[0], fmt=number_format, font_px=font_px, position=XL_LABEL_POSITION.ABOVE)
        self._axes(chart, font_px=font_px, minimum=minimum, maximum=maximum, number_format=number_format)
        return shape

    def combo_bar_line(self, slide, categories, bars, lines, *, x, y, w, h, font_px=16,
                       number_format="0.0", minimum=0, maximum=None, legend=True):
        """A genuine shared-axis column + line combo with one editable workbook.

        All series first enter one workbook. Only the plot XML changes: the
        requested line series move into a native lineChart sharing both axes.
        This avoids stale references to a second temporary chart/workbook.
        """
        if not bars or not lines:
            raise ValueError("combo requires at least one bar and one line series")
        data = CategoryChartData(number_format=number_format)
        data.categories = categories
        for item in [*bars, *lines]:
            data.add_series(item["name"], item["values"])
        shape = self._new(slide, XL_CHART_TYPE.COLUMN_CLUSTERED, data, x, y, w, h,
                          "combo_bar_line", font_px=font_px, legend=legend)
        chart = shape.chart
        bar_plot = chart._chartSpace.chart.plotArea.find(qn("c:barChart"))
        line_plot = _el("c:lineChart")
        line_plot.append(_el("c:grouping", val="standard"))
        ser_elements = bar_plot.findall(qn("c:ser"))
        for ser in ser_elements[len(bars):]:
            bar_plot.remove(ser)
            line_plot.append(ser)
        for ax in bar_plot.findall(qn("c:axId")):
            line_plot.append(deepcopy(ax))
        area = chart._chartSpace.chart.plotArea
        area.insert(area.index(bar_plot) + 1, line_plot)
        for i, item in enumerate([*bars, *lines]):
            ser = chart.series[i]
            role = item.get("color", "accent" if i == 0 else "muted")
            self._paint(ser, role, fill="forecast_fill" if item.get("forecast") else role)
            if i >= len(bars):
                ser.format.line.width = self.pt(3)
                if item.get("forecast"):
                    ser.format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        for i, plot in enumerate(chart.plots):
            self._labels(plot, fmt=number_format, font_px=font_px,
                         position=XL_LABEL_POSITION.ABOVE if i == 1 else XL_LABEL_POSITION.OUTSIDE_END)
        self._axes(chart, font_px=font_px, minimum=minimum, maximum=maximum, number_format=number_format)
        return shape

    def stacked_bar(self, slide, categories, series, *, x, y, w, h, horizontal=True,
                    font_px=16, number_format="0.0", maximum=None, legend=True):
        """Native stacked bars/columns from named component series."""
        data = CategoryChartData(number_format=number_format)
        data.categories = categories
        for item in series:
            data.add_series(item["name"], item["values"])
        shape = self._new(slide, XL_CHART_TYPE.BAR_STACKED if horizontal else XL_CHART_TYPE.COLUMN_STACKED,
                          data, x, y, w, h, "stacked_bar", font_px=font_px, legend=legend)
        chart = shape.chart
        for i, item in enumerate(series):
            self._paint(chart.series[i], item.get("color", f"chart_{i % 4 + 1}"))
        chart.plots[0].gap_width = 65
        self._labels(chart.plots[0], fmt=number_format, font_px=font_px, position=XL_LABEL_POSITION.CENTER)
        self._axes(chart, font_px=font_px, minimum=0, maximum=maximum, number_format=number_format)
        return shape

    def scatter_labeled(self, slide, points, *, x, y, w, h, highlight="Parspec", x_min=0,
                        x_max=1, y_min=0, y_max=1, x_format="0%", y_format="0.0",
                        median_x=None, median_y=None, font_px=16, qualitative=False):
        """Native XY plot with direct name labels and optional median references.

        Points may additionally supply ``label_position`` (r/l/t/b). Reference
        series retain numeric coordinates and are editable alongside the points.
        """
        data = XyChartData()
        for point in points:
            data.add_series(point["name"]).add_data_point(point["x"], point["y"])
        if median_x is not None:
            s = data.add_series("Growth median")
            s.add_data_point(median_x, y_min)
            s.add_data_point(median_x, y_max)
        if median_y is not None:
            s = data.add_series("Valuation median")
            s.add_data_point(x_min, median_y)
            s.add_data_point(x_max, median_y)
        shape = self._new(slide, XL_CHART_TYPE.XY_SCATTER, data, x, y, w, h,
                          "scatter_labeled", font_px=font_px)
        chart = shape.chart
        # python-pptx exposes no plot-level data-label API for scatter plots.
        # Each point receives a native c:dLbl on its own native series below.
        for i, point in enumerate(points):
            ser = chart.series[i]
            role = "accent" if point["name"] == highlight else "muted"
            ser.format.line.fill.background()
            ser.marker.style = XL_MARKER_STYLE.CIRCLE
            ser.marker.size = 9 if point["name"] == highlight else 6
            ser.marker.format.fill.solid()
            ser.marker.format.fill.fore_color.rgb = self.color(role)
            ser.marker.format.line.fill.background()
            pos = {"r": "r", "l": "l", "t": "t", "b": "b"}.get(point.get("label_position"), "r")
            self._custom_label(ser, 0, point["name"], color=role, font_px=font_px, position=pos)
        for i in range(len(points), len(chart.series)):
            ser = chart.series[i]
            ser.marker.style = XL_MARKER_STYLE.NONE
            ser.format.line.color.rgb = self.color("line")
            ser.format.line.width = self.pt(1)
            ser.format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
            labels = _el("c:dLbls")
            labels.append(_el("c:delete", val=1))
            for option in ("showLegendKey", "showVal", "showCatName", "showSerName", "showPercent", "showBubbleSize"):
                labels.append(_el("c:" + option, val=0))
            ser._element.insert(list(ser._element).index(ser._element.find(qn("c:xVal"))), labels)
        if median_x is not None or median_y is not None:
            # Keep line-only references in their own native plot. LibreOffice's
            # scatter importer coalesces a mixed lineMarker group and can apply
            # the final reference's `marker=none` to every singleton point.
            # Separate marker/line groups also prevent reference-label defaults
            # leaking onto otherwise directly labelled company points.
            area = chart._chartSpace.chart.plotArea
            point_plot = area.find(qn("c:scatterChart"))
            point_plot.find(qn("c:scatterStyle")).set("val", "marker")
            reference_plot = _el("c:scatterChart")
            reference_plot.append(_el("c:scatterStyle", val="line"))
            reference_plot.append(_el("c:varyColors", val=0))
            for ser in point_plot.findall(qn("c:ser"))[len(points):]:
                point_plot.remove(ser)
                reference_plot.append(ser)
            reference_labels = _el("c:dLbls")
            reference_labels.append(_el("c:delete", val=1))
            for option in ("showLegendKey", "showVal", "showCatName", "showSerName", "showPercent", "showBubbleSize"):
                reference_labels.append(_el("c:" + option, val=0))
            reference_plot.append(reference_labels)
            for axis in point_plot.findall(qn("c:axId")):
                reference_plot.append(deepcopy(axis))
            area.insert(area.index(point_plot), reference_plot)
        self._axes(chart, font_px=font_px, minimum=y_min, maximum=y_max,
                   number_format=y_format, x_format=x_format)
        chart.category_axis.minimum_scale = x_min
        chart.category_axis.maximum_scale = x_max
        if qualitative:
            chart.category_axis.visible = False
            chart.value_axis.visible = False
        return shape

    def doughnut(self, slide, labels, values, *, x, y, w, h, font_px=16, hole_size=65,
                  legend=False, number_format="0%", colors=None):
        """Native doughnut with percentage labels and optional editable legend."""
        if not values or any(v <= 0 for v in values):
            raise ValueError("doughnut values must be positive")
        data = CategoryChartData(number_format=number_format)
        data.categories = labels
        data.add_series("Allocation", values)
        shape = self._new(slide, XL_CHART_TYPE.DOUGHNUT, data, x, y, w, h,
                          "doughnut", font_px=font_px, legend=legend)
        plot = shape.chart.plots[0]
        plot.hole_size = hole_size
        plot.first_slice_angle = 270
        for i, point in enumerate(shape.chart.series[0].points):
            point.format.fill.solid()
            point.format.fill.fore_color.rgb = self.color(colors[i] if colors else f"chart_{i % 4 + 1}")
            point.format.line.color.rgb = self.color("ground")
            point.format.line.width = self.pt(2)
        self._labels(plot, fmt=number_format, font_px=font_px, position=XL_LABEL_POSITION.CENTER)
        plot.data_labels.show_value = False
        plot.data_labels.show_percentage = True
        return shape

    def bar_ranked(self, slide, labels, values, *, x, y, w, h, highlight=None,
                   font_px=16, number_format="0.0", maximum=None, sort=False):
        """Native horizontal comparison bars; input ordering preserved by default."""
        pairs = list(zip(labels, values))
        if sort:
            pairs.sort(key=lambda item: item[1], reverse=True)
        labels, values = zip(*pairs)
        data = CategoryChartData(number_format=number_format)
        data.categories = labels
        data.add_series("Value", values)
        shape = self._new(slide, XL_CHART_TYPE.BAR_CLUSTERED, data, x, y, w, h,
                          "bar_ranked", font_px=font_px)
        chart = shape.chart
        self._paint(chart.series[0], "muted")
        for i, label in enumerate(labels):
            if label == highlight or i == highlight:
                point = chart.series[0].points[i]
                point.format.fill.solid()
                point.format.fill.fore_color.rgb = self.color("accent")
                point.format.line.color.rgb = self.color("accent")
        chart.category_axis.reverse_order = True
        chart.plots[0].gap_width = 70
        self._labels(chart.plots[0], fmt=number_format, font_px=font_px)
        self._axes(chart, font_px=font_px, minimum=0, maximum=maximum, number_format=number_format)
        return shape

    def _tabular(self, paragraph):
        """Equal native digit advances via supported DrawingML character spacing.

        PowerPoint has no portable tnum feature toggle. Montserrat has lining
        digits but its default glyph widths vary. Split only existing runs and
        compensate those measured advances; a cell's editable text is identical.
        """
        metrics = self.brand.investor['financial_digit_metrics']
        for run in list(paragraph.runs):
            text = run.text
            if not any(char.isascii() and char.isdigit() for char in text):
                continue
            bold = bool(run.font.bold)
            widths = metrics['bold' if bold else 'regular']
            point_size = run.font.size.pt
            original = run._r
            index = paragraph._p.index(original)
            for char in text:
                elem = _el('a:r')
                props = deepcopy(original.get_or_add_rPr())
                spacing = (max(widths)-widths[int(char)]) / metrics['units_per_em'] * point_size * 100 if char in '0123456789' else 0
                props.set('spc', str(int(round(spacing))))
                elem.append(props)
                value = _el('a:t'); value.text = char
                if char.isspace():
                    value.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                elem.append(value)
                paragraph._p.insert(index, elem); index += 1
            paragraph._p.remove(original)

    def fin_table(self, slide, headers, rows, *, x, y, w, h, units="", widths=None,
                  statuses=None, highlight_col=None, highlight_row=None, font_px=18,
                  decimals=1, total_rows=(), row_colors=None, numeric_cols=None):
        """Native financial table with a units/header band and padded outline.

        ``statuses`` aligns to headers and contains Actual / Forecast / mixed /
        empty strings. Forecast cell text is orange, actual values are white.
        Strings preserve caller formatting; numeric values use half-up decimals
        and parentheses. ``widths`` are relative column weights. Native per-digit
        character spacing equalizes Montserrat's proportional digit advances
        using measured metrics in the brand model. Text remains editable and
        keeps its original content; no font substitution or images are used.
        """
        cols = len(headers)
        if any(len(row) != cols for row in rows):
            raise ValueError("table rows must match header length")
        band_h = 26 if units or statuses else 0
        if band_h:
            self.rect(slide, x, y, w, band_h, fill="ground")
            if units:
                self.text(slide, x, y, w, band_h, units, font_px=font_px, color="muted")
        shape = slide.shapes.add_table(len(rows) + 1, cols, *[Inches(v / self.ppi) for v in (x, y + band_h, w, h - band_h)])
        shape.name = "native:fin_table"
        table = shape.table
        table.first_row = False
        table.horz_banding = False
        weights = widths or [2.4] + [1] * (cols - 1)
        if len(weights) != cols:
            raise ValueError("column widths must match headers")
        for i, weight in enumerate(weights):
            table.columns[i].width = Inches(w * weight / sum(weights) / self.ppi)
        xs = [x]
        for col in table.columns:
            xs.append(xs[-1] + col.width / 914400 * self.ppi)
        row_h = (h - band_h) / (len(rows) + 1)
        for r, row in enumerate([headers, *rows]):
            for c, value in enumerate(row):
                cell = table.cell(r, c)
                cell.margin_left = cell.margin_right = Inches(12 / self.ppi)
                cell.margin_top = cell.margin_bottom = Inches(5 / self.ppi)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                cell.fill.solid()
                cell.fill.fore_color.rgb = self.color("band" if r == 0 else "row_alt" if r % 2 else "ground")
                tcpr = cell._tc.get_or_add_tcPr()
                for side in ("lnL", "lnR", "lnT", "lnB"):
                    edge = _el("a:" + side, w=0)
                    edge.append(_el("a:noFill"))
                    tcpr.append(edge)
                cell.text = financial(value, decimals)
                tf = cell.text_frame
                tf.word_wrap = True
                numeric = (c > 0) if numeric_cols is None else c in numeric_cols
                for para in tf.paragraphs:
                    para.alignment = PP_ALIGN.RIGHT if numeric else PP_ALIGN.LEFT
                    para.space_before = para.space_after = Pt(0)
                    # Exact leading keeps table geometry independent of inherited theme.
                    para.line_spacing = self.pt((min(font_px, 14) if r == 0 else font_px) * 1.18)
                    for run in para.runs:
                        role = "text"
                        if r == 0:
                            role = "accent" if c == highlight_col or (statuses and statuses[c].lower().startswith("forecast")) else "muted"
                        elif statuses and statuses[c].lower().startswith("forecast"):
                            role = "accent"
                        if row_colors and r > 0 and r - 1 in row_colors:
                            role = row_colors[r - 1]
                        self._font(run.font, min(font_px, 14) if r == 0 else font_px, role, bold=r == 0 or r - 1 in total_rows)
                        run._r.get_or_add_rPr().set("spc", "0")
                    if r > 0 and numeric:
                        self._tabular(para)
                        # PowerPoint/LibreOffice omit trailing character spacing
                        # at paragraph end. Reserve the missing final-digit
                        # advance in native cell padding, so decimals align.
                        if cell.text and cell.text[-1] in '0123456789':
                            last = para.runs[-1]
                            metrics = self.brand.investor['financial_digit_metrics']
                            advances = metrics['bold' if last.font.bold else 'regular']
                            missing = (max(advances)-advances[int(cell.text[-1])]) / metrics['units_per_em'] * last.font.size.pt
                            cell.margin_right = Inches(12/self.ppi + missing/72)
                if r - 1 in total_rows:
                    previous = tcpr.find(qn("a:lnT"))
                    if previous is not None:
                        tcpr.remove(previous)
                    edge = _el("a:lnT", w=6350)
                    fill = _el("a:solidFill")
                    fill.append(_el("a:srgbClr", val=str(self.color("line"))))
                    edge.append(fill)
                    tcpr.append(edge)
        if statuses:
            # Labels sit in the status band over the matching native columns.
            start = None
            for c, status in enumerate([*statuses, None]):
                if c and status != statuses[c - 1] and start is not None:
                    previous = statuses[c - 1]
                    if previous:
                        self.text(slide, xs[start] + 8, y, xs[c] - xs[start] - 16, band_h,
                                  previous.upper(), font_px=max(14, font_px - 2),
                                  color="accent" if previous.lower().startswith("forecast") else "muted", bold=True, align="r")
                    start = None
                if c < cols and start is None:
                    start = c
        if highlight_col is not None:
            self.rect(slide, xs[highlight_col] + 2, y + band_h + 2,
                      xs[highlight_col + 1] - xs[highlight_col] - 4, h - band_h - 4,
                      line="accent")
        if highlight_row is not None:
            self.rect(slide, x + 2, y + band_h + (highlight_row + 1) * row_h + 2,
                      w - 4, row_h - 4, line="accent")
        return shape

    def heatmap_table(self, slide, row_labels, col_labels, values, *, x, y, w, h,
                      font_px=20, number_format="percent", minimum=1, maximum=1.5):
        """Native cohort triangle. Missing cells have no fill, border or text.

        The sequential scale uses four semantic heat roles when supplied by the
        model, with neutral/forecast surfaces as a role-only fallback. An actual
        percentage always retains white type even at the strongest heat level.
        """
        headers = ["Cohort", *col_labels]
        rows = [[label, *[None if v is None else f"{financial(v * 100, 0)}%" if number_format == "percent" else financial(v)
                         for v in row]] for label, row in zip(row_labels, values)]
        shape = self.fin_table(slide, headers, rows, x=x, y=y, w=w, h=h,
                               font_px=font_px, numeric_cols=list(range(1, len(headers))))
        shape.name = "native:heatmap_table"
        roles = [f"heat_{i}" if "investor_heat_" + str(i) in self.brand.colors else role
                 for i, role in enumerate(("card", "band", "forecast_fill", "forecast_fill"), 1)]
        for r, row in enumerate(values):
            for c, value in enumerate(row):
                cell = shape.table.cell(r + 1, c + 1)
                if value is None:
                    cell.fill.background()
                else:
                    index = min(3, max(0, int((float(value) - float(minimum)) / (float(maximum) - float(minimum)) * 4)))
                    cell.fill.fore_color.rgb = self.color(roles[index])
        return shape


from io import BytesIO
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


def _fmt(value: Any) -> str:
    if value is None:
        return "Not available"
    if isinstance(value, float):
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def _humanize_key(key: str) -> str:
    return key.replace("_", " ").replace("-", " ").title()


def _flatten_metrics(metrics: dict[str, Any]):
    rows = []
    for key, value in metrics.items():
        if isinstance(value, dict):
            # Keep nested group summaries readable without dumping JSON.
            if all(not isinstance(v, (dict, list)) for v in value.values()):
                for subkey, subvalue in value.items():
                    rows.append([f"{_humanize_key(key)} — {_humanize_key(str(subkey))}", _fmt(subvalue)])
            else:
                rows.append([_humanize_key(key), "Grouped analysis available in report findings"])
        elif isinstance(value, list):
            rows.append([_humanize_key(key), ", ".join(map(str, value[:8]))])
        else:
            rows.append([_humanize_key(key), _fmt(value)])
    return rows


def build_report(payload: dict[str, Any]) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Autonomous Data Analysis Report",
        author="Autonomous Data Analysis Agent",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=21,
        leading=25,
        alignment=TA_CENTER,
        spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="Subtitle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#64748b"),
        alignment=TA_CENTER,
        spaceAfter=18,
    ))
    styles.add(ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#3b1b78"),
        spaceBefore=10,
        spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="BodyReadable",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="Finding",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        leftIndent=8,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748b"),
    ))

    query = payload.get("query", "Data analysis")
    dataset = payload.get("dataset", "Dataset")
    profile = payload.get("profile") or {}
    metrics = payload.get("metrics") or {}
    insights = payload.get("insights") or []
    plan = payload.get("plan") or []
    chart = payload.get("chart") or {}

    rows = profile.get("rows", 0)
    columns = profile.get("columns", 0)
    duplicate_rows = profile.get("duplicate_rows", 0)

    story = []

    story.append(Paragraph("Autonomous Data Analysis Report", styles["ReportTitle"]))
    story.append(Paragraph(
        f"Plain-language analysis generated from <b>{dataset}</b> • "
        f"{datetime.now().strftime('%d %B %Y, %I:%M %p')}",
        styles["Subtitle"]
    ))

    story.append(Paragraph("1. What was analyzed", styles["Section"]))
    story.append(Paragraph(
        f"The user asked the analysis agent: <b>{query}</b>.",
        styles["BodyReadable"]
    ))
    story.append(Paragraph(
        "The agent examined the available data, selected relevant calculations, "
        "validated the returned values, and converted the results into plain-language findings. "
        "This report is designed for readers who do not need programming knowledge.",
        styles["BodyReadable"]
    ))

    story.append(Paragraph("2. Dataset overview", styles["Section"]))
    overview = [
        ["Item", "Value"],
        ["Dataset", dataset],
        ["Number of records", _fmt(rows)],
        ["Number of columns", _fmt(columns)],
        ["Duplicate rows detected", _fmt(duplicate_rows)],
    ]
    table = Table(overview, colWidths=[70 * mm, 95 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#24104b")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#d7dce5")),
        ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#f8fafc")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(table)

    story.append(Paragraph("3. Key findings", styles["Section"]))
    if insights:
        for i, insight in enumerate(insights, 1):
            story.append(Paragraph(f"<b>{i}.</b> {insight}", styles["Finding"]))
    else:
        story.append(Paragraph(
            "No narrative findings were returned for this analysis.",
            styles["BodyReadable"]
        ))

    story.append(Paragraph("4. Results in numbers", styles["Section"]))
    metric_rows = [["Measure", "Result"]] + _flatten_metrics(metrics)
    if len(metric_rows) == 1:
        metric_rows.append(["Status", "No numerical metrics returned"])
    metric_table = Table(metric_rows, colWidths=[85 * mm, 80 * mm], repeatRows=1)
    metric_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#24104b")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#d7dce5")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(metric_table)

    # A simple text-based chart representation that remains readable in PDF.
    labels = chart.get("labels") or []
    values = chart.get("values") or []
    if labels and values and len(labels) == len(values):
        story.append(Paragraph("5. Visual summary", styles["Section"]))
        max_value = max([abs(float(v)) for v in values] + [1])
        chart_rows = [["Group", "Relative size", "Value"]]
        for label, value in zip(labels[:12], values[:12]):
            value_num = float(value)
            blocks = max(1, min(32, round(abs(value_num) / max_value * 32)))
            chart_rows.append([
                str(label),
                "█" * blocks,
                _fmt(value_num),
            ])
        chart_table = Table(chart_rows, colWidths=[43 * mm, 75 * mm, 47 * mm])
        chart_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#24104b")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("TEXTCOLOR", (1,1), (1,-1), colors.HexColor("#6d28d9")),
            ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#d7dce5")),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 5),
            ("RIGHTPADDING", (0,0), (-1,-1), 5),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        story.append(chart_table)
        story.append(Paragraph(
            f"Chart represented: <b>{chart.get('title', 'Analysis chart')}</b>. "
            "The relative bars help readers compare groups quickly; exact values are shown in the last column.",
            styles["Small"]
        ))

    story.append(Paragraph("6. How the agent reached the result", styles["Section"]))
    if plan:
        for step in plan:
            story.append(Paragraph(f"• {step}", styles["BodyReadable"]))
    else:
        story.append(Paragraph(
            "The agent used automated profiling and analysis selection.",
            styles["BodyReadable"]
        ))

    story.append(Paragraph("7. What this means", styles["Section"]))
    if insights:
        story.append(Paragraph(
            "The findings above summarize the patterns identified in the supplied dataset. "
            "They should be interpreted in the context of the selected data and analysis question. "
            "The report does not replace domain expertise or business judgment.",
            styles["BodyReadable"]
        ))
    else:
        story.append(Paragraph(
            "No additional interpretation was generated.",
            styles["BodyReadable"]
        ))

    story.append(Paragraph("8. Technical note", styles["Section"]))
    story.append(Paragraph(
        "The report was generated by the Autonomous Data Analysis Agent. "
        "Calculations are based on the selected dataset available at analysis time. "
        "Any missing values, duplicates, inconsistent entries, or extreme observations "
        "may affect the results and should be reviewed when making decisions.",
        styles["Small"]
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Generated automatically • Autonomous Data Analysis Agent",
        styles["Small"]
    ))

    doc.build(story)
    return buffer.getvalue()

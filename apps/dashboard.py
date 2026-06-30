"""HTML dashboard rendering for Genesis BusinessOS."""

from __future__ import annotations

from html import escape
from typing import Any


def render_business_dashboard(dashboard: dict[str, Any], alerts: dict[str, Any] | list[dict[str, Any]], knowledge: dict[str, Any] | list[dict[str, Any]]) -> str:
    """Render a compact founder dashboard from BusinessOS analytics data."""

    alert_items = alerts.get("alerts", []) if isinstance(alerts, dict) else alerts
    knowledge_items = knowledge.get("knowledge", []) if isinstance(knowledge, dict) else knowledge
    health = dashboard.get("businessHealth", {})
    latest = dashboard.get("latestMetrics", {})
    derived = dashboard.get("derivedMetrics", {})
    departments = dashboard.get("departmentDashboards", [])
    score = health.get("overallBusinessHealthScore", 0)
    status = health.get("status", "UNKNOWN")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Genesis BusinessOS Dashboard</title>
  <style>
    :root {{ color-scheme: light; --ink:#172026; --muted:#5b6770; --line:#d8dee4; --bg:#f7f9fb; --panel:#ffffff; --accent:#0f766e; --warn:#b45309; --danger:#b91c1c; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: var(--bg); color: var(--ink); }}
    header {{ padding: 24px clamp(16px, 5vw, 56px); background: var(--panel); border-bottom: 1px solid var(--line); }}
    main {{ padding: 24px clamp(16px, 5vw, 56px) 48px; display: grid; gap: 18px; }}
    h1 {{ margin: 0 0 6px; font-size: 28px; letter-spacing: 0; }}
    h2 {{ margin: 0 0 12px; font-size: 18px; letter-spacing: 0; }}
    p {{ margin: 0; color: var(--muted); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 16px; }}
    .metric {{ font-size: 28px; font-weight: 750; margin-top: 6px; }}
    .label {{ color: var(--muted); font-size: 13px; }}
    .score {{ color: {score_color(score)}; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 10px 8px; text-align: left; border-bottom: 1px solid var(--line); font-size: 14px; vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 650; }}
    .alert {{ border-left: 4px solid var(--warn); padding: 10px 12px; background: #fff8ed; margin-bottom: 8px; border-radius: 6px; }}
    .alert.high {{ border-left-color: var(--danger); background: #fff1f2; }}
    .empty {{ color: var(--muted); font-style: italic; }}
  </style>
</head>
<body>
  <header>
    <h1>Genesis BusinessOS Dashboard</h1>
    <p>{escape(str(dashboard.get("businessId", "")))} · {escape(str(dashboard.get("currentState", "")))} · {escape(str(dashboard.get("generatedAt", "")))}</p>
  </header>
  <main>
    <section class="grid">
      {metric_card("Health", score, status, css_class="score")}
      {metric_card("Revenue", latest.get("revenue", 0), "latest")}
      {metric_card("Orders", latest.get("orders", 0), "latest")}
      {metric_card("ROAS", derived.get("roas", 0), "derived")}
      {metric_card("Inventory", latest.get("inventoryOnHand", 0), "on hand")}
      {metric_card("Cash", latest.get("cash", 0), "latest")}
    </section>
    <section class="panel">
      <h2>Department Health</h2>
      <table>
        <thead><tr><th>Department</th><th>Score</th><th>KPIs</th></tr></thead>
        <tbody>{department_rows(departments)}</tbody>
      </table>
    </section>
    <section class="panel">
      <h2>Alerts</h2>
      {alert_blocks(alert_items)}
    </section>
    <section class="panel">
      <h2>Knowledge</h2>
      {knowledge_rows(knowledge_items)}
    </section>
  </main>
</body>
</html>"""


def metric_card(title: str, value: object, label: object, *, css_class: str = "") -> str:
    return f"""<div class="panel"><div class="label">{escape(title)}</div><div class="metric {css_class}">{escape(str(value))}</div><div class="label">{escape(str(label))}</div></div>"""


def department_rows(departments: list[dict[str, Any]]) -> str:
    if not departments:
        return '<tr><td colspan="3" class="empty">No department metrics yet.</td></tr>'
    rows = []
    for department in departments:
        kpis = ", ".join(f"{key}: {value}" for key, value in department.get("kpis", {}).items())
        rows.append(f"<tr><td>{escape(str(department.get('department', '')))}</td><td>{escape(str(department.get('score', '')))}</td><td>{escape(kpis)}</td></tr>")
    return "".join(rows)


def alert_blocks(alerts: list[dict[str, Any]]) -> str:
    if not alerts:
        return '<p class="empty">No active alerts.</p>'
    blocks = []
    for alert in alerts:
        severity = str(alert.get("severity", "")).lower()
        blocks.append(
            f"""<div class="alert {'high' if severity == 'high' else ''}"><strong>{escape(str(alert.get('type', 'alert')))}</strong><br>{escape(str(alert.get('message', '')))}<br><span class="label">{escape(str(alert.get('recommendedAction', '')))}</span></div>"""
        )
    return "".join(blocks)


def knowledge_rows(knowledge: list[dict[str, Any]]) -> str:
    if not knowledge:
        return '<p class="empty">No knowledge entries captured yet.</p>'
    rows = []
    for entry in knowledge[-5:]:
        lessons = "; ".join(str(item) for item in entry.get("lessons", []))
        rows.append(f"<p><strong>{escape(str(entry.get('type', 'learning')))}</strong> · {escape(str(entry.get('createdAt', '')))}<br><span class=\"label\">{escape(lessons)}</span></p>")
    return "".join(rows)


def score_color(score: object) -> str:
    if isinstance(score, (int, float)) and score < 50:
        return "var(--danger)"
    if isinstance(score, (int, float)) and score < 70:
        return "var(--warn)"
    return "var(--accent)"

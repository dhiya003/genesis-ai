"""Business analytics runtime for continuous monitoring."""

from __future__ import annotations

from statistics import mean
from typing import Any
from uuid import uuid4

from apps.audit import now_iso
from apps.storage import JsonStore


class AnalyticsRuntime:
    """Ingests business metrics and refreshes dashboard, alerts, and recommendations."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def ingest_metrics(self, business_id: str, metrics: dict[str, Any], *, source: str = "manual", observed_at: str | None = None) -> dict[str, Any]:
        plan = self.store.get_business_operating_plan(business_id)
        normalized_metrics = _normalize_metrics(metrics)
        normalized_metrics["businessId"] = business_id
        event = {
            "id": str(uuid4()),
            "businessId": business_id,
            "source": source,
            "observedAt": observed_at or now_iso(),
            "createdAt": now_iso(),
            "metrics": normalized_metrics,
        }
        self.store.save_business_metric_event(event)
        events = self.store.list_business_metric_events(business_id)
        dashboard = self.build_dashboard(plan, events)
        alerts = _alerts(dashboard, events)
        recommendations = _recommendations(dashboard, alerts)
        knowledge = _knowledge_entry(business_id, event, dashboard, alerts, recommendations)

        self.store.save_business_dashboard(business_id, dashboard)
        self.store.save_business_alerts(business_id, {"businessId": business_id, "alerts": alerts, "updatedAt": now_iso()})
        self.store.save_recommendation_report(business_id, {"businessId": business_id, "recommendations": recommendations})
        self.store.save_business_health_report(business_id, dashboard["businessHealth"])
        self.store.save_business_knowledge_entry(knowledge)
        return {
            "event": event,
            "dashboard": dashboard,
            "alerts": alerts,
            "recommendations": recommendations,
            "knowledgeEntry": knowledge,
        }

    def build_dashboard(self, plan: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
        business_id = plan["businessId"]
        latest = events[-1]["metrics"] if events else {}
        previous = events[-2]["metrics"] if len(events) > 1 else {}
        derived = _derived_metrics(latest)
        health = _health(latest, derived)
        return {
            "reportType": "BUSINESS_DASHBOARD",
            "version": "0.7.0-foundation",
            "businessId": business_id,
            "generatedAt": now_iso(),
            "currentState": plan["digitalTwin"]["currentState"],
            "metricEventCount": len(events),
            "latestMetrics": latest,
            "previousMetrics": previous,
            "derivedMetrics": derived,
            "businessHealth": health,
            "departmentDashboards": _department_dashboards(plan, latest, derived, health),
            "campaignDashboard": _campaign_dashboard(latest, derived),
            "salesDashboard": _sales_dashboard(latest, derived),
            "inventoryDashboard": _inventory_dashboard(latest),
            "financialDashboard": _financial_dashboard(latest, derived),
            "knowledgeDashboard": {"capturedEvents": len(events), "latestLearning": "Metrics ingested into BusinessOS knowledge base."},
        }


def _normalize_metrics(metrics: dict[str, Any]) -> dict[str, float | str]:
    normalized: dict[str, float | str] = {}
    for key, value in metrics.items():
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            normalized[key] = round(float(value), 4)
        elif isinstance(value, str):
            stripped = value.strip()
            try:
                normalized[key] = round(float(stripped), 4)
            except ValueError:
                normalized[key] = stripped
    return normalized


def _num(metrics: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = metrics.get(key, default)
    return float(value) if isinstance(value, (int, float)) else default


def _derived_metrics(metrics: dict[str, Any]) -> dict[str, float]:
    revenue = _num(metrics, "revenue")
    orders = _num(metrics, "orders")
    ad_spend = _num(metrics, "adSpend")
    clicks = _num(metrics, "clicks")
    impressions = _num(metrics, "impressions")
    gross_profit = _num(metrics, "grossProfit", revenue - _num(metrics, "costOfGoods"))
    return {
        "aov": round(revenue / orders, 2) if orders else 0,
        "cac": round(ad_spend / orders, 2) if orders else 0,
        "roas": round(revenue / ad_spend, 2) if ad_spend else 0,
        "ctr": round((clicks / impressions) * 100, 2) if impressions else 0,
        "conversionRate": round((orders / clicks) * 100, 2) if clicks else 0,
        "grossMargin": round((gross_profit / revenue) * 100, 2) if revenue else 0,
    }


def _score(value: float, *, good: float, weak: float) -> int:
    if value >= good:
        return 90
    if value >= weak:
        return 70
    if value > 0:
        return 45
    return 35


def _health(metrics: dict[str, Any], derived: dict[str, float]) -> dict[str, Any]:
    revenue = _num(metrics, "revenue")
    orders = _num(metrics, "orders")
    rating = _num(metrics, "rating")
    inventory = _num(metrics, "inventoryOnHand")
    cash = _num(metrics, "cash")
    dimensions = {
        "revenueHealth": _score(revenue, good=100000, weak=25000),
        "profitHealth": _score(derived["grossMargin"], good=55, weak=35),
        "marketingHealth": _score(derived["roas"], good=2.5, weak=1.2),
        "customerHealth": _score(rating, good=4.3, weak=3.7) if rating else 55,
        "inventoryHealth": 90 if inventory >= 50 else 65 if inventory >= 20 else 35,
        "operationsHealth": 85 if orders else 60,
        "cashFlowHealth": 85 if cash > 0 else 55 if cash == 0 else 25,
    }
    return {
        "businessId": str(metrics.get("businessId", "")),
        **dimensions,
        "overallBusinessHealthScore": round(mean(dimensions.values())),
        "status": "LIVE_METRICS_INGESTED",
        "explanation": "Health score is based on the latest ingested business metrics.",
    }


def _department_dashboards(plan: dict[str, Any], metrics: dict[str, Any], derived: dict[str, float], health: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"department": "Sales", "score": health["revenueHealth"], "kpis": {"revenue": _num(metrics, "revenue"), "orders": _num(metrics, "orders"), "aov": derived["aov"]}},
        {"department": "Marketing", "score": health["marketingHealth"], "kpis": {"adSpend": _num(metrics, "adSpend"), "roas": derived["roas"], "ctr": derived["ctr"], "conversionRate": derived["conversionRate"]}},
        {"department": "Inventory", "score": health["inventoryHealth"], "kpis": {"inventoryOnHand": _num(metrics, "inventoryOnHand"), "reorderThreshold": plan["digitalTwin"].get("inventory", {}).get("reorderThreshold", 25)}},
        {"department": "Finance", "score": health["cashFlowHealth"], "kpis": {"cash": _num(metrics, "cash"), "grossMargin": derived["grossMargin"]}},
        {"department": "Customer", "score": health["customerHealth"], "kpis": {"rating": _num(metrics, "rating"), "reviews": _num(metrics, "reviews")}},
    ]


def _campaign_dashboard(metrics: dict[str, Any], derived: dict[str, float]) -> dict[str, Any]:
    return {"adSpend": _num(metrics, "adSpend"), "clicks": _num(metrics, "clicks"), "impressions": _num(metrics, "impressions"), "roas": derived["roas"], "ctr": derived["ctr"], "conversionRate": derived["conversionRate"]}


def _sales_dashboard(metrics: dict[str, Any], derived: dict[str, float]) -> dict[str, Any]:
    return {"revenue": _num(metrics, "revenue"), "orders": _num(metrics, "orders"), "refunds": _num(metrics, "refunds"), "aov": derived["aov"]}


def _inventory_dashboard(metrics: dict[str, Any]) -> dict[str, Any]:
    inventory = _num(metrics, "inventoryOnHand")
    return {"inventoryOnHand": inventory, "status": "REORDER" if inventory < 20 else "WATCH" if inventory < 50 else "HEALTHY"}


def _financial_dashboard(metrics: dict[str, Any], derived: dict[str, float]) -> dict[str, Any]:
    return {"cash": _num(metrics, "cash"), "revenue": _num(metrics, "revenue"), "grossProfit": _num(metrics, "grossProfit"), "grossMargin": derived["grossMargin"]}


def _alerts(dashboard: dict[str, Any], events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metrics = dashboard["latestMetrics"]
    derived = dashboard["derivedMetrics"]
    alerts: list[dict[str, Any]] = []
    if _num(metrics, "inventoryOnHand") < 20:
        alerts.append({"severity": "HIGH", "type": "inventory.low", "message": "Inventory is below reorder threshold.", "recommendedAction": "Review supplier lead time and reorder quantity."})
    if _num(metrics, "adSpend") > 0 and derived["roas"] < 1.2:
        alerts.append({"severity": "HIGH", "type": "marketing.roas_low", "message": "ROAS is below target.", "recommendedAction": "Pause budget scaling and review creative/audience performance."})
    if _num(metrics, "rating") and _num(metrics, "rating") < 3.7:
        alerts.append({"severity": "MEDIUM", "type": "customer.rating_low", "message": "Customer rating is below healthy threshold.", "recommendedAction": "Inspect reviews and trigger customer success follow-up."})
    if len(events) >= 2 and _num(events[-1]["metrics"], "revenue") < _num(events[-2]["metrics"], "revenue") * 0.8:
        alerts.append({"severity": "MEDIUM", "type": "revenue.drop", "message": "Revenue dropped more than 20% versus previous metric event.", "recommendedAction": "Review traffic, conversion, pricing, and stock status."})
    if _num(metrics, "cash") < 0:
        alerts.append({"severity": "HIGH", "type": "cash.negative", "message": "Cash is negative.", "recommendedAction": "Block discretionary spend and review payables."})
    return alerts


def _recommendations(dashboard: dict[str, Any], alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    recommendations = [
        {"recommendation": "Keep monitoring launch KPIs daily.", "priority": "MEDIUM", "confidence": 0.78, "evidence": dashboard["derivedMetrics"], "approvalRequirement": "automatic"},
    ]
    for alert in alerts:
        recommendations.insert(
            0,
            {
                "recommendation": alert["recommendedAction"],
                "priority": alert["severity"],
                "confidence": 0.82,
                "evidence": alert,
                "approvalRequirement": "founder approval" if alert["severity"] == "HIGH" else "operator review",
            },
        )
    return recommendations


def _knowledge_entry(business_id: str, event: dict[str, Any], dashboard: dict[str, Any], alerts: list[dict[str, Any]], recommendations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": str(uuid4()),
        "businessId": business_id,
        "createdAt": now_iso(),
        "type": "METRIC_INGESTION",
        "source": event["source"],
        "evidence": {"metricEventId": event["id"], "health": dashboard["businessHealth"], "alerts": alerts},
        "lessons": [recommendation["recommendation"] for recommendation in recommendations],
        "confidence": 0.8,
    }

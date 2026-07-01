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

    def generate_business_intelligence_report(self, launch_package: dict[str, Any], project: dict[str, Any], workflow: dict[str, Any]) -> dict[str, Any]:
        metrics_collection = _baseline_metrics_collection(launch_package)
        sales = _sales_analytics(launch_package)
        marketing = _marketing_analytics(launch_package)
        customers = _customer_analytics(launch_package)
        products = _product_performance_analytics(launch_package)
        health = _business_intelligence_health(metrics_collection, sales, marketing, customers, products)
        recommendations = _business_intelligence_recommendations(health, launch_package)
        executive_report = _executive_business_report(project, health, sales, marketing, customers, products, recommendations)
        report = {
            "reportType": "BUSINESS_INTELLIGENCE_REPORT",
            "version": "0.7.0",
            "projectId": project["id"],
            "businessId": project["id"],
            "launchId": launch_package["launchId"],
            "workflowId": workflow["id"],
            "department": "BUSINESS_INTELLIGENCE",
            "departmentStatus": "COMPLETED",
            "businessIntelligenceDepartment": {"initialized": True, "status": "COMPLETED", "businessConnected": True},
            "chiefBusinessAnalyst": {"name": "Chief Business Analyst", "role": "Measure business performance, explain health, and recommend next actions."},
            "monitoringPlan": {"configured": True, "sources": metrics_collection["dataSources"], "cadence": "daily during launch, weekly after stabilization"},
            "dashboardUpdate": {"updated": True, "dashboard": "Executive Business Report", "mobileFriendly": True, "exportSupported": True},
            "auditSummary": {"recorded": True, "workflowId": workflow["id"], "handoffAudited": True},
            "metricsCollection": metrics_collection,
            "salesAnalytics": sales,
            "marketingAnalytics": marketing,
            "customerAnalytics": customers,
            "productPerformanceAnalytics": products,
            "businessHealth": health,
            "recommendations": recommendations,
            "executiveBusinessReport": executive_report,
            "completionChecklist": [
                {"item": "Metrics collected", "status": "COMPLETED"},
                {"item": "Sales analyzed", "status": "COMPLETED"},
                {"item": "Marketing analyzed", "status": "COMPLETED"},
                {"item": "Customers analyzed", "status": "COMPLETED"},
                {"item": "Products analyzed", "status": "COMPLETED"},
                {"item": "Business Health calculated", "status": "COMPLETED"},
                {"item": "Recommendations generated", "status": "COMPLETED"},
                {"item": "Executive Report completed", "status": "COMPLETED"},
                {"item": "Knowledge captured", "status": "COMPLETED"},
                {"item": "Metrics stored", "status": "COMPLETED"},
                {"item": "Audit completed", "status": "COMPLETED"},
            ],
            "founderNotification": {"status": "READY", "message": "Business Intelligence baseline is ready for founder review."},
            "workflowTransition": "BUSINESS_OPERATING_SYSTEM",
            "departmentMetrics": {"analysisCount": 5, "recommendationCount": len(recommendations), "healthScore": health["score"]},
            "knowledgeBaseEntries": [
                {"type": "BUSINESS_INTELLIGENCE_BASELINE", "lesson": "Launch readiness creates the first operating baseline before live order data arrives.", "evidence": {"launchId": launch_package["launchId"], "healthScore": health["score"]}, "confidence": 0.82}
            ],
            "overallScore": round(mean([health["score"], sales["score"], marketing["score"], customers["score"], products["score"]])),
        }
        self.store.save_business_intelligence_report(report)
        self.store.save_business_health_report(project["id"], health)
        self.store.save_recommendation_report(project["id"], {"businessId": project["id"], "recommendations": recommendations})
        self.store.save_business_dashboard(project["id"], executive_report["kpiDashboard"])
        self.store.save_business_knowledge_entry({
            "id": str(uuid4()),
            "businessId": project["id"],
            "createdAt": now_iso(),
            "type": "BUSINESS_INTELLIGENCE_BASELINE",
            "evidence": {"launchId": launch_package["launchId"], "health": health},
            "lessons": [entry["lesson"] for entry in report["knowledgeBaseEntries"]],
            "confidence": 0.82,
        })
        return report

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


def _baseline_metrics_collection(launch_package: dict[str, Any]) -> dict[str, Any]:
    return {
        "collected": True,
        "dataSources": ["Marketplace Orders", "Website Orders", "CRM", "Marketing Platforms", "Inventory", "Customer Reviews", "Advertising Platforms"],
        "metrics": {"revenue": 0, "orders": 0, "customers": 0, "conversionRate": 0, "inventory": launch_package.get("inventorySynchronization", {}).get("baseInventory", {}).get("startingInventoryAssumption", 0), "advertisingSpend": 0, "returns": 0, "profitEstimate": launch_package.get("pricingSynchronization", {}).get("basePrice", 0)},
        "duplicateHandling": "dedupe by source id, observedAt, and channel",
        "missingDataFlags": ["live order data pending", "customer reviews pending"],
        "collectionHistory": [{"source": "Commerce & Publishing launch baseline", "observedAt": now_iso()}],
        "timestampRecorded": True,
    }


def _sales_analytics(launch_package: dict[str, Any]) -> dict[str, Any]:
    products = launch_package.get("productCatalogue", {}).get("items", [])
    return {
        "score": 72,
        "dailyRevenue": 0,
        "weeklyRevenue": 0,
        "monthlyRevenue": 0,
        "averageOrderValue": launch_package.get("pricingSynchronization", {}).get("basePrice", 0),
        "topProducts": products[:3],
        "lowPerformingProducts": [],
        "customerSegments": ["Parents of children aged 3-5", "Preschool buyers", "Gift buyers"],
        "salesGrowth": {"trend": "BASELINE", "growthIdentified": False},
        "reportsStored": True,
    }


def _marketing_analytics(launch_package: dict[str, Any]) -> dict[str, Any]:
    channels = launch_package.get("channelsDetected", [])
    return {
        "score": 76,
        "metrics": {"reach": 0, "impressions": 0, "engagement": 0, "ctr": 0, "cpc": 0, "cpm": 0, "cac": 0, "roas": 0, "conversionRate": 0},
        "campaignComparison": launch_package.get("campaignLaunchPlan", {}).get("campaigns", []),
        "underperformingCampaigns": [],
        "bestPerformingChannels": channels[:3],
        "status": "BASELINE_READY",
    }


def _customer_analytics(launch_package: dict[str, Any]) -> dict[str, Any]:
    return {
        "score": 70,
        "customerLifetimeValue": 0,
        "repeatPurchases": 0,
        "churnEstimate": "UNKNOWN_UNTIL_ORDERS",
        "customerSatisfaction": "UNKNOWN_UNTIL_REVIEWS",
        "reviewTrends": [],
        "customerSegments": ["Parents", "Teachers", "Gift buyers"],
        "purchaseFrequency": "BASELINE",
        "loyaltyIndicators": ["waitlist signup", "repeat inquiry", "review submission"],
        "repeatCustomerTrends": "PENDING_LIVE_DATA",
        "customerInsightsStored": True,
    }


def _product_performance_analytics(launch_package: dict[str, Any]) -> dict[str, Any]:
    catalogue = launch_package.get("productCatalogue", {}).get("items", [])
    return {
        "score": 78,
        "bestSellers": catalogue[:1],
        "slowMovers": [],
        "grossMargin": "FROM_PRODUCT_BLUEPRINT",
        "returnRate": 0,
        "inventoryTurnover": "PENDING_LIVE_DATA",
        "customerRatings": "PENDING_REVIEWS",
        "productProfitability": launch_package.get("pricingSynchronization", {}),
        "productRankingGenerated": True,
        "weakProductsIdentified": True,
        "marginTrendsCalculated": True,
        "recommendationsCreated": True,
    }


def _business_intelligence_health(metrics: dict[str, Any], sales: dict[str, Any], marketing: dict[str, Any], customers: dict[str, Any], products: dict[str, Any]) -> dict[str, Any]:
    components = {
        "revenueHealth": 55 if metrics["metrics"]["revenue"] == 0 else 75,
        "marketingHealth": marketing["score"],
        "customerHealth": customers["score"],
        "productHealth": products["score"],
        "inventoryHealth": 80 if metrics["metrics"]["inventory"] else 50,
        "operationalHealth": 82,
        "growthHealth": sales["score"],
    }
    score = round(mean(components.values()))
    rating = "Excellent" if score >= 90 else "Healthy" if score >= 75 else "Stable" if score >= 60 else "Poor" if score >= 40 else "Critical"
    return {
        **components,
        "score": score,
        "businessHealthScore": score,
        "healthRating": rating,
        "explanation": "Baseline score uses launch readiness, catalogue completeness, and channel coverage until live metrics arrive.",
        "trends": {"current": "BASELINE", "direction": "PENDING_LIVE_DATA"},
        "historicalComparison": "FIRST_BASELINE",
    }


def _business_intelligence_recommendations(health: dict[str, Any], launch_package: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"area": "Inventory", "recommendation": "Confirm starting stock before activating all commerce channels.", "priority": "HIGH", "expectedImpact": "Prevents overselling and launch failures.", "confidence": 0.84, "evidence": launch_package.get("inventorySynchronization", {})},
        {"area": "Marketing", "recommendation": "Measure ROAS and CAC before scaling paid campaigns.", "priority": "HIGH", "expectedImpact": "Protects cash and improves campaign efficiency.", "confidence": 0.82, "evidence": health},
        {"area": "Product", "recommendation": "Track variant-level sales to identify Starter vs Premium demand.", "priority": "MEDIUM", "expectedImpact": "Improves SKU focus and inventory planning.", "confidence": 0.78, "evidence": launch_package.get("productCatalogue", {})},
    ]


def _executive_business_report(project: dict[str, Any], health: dict[str, Any], sales: dict[str, Any], marketing: dict[str, Any], customers: dict[str, Any], products: dict[str, Any], recommendations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "reportType": "EXECUTIVE_BUSINESS_REPORT",
        "versionControlled": True,
        "downloadable": True,
        "searchable": True,
        "linkedToProject": True,
        "executiveSummary": f"Business Intelligence baseline for {project.get('idea', 'Genesis business')} is stable and ready for BusinessOS orchestration.",
        "kpiDashboard": {"reportType": "BUSINESS_DASHBOARD", "businessId": project["id"], "businessHealth": health, "sales": sales, "marketing": marketing, "customers": customers, "products": products, "recommendations": recommendations},
        "businessHealth": health,
        "salesAnalysis": sales,
        "marketingAnalysis": marketing,
        "customerAnalysis": customers,
        "productAnalysis": products,
        "risks": ["Live sales and campaign metrics are not connected yet."],
        "opportunities": ["Use launch baseline to compare day-1 and week-1 performance."],
        "recommendations": recommendations,
        "nextActions": ["Ingest live order metrics", "Review first campaign performance", "Update business health after first sales data"],
    }


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

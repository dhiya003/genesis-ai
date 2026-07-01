"""Executable Sales Department employees for Sprint 6."""

from __future__ import annotations

from typing import Any


SALES_EMPLOYEES: dict[str, dict[str, Any]] = {
    "EMP-401": {"name": "Sales Director", "section": "salesStrategy", "role": "Initialize sales execution, channels, pipeline, and lead policies.", "inputSchema": {"required": ["marketingPack"]}, "outputSchema": {"required": ["salesExecutionPlan", "communicationChannels", "pipelineStages"]}, "promptContract": "Convert Marketing Pack into a sales operating plan.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-402": {"name": "Lead Qualification Specialist", "section": "leadQualification", "role": "Capture, deduplicate, score, prioritize, and recommend follow-ups for leads.", "inputSchema": {"required": ["marketingPack"]}, "outputSchema": {"required": ["leads", "duplicateLeads", "qualificationRules"]}, "promptContract": "Qualify sales leads using intent, budget, timeline, fit, location, and history.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-403": {"name": "AI Sales Conversation Agent", "section": "salesConversations", "role": "Create channel-safe sales responses and escalation rules.", "inputSchema": {"required": ["productBlueprint", "creativePack", "leadQualification"]}, "outputSchema": {"required": ["conversationPlaybooks", "conversationHistory", "escalationRules"]}, "promptContract": "Answer product questions in brand voice and escalate when needed.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-404": {"name": "Quotation Specialist", "section": "quotations", "role": "Generate quotation drafts from product pricing and customer details.", "inputSchema": {"required": ["productBlueprint", "leadQualification"]}, "outputSchema": {"required": ["quotes", "versionHistory", "exportFormats"]}, "promptContract": "Create accurate quotations with taxes, shipping, terms, and validity.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-405": {"name": "Follow-Up Automation Specialist", "section": "followUpAutomation", "role": "Create follow-up schedules, stop conditions, and dedupe policy.", "inputSchema": {"required": ["leadQualification", "quotations"]}, "outputSchema": {"required": ["followUpSchedules", "communicationHistory", "stopConditions"]}, "promptContract": "Prevent lead leakage through configurable follow-up automation.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-406": {"name": "CRM Synchronization Specialist", "section": "crmSynchronization", "role": "Synchronize contacts, scores, opportunities, conversations, quotes, orders, and notes.", "inputSchema": {"required": ["leadQualification", "salesConversations", "quotations"]}, "outputSchema": {"required": ["customerRecords", "duplicateDetection", "accessControl"]}, "promptContract": "Maintain a consistent customer view across Genesis departments.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-407": {"name": "Pipeline Manager", "section": "salesPipeline", "role": "Track opportunity stages, history, transitions, and lost reasons.", "inputSchema": {"required": ["crmSynchronization", "quotations"]}, "outputSchema": {"required": ["opportunities", "stageConfiguration", "transitionAudit"]}, "promptContract": "Manage sales pipeline visibility and bottleneck tracking.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-408": {"name": "Order Handoff Specialist", "section": "orderHandoff", "role": "Confirm won opportunities and prepare fulfilment handoff.", "inputSchema": {"required": ["salesPipeline", "productBlueprint"]}, "outputSchema": {"required": ["orders", "fulfilmentNotifications", "customerConfirmations"]}, "promptContract": "Convert won opportunities into fulfilment-ready order handoffs.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-409": {"name": "Sales Analytics Specialist", "section": "salesAnalytics", "role": "Calculate sales performance metrics, trends, reports, and dashboard updates.", "inputSchema": {"required": ["salesPipeline", "orderHandoff"]}, "outputSchema": {"required": ["metrics", "trends", "reports", "dashboardUpdate"]}, "promptContract": "Measure lead volume, conversion, average deal value, cycle time, and revenue.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-410": {"name": "Sales QA Manager", "section": "salesQaReport", "role": "Validate Sales Package completion, knowledge capture, founder notification, and Commerce handoff.", "inputSchema": {"required": ["salesSections"]}, "outputSchema": {"required": ["checks", "completionChecklist", "risks"]}, "promptContract": "Run final sales quality gates before Commerce and Publishing.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
}


def run_sales_employee(employee_id: str, context: dict[str, Any]) -> dict[str, Any]:
    """Run a deterministic Sales Department employee."""

    if employee_id not in SALES_EMPLOYEES:
        raise KeyError(f"Unknown Sales Department employee: {employee_id}")
    contract = SALES_EMPLOYEES[employee_id]
    builders = {
        "EMP-401": _sales_strategy_output,
        "EMP-402": _lead_qualification_output,
        "EMP-403": _conversation_output,
        "EMP-404": _quotation_output,
        "EMP-405": _followup_output,
        "EMP-406": _crm_output,
        "EMP-407": _pipeline_output,
        "EMP-408": _order_output,
        "EMP-409": _analytics_output,
        "EMP-410": _qa_output,
    }
    data = builders[employee_id](context)
    output = {
        "employeeId": employee_id,
        "employeeName": contract["name"],
        "department": "SALES",
        "section": contract["section"],
        "status": "COMPLETED",
        "score": data.pop("score", 82),
        "confidence": data.pop("confidence", {"level": "MEDIUM", "score": 0.75}),
        "risks": data.pop("risks", []),
        "validation": data.pop("validation", _default_validation()),
        "contract": contract,
        **data,
    }
    issues = validate_sales_employee_output(output)
    if issues:
        raise ValueError(f"{employee_id} output validation failed: {issues}")
    return output


def validate_sales_employee_output(output: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    employee_id = output.get("employeeId")
    contract = SALES_EMPLOYEES.get(str(employee_id))
    if not contract:
        return [f"unknown employee: {employee_id}"]
    for key in ["employeeId", "employeeName", "department", "section", "status", "score", "confidence", "validation", "contract"]:
        if key not in output:
            issues.append(f"missing key: {key}")
    if output.get("section") != contract["section"]:
        issues.append(f"section must be {contract['section']}")
    score = output.get("score")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("score must be 0-100")
    for key in contract["outputSchema"]["required"]:
        if key not in output:
            issues.append(f"missing contract output: {key}")
    validation = output.get("validation")
    if not isinstance(validation, dict) or not all(validation.get(key) == "PASS" for key in ["schema", "crm", "conversation", "pricing", "risk"]):
        issues.append("validation gates must all PASS")
    return issues


def _default_validation() -> dict[str, str]:
    return {"schema": "PASS", "crm": "PASS", "conversation": "PASS", "pricing": "PASS", "risk": "PASS"}


def _brand(context: dict[str, Any]) -> str:
    return str(context["creativePack"].get("brandIdentity", {}).get("brandName", "Genesis Brand"))


def _product(context: dict[str, Any]) -> str:
    return str(context["productBlueprint"].get("productName", "Genesis Product"))


def _price(context: dict[str, Any]) -> int:
    return int(context["productBlueprint"].get("pricingStrategy", {}).get("retailPrice", 1299))


def _sales_strategy_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "salesExecutionPlan": ["Capture demand", "Qualify leads", "Respond in brand voice", "Send quotation", "Follow up", "Sync CRM", "Move pipeline", "Confirm order"],
        "communicationChannels": ["WhatsApp", "Instagram DM", "Facebook Messenger", "Website Chat", "Email", "Marketplace enquiries", "Manual entry"],
        "pipelineStages": ["New Lead", "Qualified", "Proposal Sent", "Negotiation", "Awaiting Decision", "Won", "Lost"],
        "salesPolicies": {"humanEscalation": "Founder escalation for discounts, safety/legal claims, bulk orders, or angry customers.", "defaultCurrency": "INR"},
        "score": 85,
    }


def _lead_qualification_output(context: dict[str, Any]) -> dict[str, Any]:
    leads = [
        {"leadId": "lead-001", "source": "WhatsApp", "name": "Priya Sharma", "intent": "HIGH", "budget": 2500, "timeline": "This week", "productFit": "HIGH", "purchaseReadiness": "READY", "location": "Bengaluru", "previousInteractions": 1, "score": 88, "priority": "HIGH", "followUpRecommendation": "Send Starter and Premium quote with founder-batch availability."},
        {"leadId": "lead-002", "source": "Instagram", "name": "Aarav Gifts", "intent": "MEDIUM", "budget": 10000, "timeline": "This month", "productFit": "MEDIUM", "purchaseReadiness": "CONSIDERING", "location": "Mumbai", "previousInteractions": 0, "score": 72, "priority": "MEDIUM", "followUpRecommendation": "Ask quantity and gifting date, then suggest bundle pricing."},
        {"leadId": "lead-003", "source": "Website", "name": "Little Steps Preschool", "intent": "MEDIUM", "budget": 20000, "timeline": "30 days", "productFit": "HIGH", "purchaseReadiness": "QUALIFY", "location": "Chennai", "previousInteractions": 0, "score": 76, "priority": "MEDIUM", "followUpRecommendation": "Offer classroom kit discussion and founder escalation."},
    ]
    return {"leads": leads, "duplicateLeads": [{"leadId": "lead-001", "duplicateSource": "Email", "resolution": "MERGED"}], "qualificationRules": ["Intent", "Budget", "Timeline", "Product fit", "Purchase readiness", "Location", "Previous interactions"], "crmUpdated": True, "score": 86}


def _conversation_output(context: dict[str, Any]) -> dict[str, Any]:
    brand = _brand(context)
    product = _product(context)
    return {
        "conversationPlaybooks": [
            {"channel": "WhatsApp", "intent": "price", "response": f"{brand} {product} starts with the Starter kit. I can share a founder-batch quote and delivery estimate.", "brandVoice": "warm expert"},
            {"channel": "Instagram DM", "intent": "safety", "response": "The product plan uses rounded wooden pieces and certification placeholders; final safety claims are reviewed before production.", "brandVoice": "clear parent guide"},
            {"channel": "Email", "intent": "bulk", "response": "For preschool or gifting quantities, I can prepare a quantity-based quote for founder review.", "brandVoice": "professional"},
        ],
        "conversationHistory": [{"leadId": "lead-001", "channel": "WhatsApp", "messages": 3, "status": "QUOTE_READY"}],
        "escalationRules": ["Discount request over 10%", "Safety certification claim", "Bulk order over 25 units", "Customer complaint"],
        "customerSatisfactionFeedback": [{"leadId": "lead-001", "rating": "POSITIVE", "note": "Asked for quote after product explanation."}],
        "score": 82,
    }


def _quotation_output(context: dict[str, Any]) -> dict[str, Any]:
    unit_price = _price(context)
    product = _product(context)
    quotes = [
        {"quoteId": "quote-001", "customerId": "lead-001", "productDetails": product, "quantity": 1, "unitPrice": unit_price, "discount": 0, "taxes": 0, "shippingEstimate": 90, "total": unit_price + 90, "validityPeriod": "7 days", "terms": "Subject to final supplier and safety review.", "status": "SENT"},
        {"quoteId": "quote-002", "customerId": "lead-002", "productDetails": product, "quantity": 10, "unitPrice": unit_price, "discount": 1000, "taxes": 0, "shippingEstimate": 350, "total": (unit_price * 10) - 1000 + 350, "validityPeriod": "7 days", "terms": "Bulk pricing requires founder approval.", "status": "DRAFT"},
    ]
    return {"quotes": quotes, "pricingSource": "Product Blueprint pricingStrategy", "versionHistory": [{"quoteId": "quote-001", "version": 1, "status": "SENT"}], "exportFormats": ["json", "pdf"], "score": 84}


def _followup_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "followUpSchedules": [
            {"leadId": "lead-001", "type": "Quote reminder", "delayHours": 24, "channel": "WhatsApp"},
            {"leadId": "lead-002", "type": "Abandoned enquiry", "delayHours": 48, "channel": "Instagram DM"},
            {"leadId": "lead-003", "type": "Appointment reminder", "delayHours": 72, "channel": "Email"},
        ],
        "communicationHistory": [{"leadId": "lead-001", "events": ["quote sent", "reminder scheduled"]}],
        "duplicateFollowUpPolicy": "One active follow-up per lead/channel/type.",
        "stopConditions": ["Customer replies", "Order confirmed", "Lead unsubscribes", "Founder manually pauses"],
        "score": 81,
    }


def _crm_output(context: dict[str, Any]) -> dict[str, Any]:
    leads = context["sections"]["leadQualification"]["leads"]
    return {
        "customerRecords": [{"contact": lead["name"], "company": None, "leadScore": lead["score"], "opportunityStage": "Qualified" if lead["score"] >= 75 else "New Lead", "conversationHistory": [], "quotations": [], "orders": [], "notes": [lead["followUpRecommendation"]]} for lead in leads],
        "duplicateDetection": {"performed": True, "duplicatesMerged": 1},
        "historyPreserved": True,
        "accessControl": {"founder": "FULL", "sales": "FULL", "marketing": "READ", "publishing": "ORDER_HANDOFF_ONLY"},
        "score": 83,
    }


def _pipeline_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "stageConfiguration": ["New Lead", "Qualified", "Proposal Sent", "Negotiation", "Awaiting Decision", "Won", "Lost"],
        "opportunities": [
            {"opportunityId": "opp-001", "leadId": "lead-001", "stage": "Proposal Sent", "value": _price(context), "history": ["New Lead", "Qualified", "Proposal Sent"], "lostReason": None},
            {"opportunityId": "opp-002", "leadId": "lead-002", "stage": "Negotiation", "value": _price(context) * 10, "history": ["New Lead", "Qualified", "Proposal Sent", "Negotiation"], "lostReason": None},
            {"opportunityId": "opp-003", "leadId": "lead-003", "stage": "Qualified", "value": _price(context) * 15, "history": ["New Lead", "Qualified"], "lostReason": None},
        ],
        "transitionAudit": [{"opportunityId": "opp-001", "from": "Qualified", "to": "Proposal Sent", "actor": "Genesis Sales"}],
        "lostReasons": ["Price", "Timeline", "Product fit", "No response"],
        "score": 82,
    }


def _order_output(context: dict[str, Any]) -> dict[str, Any]:
    product = _product(context)
    return {
        "orders": [{"orderId": "order-001", "customerId": "lead-001", "productDetails": product, "quantity": 1, "paymentStatus": "PENDING", "deliveryInstructions": "Ship after founder-batch confirmation", "internalNotes": "Verify safety and stock before final confirmation."}],
        "fulfilmentNotifications": [{"orderId": "order-001", "target": "Commerce & Publishing", "status": "READY"}],
        "customerConfirmations": [{"orderId": "order-001", "message": "Thanks. Your founder-batch order request is recorded and will be confirmed after final availability review."}],
        "auditRecorded": True,
        "score": 80,
    }


def _analytics_output(context: dict[str, Any]) -> dict[str, Any]:
    opportunities = context["sections"]["salesPipeline"]["opportunities"]
    orders = context["sections"]["orderHandoff"]["orders"]
    lead_volume = len(context["sections"]["leadQualification"]["leads"])
    revenue = sum(item["value"] for item in opportunities if item["stage"] in {"Proposal Sent", "Negotiation", "Won"})
    return {
        "metrics": {"leadVolume": lead_volume, "conversionRate": round(len(orders) / lead_volume, 2), "averageDealValue": round(revenue / max(len(opportunities), 1)), "salesCycle": "3-14 days estimate", "revenue": revenue, "lostOpportunities": 0, "followUpEffectiveness": "PENDING_LIVE_DATA"},
        "trends": [{"metric": "leadScore", "direction": "PROMISING", "note": "Two medium/high-intent leads available for follow-up."}],
        "reports": [{"name": "Sales Performance Report", "status": "GENERATED"}],
        "dashboardUpdate": {"status": "UPDATED", "widgets": ["Lead volume", "Pipeline value", "Quote status", "Order handoff"]},
        "score": 81,
    }


def _qa_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "checks": [
            {"check": "Lead qualification complete", "status": "PASS"},
            {"check": "Conversations prepared", "status": "PASS"},
            {"check": "Quotations generated", "status": "PASS"},
            {"check": "CRM synchronized", "status": "PASS"},
            {"check": "Orders handed off or opportunities tracked", "status": "PASS"},
        ],
        "completionChecklist": ["Lead qualification complete", "Customer conversations completed", "Quotations generated", "Follow-ups scheduled", "CRM synchronized", "Pipeline updated", "Orders confirmed or opportunities tracked", "Metrics recorded", "Audit completed"],
        "risks": ["Live channel sending requires WhatsApp/Instagram/email credentials.", "Payment and inventory confirmation remain Commerce responsibilities."],
        "score": 83,
    }

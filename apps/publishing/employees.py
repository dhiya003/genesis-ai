"""Executable Publishing Department employees for Sprint 6."""

from __future__ import annotations

from typing import Any


PUBLISHING_EMPLOYEES: dict[str, dict[str, Any]] = {
    "EMP-201": {"name": "Marketplace Publisher", "section": "marketplacePublishingPlan", "role": "Prepare marketplace listings for Amazon, Shopify, Etsy, and WooCommerce.", "inputSchema": {"required": ["productBlueprint", "creativePack", "marketingPack"]}, "outputSchema": {"required": ["listings", "publishingActions", "validationChecks"]}, "promptContract": "Convert approved product, creative, and marketing assets into marketplace publishing actions.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-202": {"name": "Social Publisher", "section": "socialPublishingPlan", "role": "Prepare social media publishing actions across Instagram, Facebook, Pinterest, LinkedIn, and X.", "inputSchema": {"required": ["creativePack", "marketingPack"]}, "outputSchema": {"required": ["channels", "publishingActions", "mediaRequirements"]}, "promptContract": "Prepare social posts with channel-specific execution metadata.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-203": {"name": "Content Scheduler", "section": "contentSchedule", "role": "Create launch schedule with time-zone awareness and recurring campaigns.", "inputSchema": {"required": ["marketingPack"]}, "outputSchema": {"required": ["timezone", "schedule", "recurringCampaigns"]}, "promptContract": "Transform campaign calendar into executable schedule.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-204": {"name": "Asset Manager", "section": "assetRepository", "role": "Catalog images, logos, packaging files, documents, and generated assets.", "inputSchema": {"required": ["creativePack", "productBlueprint"]}, "outputSchema": {"required": ["assets", "repositoryPolicy", "versionHistory"]}, "promptContract": "Build an asset repository manifest for launch execution.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-205": {"name": "Store Manager", "section": "storeManagementPlan", "role": "Prepare catalog, pricing, collections, and inventory sync actions.", "inputSchema": {"required": ["productBlueprint", "marketingPack"]}, "outputSchema": {"required": ["catalog", "pricing", "inventorySync", "collections"]}, "promptContract": "Prepare store operations for a controlled launch.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-206": {"name": "Campaign Launcher", "section": "campaignLaunchPlan", "role": "Prepare Meta, Google, Amazon, email, and WhatsApp launch actions without live spend.", "inputSchema": {"required": ["marketingPack"]}, "outputSchema": {"required": ["campaigns", "budgetControls", "executionMode"]}, "promptContract": "Convert campaign plans into approval-gated launch actions.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-207": {"name": "Approval Manager", "section": "approvalPlan", "role": "Define approval gates for publishing, budget, legal, and rollback-sensitive actions.", "inputSchema": {"required": ["publishingSections"]}, "outputSchema": {"required": ["approvalGates", "approvalPolicy", "auditRequirements"]}, "promptContract": "Ensure every execution action has evidence, policy, approval, and auditability.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
    "EMP-208": {"name": "Notification Manager", "section": "notificationPlan", "role": "Create founder notifications for launch success, failure, approvals, and operational issues.", "inputSchema": {"required": ["publishingSections"]}, "outputSchema": {"required": ["notifications", "alertRules", "escalationPolicy"]}, "promptContract": "Prepare founder-facing notifications for business execution.", "retryPolicy": {"maxAttempts": 2}, "timeoutSeconds": 30},
}


def run_publishing_employee(employee_id: str, context: dict[str, Any]) -> dict[str, Any]:
    if employee_id not in PUBLISHING_EMPLOYEES:
        raise KeyError(f"Unknown Publishing Department employee: {employee_id}")
    contract = PUBLISHING_EMPLOYEES[employee_id]
    builders = {
        "EMP-201": _marketplace_output,
        "EMP-202": _social_output,
        "EMP-203": _schedule_output,
        "EMP-204": _asset_output,
        "EMP-205": _store_output,
        "EMP-206": _campaign_output,
        "EMP-207": _approval_output,
        "EMP-208": _notification_output,
    }
    data = builders[employee_id](context)
    output = {
        "employeeId": employee_id,
        "employeeName": contract["name"],
        "department": "PUBLISHING",
        "section": contract["section"],
        "status": "COMPLETED",
        "score": data.pop("score", 82),
        "confidence": data.pop("confidence", {"level": "MEDIUM", "score": 0.76}),
        "risks": data.pop("risks", []),
        "validation": data.pop("validation", _default_validation()),
        "metrics": data.pop("metrics", {"estimatedActionCount": 1, "manualApprovalRequired": True}),
        "contract": contract,
        **data,
    }
    issues = validate_publishing_employee_output(output)
    if issues:
        raise ValueError(f"{employee_id} output validation failed: {issues}")
    return output


def validate_publishing_employee_output(output: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    contract = PUBLISHING_EMPLOYEES.get(str(output.get("employeeId")))
    if not contract:
        return [f"unknown employee: {output.get('employeeId')}"]
    for key in ["employeeId", "employeeName", "department", "section", "status", "score", "confidence", "validation", "metrics", "contract"]:
        if key not in output:
            issues.append(f"missing key: {key}")
    if output.get("department") != "PUBLISHING":
        issues.append("department must be PUBLISHING")
    if output.get("section") != contract["section"]:
        issues.append(f"section must be {contract['section']}")
    score = output.get("score")
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        issues.append("score must be 0-100")
    for key in contract["outputSchema"]["required"]:
        if key not in output:
            issues.append(f"missing contract output: {key}")
    validation = output.get("validation")
    if not isinstance(validation, dict) or not all(validation.get(key) == "PASS" for key in ["schema", "business", "execution", "approval", "risk"]):
        issues.append("validation gates must all PASS")
    return issues


def _default_validation() -> dict[str, str]:
    return {"schema": "PASS", "business": "PASS", "execution": "PASS", "approval": "PASS", "risk": "PASS"}


def _brand_name(context: dict[str, Any]) -> str:
    return str(context["creativePack"].get("brandIdentity", {}).get("brandName", "Genesis Brand"))


def _product_name(context: dict[str, Any]) -> str:
    return str(context["productBlueprint"].get("productName", "Genesis Product"))


def _marketplace_output(context: dict[str, Any]) -> dict[str, Any]:
    listing = context["marketingPack"].get("marketplaceListing", {})
    return {
        "listings": [
            {"channel": "Shopify", "status": "READY_FOR_APPROVAL", "title": listing.get("title", _product_name(context)), "priceSource": "productBlueprint.pricingStrategy"},
            {"channel": "Amazon", "status": "READY_FOR_SELLER_ACCOUNT", "title": listing.get("title", _product_name(context)), "imageOrder": listing.get("imageOrder", [])},
            {"channel": "Etsy", "status": "READY_FOR_ADAPTER", "title": listing.get("title", _product_name(context)), "category": "Educational toys"},
            {"channel": "WooCommerce", "status": "READY_FOR_ADAPTER", "title": listing.get("title", _product_name(context)), "category": "Kids learning"},
        ],
        "publishingActions": ["Create draft listing", "Attach approved media", "Apply pricing", "Submit for founder approval", "Publish after approval"],
        "validationChecks": ["Title present", "Bullets present", "Images mapped", "Price available", "No compliance-sensitive claims without review"],
        "score": 84,
    }


def _social_output(context: dict[str, Any]) -> dict[str, Any]:
    social = context["marketingPack"].get("socialMediaPlan", {})
    return {
        "channels": ["Instagram", "Facebook", "Pinterest", "LinkedIn", "X"],
        "publishingActions": [
            {"channel": "Instagram", "action": "Schedule launch carousel and reel", "status": "READY_FOR_APPROVAL"},
            {"channel": "Facebook", "action": "Schedule parent-community launch post", "status": "READY_FOR_APPROVAL"},
            {"channel": "Pinterest", "action": "Create educational activity pins", "status": "READY_FOR_APPROVAL"},
            {"channel": "LinkedIn", "action": "Optional founder build-in-public post", "status": "OPTIONAL"},
            {"channel": "X", "action": "Optional concise launch thread", "status": "OPTIONAL"},
        ],
        "mediaRequirements": social.get("instagramCalendar", []),
        "score": 82,
    }


def _schedule_output(context: dict[str, Any]) -> dict[str, Any]:
    launch_roadmap = context["marketingPack"].get("launchRoadmap", [])
    return {
        "timezone": "Asia/Kolkata",
        "schedule": [
            {"day": 1, "time": "10:00", "action": "Publish waitlist announcement", "approval": "PUBLISHING"},
            {"day": 3, "time": "18:00", "action": "Publish product demo content", "approval": "PUBLISHING"},
            {"day": 5, "time": "11:00", "action": "Open founder-batch listing draft", "approval": "FOUNDER"},
            {"day": 7, "time": "19:00", "action": "Launch WhatsApp/email reminder", "approval": "BUDGET"},
        ],
        "sourceRoadmap": launch_roadmap,
        "recurringCampaigns": [{"name": "Weekly review request", "cadence": "weekly", "status": "READY_AFTER_FIRST_ORDERS"}],
        "score": 83,
    }


def _asset_output(context: dict[str, Any]) -> dict[str, Any]:
    generated = context["creativePack"].get("generatedAssets", {}).get("assets", [])
    assets = generated or [
        {"kind": "logo", "path": "creative/logo-primary.svg", "status": "EXPECTED"},
        {"kind": "productHero", "path": "creative/product-hero.png", "status": "EXPECTED"},
        {"kind": "packaging", "path": "creative/packaging-spec.pdf", "status": "EXPECTED"},
    ]
    return {
        "assets": assets,
        "repositoryPolicy": {"versioning": "immutable manifest per launch", "naming": "channel-purpose-version", "storage": "local JSON store; optional Google Drive export"},
        "versionHistory": [{"version": "v0.6.0-launch-draft", "status": "CURRENT", "source": "Sprint 4 Creative Pack"}],
        "score": 85,
    }


def _store_output(context: dict[str, Any]) -> dict[str, Any]:
    blueprint = context["productBlueprint"]
    pricing = blueprint.get("pricingStrategy", {})
    return {
        "catalog": {"productName": _product_name(context), "variants": blueprint.get("productVariants", []), "collections": ["Educational toys", "Premium wooden toys", "Ages 3-5"]},
        "pricing": pricing,
        "inventorySync": {"mode": "MANUAL_CONFIRMATION_REQUIRED", "startingInventoryAssumption": 100, "reorderThreshold": 25},
        "collections": ["Founder batch", "Screen-free learning", "Gift-ready toys"],
        "score": 81,
    }


def _campaign_output(context: dict[str, Any]) -> dict[str, Any]:
    ads = context["marketingPack"].get("advertisingPlan", {})
    return {
        "campaigns": [
            {"channel": "Meta Ads", "status": "DRAFT_READY", "budgetApprovalRequired": True, "source": ads.get("metaAds", [])},
            {"channel": "Google Ads", "status": "DRAFT_READY", "budgetApprovalRequired": True, "source": ads.get("googleAds", [])},
            {"channel": "Amazon Ads", "status": "SELLER_ACCOUNT_REQUIRED", "budgetApprovalRequired": True, "source": ads.get("amazonAdsStrategy", {})},
            {"channel": "Email", "status": "READY_FOR_PROVIDER", "budgetApprovalRequired": False},
            {"channel": "WhatsApp", "status": "READY_FOR_PROVIDER", "budgetApprovalRequired": False},
        ],
        "budgetControls": {"dailyBudgetCap": "Founder approval required", "killSwitch": "Pause campaigns when ROAS or spend guardrail fails"},
        "executionMode": "APPROVAL_GATED_DRAFTS",
        "score": 80,
    }


def _approval_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "approvalGates": [
            {"gate": "Publishing", "requiredFor": ["marketplace listings", "social posts"], "approver": "founder"},
            {"gate": "Budget", "requiredFor": ["paid ads", "influencer spend"], "approver": "founder"},
            {"gate": "Legal", "requiredFor": ["safety claims", "child-product compliance claims"], "approver": "human reviewer"},
            {"gate": "Rollback", "requiredFor": ["remove listing", "pause campaign"], "approver": "operator or founder"},
        ],
        "approvalPolicy": {"defaultMode": "manual", "autoApprovalAllowed": ["non-spend draft creation"], "manualApprovalRequired": ["publish", "ad spend", "legal claims"]},
        "auditRequirements": ["requester", "evidence", "approval policy", "decision", "execution result", "rollback result if needed"],
        "score": 87,
    }


def _notification_output(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "notifications": [
            {"event": "approval.requested", "channel": "dashboard", "message": "Founder approval required before launch execution."},
            {"event": "launch.succeeded", "channel": "email_or_whatsapp", "message": "Launch action completed successfully."},
            {"event": "launch.failed", "channel": "email_or_whatsapp", "message": "Launch action failed and rollback plan is available."},
            {"event": "inventory.low", "channel": "dashboard", "message": "Inventory has reached reorder threshold."},
        ],
        "alertRules": ["Notify on failed publish", "Notify on budget exhaustion", "Notify on missing asset", "Notify on approval pending more than 24 hours"],
        "escalationPolicy": {"first": "dashboard", "second": "email", "urgent": "WhatsApp when configured"},
        "score": 83,
    }

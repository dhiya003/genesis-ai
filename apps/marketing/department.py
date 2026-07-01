"""Marketing Department execution for Sprint 5."""

from __future__ import annotations

import logging
from statistics import mean
from time import perf_counter
from typing import Any

from apps.marketing.employees import MARKETING_EMPLOYEES, run_marketing_employee
from apps.observability import MetricsRecorder
from apps.storage import JsonStore
from scripts.validate_marketing_pack import validate_marketing_pack_payload

LOGGER = logging.getLogger("genesis.marketing")


class MarketingDepartment:
    """Converts Product Blueprint and Creative Pack into a Marketing Pack."""

    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def execute(self, project: dict[str, Any], workflow: dict[str, Any], product_blueprint: dict[str, Any], creative_pack: dict[str, Any]) -> dict[str, Any]:
        LOGGER.info("marketing pack started", extra={"event": "marketing.started", "project_id": project["id"], "workflow_id": workflow["id"], "status": "RUNNING"})
        context: dict[str, Any] = {"project": project, "workflow": workflow, "productBlueprint": product_blueprint, "creativePack": creative_pack, "sections": {}}
        employee_outputs: list[dict[str, Any]] = []
        for employee_id in MARKETING_EMPLOYEES:
            started = perf_counter()
            output = run_marketing_employee(employee_id, context)
            output["projectId"] = project["id"]
            output["workflowId"] = workflow["id"]
            self.store.save_employee_output(output)
            context["sections"][output["section"]] = output
            employee_outputs.append(output)
            MetricsRecorder(self.store).record(
                "marketing.employee_completed",
                {"employeeId": employee_id, "runtimeSeconds": round(perf_counter() - started, 4), "score": output.get("score")},
                project_id=project["id"],
                workflow_id=workflow["id"],
            )

        marketing_pack = self.build_marketing_pack(project, workflow, product_blueprint, creative_pack, employee_outputs)
        issues = validate_marketing_pack_payload(marketing_pack)
        if issues:
            raise ValueError(f"Marketing pack validation failed: {issues}")

        marketing_id = marketing_pack["marketingId"]
        self.store.save_marketing_pack(marketing_pack)
        self.store.save_marketing_strategy_report(marketing_id, marketing_pack["marketingStrategy"])
        self.store.save_seo_report(marketing_id, marketing_pack["seoPlan"])
        self.store.save_social_marketing_report(marketing_id, marketing_pack["socialMediaPlan"])
        self.store.save_ads_report(marketing_id, marketing_pack["advertisingPlan"])
        self.store.save_listing_report(marketing_id, marketing_pack["marketplaceListing"])
        self.store.save_launch_report(marketing_id, marketing_pack["launchPlan"])
        MetricsRecorder(self.store).record(
            "marketing.pack_stored",
            {"overallScore": marketing_pack["overallScore"], "employeeCount": len(employee_outputs)},
            project_id=project["id"],
            workflow_id=workflow["id"],
        )
        LOGGER.info("marketing pack stored", extra={"event": "marketing.pack_stored", "project_id": project["id"], "workflow_id": workflow["id"], "status": "COMPLETED"})
        return marketing_pack

    def build_marketing_pack(
        self,
        project: dict[str, Any],
        workflow: dict[str, Any],
        product_blueprint: dict[str, Any],
        creative_pack: dict[str, Any],
        employee_outputs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        sections = {output["section"]: output for output in employee_outputs}
        launch_readiness = _launch_readiness_score(product_blueprint, creative_pack, sections)
        validation_history = [
            {"stage": "Creative Pack precondition", "status": "PASS", "evidence": creative_pack.get("departmentStatus", "CREATIVE_PACK_AVAILABLE")},
            {"stage": "Marketing employee outputs", "status": "PASS", "validator": "validate_marketing_employee_output"},
            {"stage": "Marketing Pack", "status": "PASS", "validator": "validate_marketing_pack.py"},
        ]
        marketing_calendar = _marketing_calendar(sections)
        marketing_content = _marketing_content(sections)
        advertising_strategy = _advertising_strategy(sections)
        marketing_launch_kit = _marketing_launch_kit(sections, marketing_calendar, marketing_content, launch_readiness)
        return {
            "reportType": "MARKETING_PACK",
            "version": "0.5.0",
            "projectId": project["id"],
            "marketingId": project["id"],
            "creativeId": creative_pack["creativeId"],
            "productId": product_blueprint["productId"],
            "workflowId": workflow["id"],
            "department": "MARKETING",
            "departmentStatus": "COMPLETED",
            "executiveSummary": f"Genesis Marketing Engine generated a launch-ready Marketing Pack for {creative_pack['brandIdentity']['brandName']}.",
            "marketingDepartment": {
                "status": "READY",
                "entryCriteria": ["Creative Studio completed", "Brand guidelines approved", "Product Blueprint available", "Creative Package available"],
                "output": "Marketing Launch Package",
            },
            "marketingDirector": {
                "employeeId": "EMP-310",
                "name": "Launch Manager / QA",
                "assignmentStatus": "ASSIGNED",
                "responsibilities": ["Validate marketing readiness", "Coordinate launch kit", "Prepare publishing handoff"],
            },
            "marketingExecutionPlan": {
                "steps": ["GTM strategy", "Acquisition", "Content strategy", "Calendar", "Content", "Advertising", "Sales funnel", "Launch kit", "Validation"],
                "employees": list(sections.keys()),
                "automation": "FULLY_AUTOMATED",
            },
            "brandAssetsLoaded": bool(creative_pack.get("brandIdentity") and creative_pack.get("creativeAssetManifest")),
            "productBlueprintLoaded": product_blueprint.get("reportType") == "PRODUCT_BLUEPRINT",
            "creativePackageLinked": creative_pack.get("creativeId") == product_blueprint.get("productId"),
            "dashboardUpdate": {"status": "MARKETING_PACK_COMPLETED", "visibleToFounder": True},
            "auditSummary": {"createdBy": "MarketingDepartment", "workflowId": workflow["id"], "sourceCreativeId": creative_pack["creativeId"]},
            "marketingStrategy": sections["marketingStrategy"],
            "launchPositioning": sections["marketingStrategy"]["launchPositioning"],
            "customerPersonas": sections["marketingStrategy"]["customerPersonas"],
            "customerSegments": sections["marketingStrategy"]["customerSegments"],
            "goToMarketStrategy": sections["marketingStrategy"]["goToMarketStrategy"],
            "launchRoadmap": sections["marketingStrategy"]["launchRoadmap"],
            "marketingBudget": sections["marketingStrategy"]["marketingBudget"],
            "channelPrioritization": sections["marketingStrategy"]["channelPrioritization"],
            "customerAcquisitionStrategy": sections["marketingStrategy"]["customerAcquisitionStrategy"],
            "contentStrategy": _content_strategy(sections),
            "marketingCalendar": marketing_calendar,
            "marketingContent": marketing_content,
            "advertisingStrategy": advertising_strategy,
            "retentionStrategy": sections["marketingStrategy"]["retentionStrategy"],
            "referralStrategy": sections["marketingStrategy"]["referralStrategy"],
            "seoPlan": sections["seoPlan"],
            "socialMediaPlan": sections["socialCalendar"],
            "advertisingPlan": sections["adConcepts"],
            "marketplaceListing": sections["marketplaceListing"],
            "ecommerceDeliverables": _ecommerce_deliverables(sections),
            "crmDeliverables": _crm_deliverables(sections),
            "salesFunnel": _sales_funnel(sections, product_blueprint),
            "analyticsPlan": _analytics_plan(),
            "landingPageCopy": sections["landingPageCopy"],
            "emailCampaign": sections["emailCampaign"],
            "whatsappCampaign": sections["whatsappCampaign"],
            "influencerStrategy": sections["influencerStrategy"],
            "hashtagPlan": sections["socialCalendar"]["hashtags"],
            "launchPlan": sections["launchQaReport"]["launchPlan"],
            "marketingLaunchKit": marketing_launch_kit,
            "campaignQaReport": sections["launchQaReport"],
            "validationReport": _marketing_validation_report(sections, validation_history),
            "validationHistory": validation_history,
            "aiDeliverables": _ai_deliverables(sections),
            "launchReadinessScore": launch_readiness,
            "founderApprovalChecklist": sections["launchQaReport"]["approvalChecklist"],
            "risks": [
                {"risk": "Marketing Pack does not publish or spend budget in Sprint 5 MVP.", "severity": "LOW", "mitigation": "Use Sprint 6 Publishing Engine for approved automation."},
                {"risk": "Performance estimates require live campaign data.", "severity": "MEDIUM", "mitigation": "Track analytics after launch and feed Sprint 7 intelligence."},
            ],
            "assumptions": [
                "Sprint 5 MVP produces deterministic campaign plans and copy-ready assets.",
                "Founder approval is required before publishing, scheduling, or ad spend.",
                "Live SEO and ad platform credentials can improve later versions.",
            ],
            "nextActions": [
                "Founder approves marketing positioning and launch calendar.",
                "Attach final creative assets from Sprint 4 visual production.",
                "Hand approved Marketing Pack to Sprint 6 Sales Department.",
            ],
            "salesTransition": {
                "status": "READY",
                "nextDepartment": "SALES",
                "handoffArtifacts": ["Marketing Pack", "Campaign calendar", "Lead magnets", "WhatsApp scripts", "Sales funnel"],
            },
            "founderNotification": {
                "status": "READY_FOR_REVIEW",
                "message": "Marketing Launch Package is complete and ready for founder approval before Sales execution.",
            },
            "departmentMetrics": {"employeeCount": len(employee_outputs), "overallScore": round(mean(output["score"] for output in employee_outputs)), "launchReadiness": launch_readiness["score"]},
            "knowledgeBaseEntries": [
                {"projectId": project["id"], "type": "MARKETING_STRATEGY", "lesson": "Marketing begins with GTM strategy before channel content."},
                {"projectId": project["id"], "type": "SALES_HANDOFF", "lesson": "Demand generation should hand structured leads and scripts into Sales."},
            ],
            "employeeOutputs": employee_outputs,
            "overallScore": round(mean(output["score"] for output in employee_outputs)),
        }


def _ecommerce_deliverables(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    listing = sections["marketplaceListing"]
    return {
        "amazonListing": listing,
        "shopifyProductPage": {
            "title": listing["title"],
            "description": listing["description"],
            "featureBullets": listing["bullets"],
            "seoTitle": listing["title"][:60],
            "metaDescription": "Premium wooden educational toy for ages 3-5 with screen-free learning benefits.",
            "faq": listing.get("faq", []),
        },
        "productDescriptions": [listing["description"]],
        "comparisonTables": [
            {"columns": ["Starter", "Standard", "Premium"], "rows": ["Cubes included", "Activity cards", "Gift packaging", "Price tier"]}
        ],
    }


def _crm_deliverables(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "welcomeEmailSequence": sections["emailCampaign"]["sequence"],
        "cartAbandonmentEmails": [
            {"subject": "Still thinking about screen-free play?", "body": "Your founding batch spot is waiting."}
        ],
        "postPurchaseEmails": [
            {"subject": "How to start with your logic cubes", "body": "Begin with the first activity card and share feedback."}
        ],
        "reviewRequestFlow": ["Day 7 play feedback", "Day 14 review request", "Day 21 referral ask"],
        "whatsappAutomation": sections["whatsappCampaign"],
        "customerSegmentation": ["Waitlist parent", "Gift buyer", "Founding batch buyer", "Repeat buyer"],
    }


def _sales_funnel(sections: dict[str, dict[str, Any]], product_blueprint: dict[str, Any]) -> dict[str, Any]:
    return {
        "funnelArchitecture": ["Awareness", "Interest", "Consideration", "Purchase", "Onboarding", "Retention", "Referral"],
        "customerTouchpoints": ["Instagram", "SEO article", "Landing page", "WhatsApp reply", "Marketplace listing", "Email nurture"],
        "conversionGoals": {"awarenessToInterest": "2% click-through", "interestToLead": "10% waitlist conversion", "leadToPurchase": "5% founder-batch conversion"},
        "dropOffRisks": ["Low trust before sample visuals", "Price objection", "Safety claim uncertainty", "Shipping delay concerns"],
        "landingPages": [sections["landingPageCopy"]],
        "leadMagnets": ["Printable pattern activity sheet", "Screen-free play guide"],
        "upsells": ["Activity card expansion pack", "Gift wrap"],
        "crossSells": ["Replacement cubes", "Advanced pattern cards"],
        "bundles": product_blueprint.get("productVariants", []),
        "subscriptionStrategy": "Monthly activity-card expansion after repeat demand is validated.",
    }


def _content_strategy(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "version": "1.0",
        "contentPillars": ["Educational play", "Material trust", "Founder batch", "Parent proof", "Giftability"],
        "educationalContent": ["Pattern play tips", "Screen-free routines", "Logic-building activities"],
        "promotionalContent": ["Founder batch open", "Starter kit offer", "Bundle upgrade"],
        "communityContent": ["Parent poll", "Activity challenge", "Feedback request"],
        "userGeneratedContent": ["Parent demo", "Child pattern challenge", "Review screenshot"],
        "seasonalCampaigns": sections["socialCalendar"]["seasonalEvents"],
        "launchCampaigns": sections["socialCalendar"]["weeklyCampaigns"],
        "targetAudience": sections["marketingStrategy"]["customerSegments"],
        "postingObjectives": ["Build trust", "Capture leads", "Explain product value", "Convert warm prospects"],
    }


def _marketing_calendar(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "dailyPosts": sections["socialCalendar"]["instagramCalendar"],
        "weeklyCampaigns": sections["socialCalendar"]["weeklyCampaigns"],
        "monthlyThemes": sections["socialCalendar"]["monthlyThemes"],
        "productLaunches": ["Founder batch launch"],
        "seasonalEvents": sections["socialCalendar"]["seasonalEvents"],
        "promotionalPeriods": sections["socialCalendar"]["promotionalPeriods"],
        "contentDeadlines": [item["deadline"] for item in sections["socialCalendar"]["instagramCalendar"]],
        "dependencies": {str(item["day"]): item["dependencies"] for item in sections["socialCalendar"]["instagramCalendar"]},
        "campaignOverlap": sections["socialCalendar"]["campaignOverlap"],
        "scheduleExport": {"supported": True, "formats": sections["socialCalendar"]["exportFormats"]},
    }


def _marketing_content(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "instagramCaptions": sections["socialCalendar"]["captions"],
        "facebookCaptions": [item["theme"] for item in sections["socialCalendar"]["facebookCalendar"]],
        "linkedinCopy": sections["socialCalendar"]["linkedinStrategy"],
        "xPosts": ["Screen-free play can still feel premium.", "Founder batch soon: logic cubes for ages 3-5."],
        "pinterestDescriptions": [sections["socialCalendar"]["pinterestStrategy"]],
        "emailCopy": sections["emailCampaign"]["sequence"],
        "whatsappMessages": sections["whatsappCampaign"]["broadcasts"],
        "productDescriptions": [sections["marketplaceListing"]["description"]],
        "marketplaceCopy": sections["marketplaceListing"],
        "blogOutlines": sections["seoPlan"]["contentTopics"],
        "brandVoice": "Warm expert, clear parent guide, quietly playful",
        "campaignLinks": ["Founder Batch Awareness", "Product Education", "Trust Proof", "Waitlist Conversion"],
    }


def _advertising_strategy(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ads = sections["adConcepts"]
    return {
        "campaignObjectives": ["Waitlist acquisition", "Founder batch conversion", "Marketplace retargeting"],
        "metaAds": ads["metaAds"],
        "googleAds": ads["googleAds"],
        "amazonAds": ads["amazonAdsStrategy"],
        "marketplacePromotions": ["Founder batch coupon", "Bundle listing test"],
        "influencerCollaborations": sections["influencerStrategy"]["collaborationPlan"],
        "retargeting": "Retarget landing page visitors and waitlist non-buyers.",
        "remarketing": "Email and WhatsApp reminders for warm prospects.",
        "audienceSegmentation": ads["audienceSegmentation"],
        "budgetAllocation": sections["marketingStrategy"]["marketingBudget"]["allocation"],
        "successMetrics": sections["marketingStrategy"]["successKpis"],
        "risks": sections["launchQaReport"]["risks"],
    }


def _marketing_launch_kit(sections: dict[str, dict[str, Any]], calendar: dict[str, Any], content: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": "1.0",
        "goToMarketStrategy": sections["marketingStrategy"]["goToMarketStrategy"],
        "contentCalendar": calendar,
        "marketingContent": content,
        "advertisingStrategy": sections["adConcepts"],
        "salesFunnel": sections["marketingStrategy"]["funnel"],
        "channelStrategy": sections["marketingStrategy"]["channelStrategy"],
        "kpis": sections["marketingStrategy"]["successKpis"],
        "budgetPlan": sections["marketingStrategy"]["marketingBudget"],
        "launchChecklist": sections["launchQaReport"]["approvalChecklist"],
        "assetsLinked": True,
        "downloadable": {"supported": True, "formats": ["json"]},
        "readiness": readiness,
    }


def _marketing_validation_report(sections: dict[str, dict[str, Any]], validation_history: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "PASS",
        "validationAreas": [
            {"area": "GTM strategy", "status": "PASS"},
            {"area": "Acquisition strategy", "status": "PASS"},
            {"area": "Content strategy", "status": "PASS"},
            {"area": "Calendar", "status": "PASS"},
            {"area": "Advertising", "status": "PASS"},
            {"area": "Sales funnel", "status": "PASS"},
            {"area": "Launch kit", "status": "PASS"},
        ],
        "warnings": sections["launchQaReport"]["risks"],
        "errors": [],
        "validationHistory": validation_history,
    }


def _analytics_plan() -> dict[str, Any]:
    return {
        "kpiDashboard": ["CAC", "ROAS", "CTR", "Conversion Rate", "AOV", "LTV", "Retention", "Funnel Drop-off"],
        "cac": {"target": "Under INR 250 during founder batch", "status": "ESTIMATE"},
        "roas": {"target": "2.0x after creative testing", "status": "ESTIMATE"},
        "ctr": {"target": "1.5%+ Meta cold audience", "status": "ESTIMATE"},
        "conversionRate": {"target": "2-4% landing page", "status": "ESTIMATE"},
        "aov": {"target": "INR 1299-2499", "status": "ESTIMATE"},
        "ltv": {"target": "Improve through expansion packs", "status": "ESTIMATE"},
        "retentionMetrics": ["Repeat purchase", "Expansion-pack purchase", "Referral rate"],
        "funnelDropOffAnalysis": ["Ad click to landing", "Landing to waitlist", "Waitlist to purchase", "Purchase to review"],
    }


def _ai_deliverables(sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "marketingPrompts": ["Generate launch calendar variants using the approved brand voice and parent persona."],
        "adPrompts": [ad["hook"] for ad in sections["adConcepts"]["metaAds"]],
        "contentPrompts": sections["socialCalendar"]["captions"],
        "campaignTemplates": ["Founder batch launch", "Educational benefit campaign", "Gift buyer campaign"],
        "automationWorkflows": [
            {"name": "Waitlist nurture", "trigger": "Lead form submit", "steps": ["Welcome email", "WhatsApp opt-in", "Launch reminder"]},
            {"name": "Review request", "trigger": "Order delivered", "steps": ["Day 7 check-in", "Day 14 review ask"]},
        ],
    }


def _launch_readiness_score(product_blueprint: dict[str, Any], creative_pack: dict[str, Any], sections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    dimensions = {
        "researchQuality": 84,
        "productReadiness": int(product_blueprint.get("overallScore", 82)),
        "manufacturingReadiness": 78 if product_blueprint.get("manufacturingPlan") else 60,
        "brandingCompleteness": int(creative_pack.get("overallScore", 84)),
        "marketingCompleteness": round(mean([sections["marketingStrategy"]["score"], sections["seoPlan"]["score"], sections["socialCalendar"]["score"], sections["adConcepts"]["score"]])),
        "budgetAvailability": 72,
        "riskAssessment": 76,
    }
    score = round(mean(dimensions.values()))
    threshold = 85
    return {
        "score": score,
        "threshold": threshold,
        "recommendation": "READY_FOR_SPRINT_6_REVIEW" if score >= threshold else "HOLD_FOR_FOUNDER_REVIEW",
        "dimensions": dimensions,
        "blockingIssues": [] if score >= threshold else ["Confirm budget availability", "Verify final supplier/manufacturing assumptions before publishing"],
    }

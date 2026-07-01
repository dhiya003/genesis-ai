# Epic 09-10 Marketing And Sales Validation

This document maps the Sprint 5 Marketing Engine and Sprint 6 AI Sales Department stories to implemented Genesis runtime behavior.

## Epic 09 - Marketing Engine

US-00081 through US-00090 are implemented through `MarketingDepartment` and EMP-301 through EMP-310.

- Marketing Department initialization is emitted as `marketingDepartment`.
- Marketing Director assignment is emitted as `marketingDirector`.
- Product Blueprint, Creative Pack, and brand assets are checked through `productBlueprintLoaded`, `creativePackageLinked`, and `brandAssetsLoaded`.
- Go-To-Market strategy is emitted as `goToMarketStrategy`, `customerSegments`, `salesChannels`, `marketingBudget`, and `launchRoadmap`.
- Customer acquisition strategy includes ranked channels, strengths, budget allocation, and customer journey.
- Content strategy is emitted as `contentStrategy`.
- Marketing calendar is emitted as `marketingCalendar` with dependencies, overlap status, and export formats.
- Channel-specific content is emitted as `marketingContent`.
- Advertising strategy is emitted as `advertisingStrategy`.
- Sales funnel includes awareness, interest, consideration, purchase, onboarding, retention, referral, touchpoints, conversion goals, and drop-off risks.
- Marketing Launch Kit is emitted as `marketingLaunchKit`.
- Final completion is emitted through `departmentStatus`, `validationReport`, `salesTransition`, `founderNotification`, `departmentMetrics`, and `knowledgeBaseEntries`.

## Epic 10 - AI Sales Department

US-00091 through US-00100 are implemented through `SalesDepartment` and EMP-401 through EMP-410.

- Sales Department initialization is emitted as `salesDepartment`.
- Sales Director assignment is emitted as `salesDirector`.
- Marketing Package loading and communication channels are emitted as `marketingPackageLoaded` and `communicationChannels`.
- Lead qualification is emitted as `leadQualification` with captured leads, scores, priorities, duplicate detection, CRM update status, and follow-up recommendations.
- Sales conversations are emitted as `salesConversations` with channel playbooks, brand voice, history, escalation rules, and satisfaction feedback placeholders.
- Quotations are emitted as `quotations` with customer details, product details, quantity, unit price, discount, taxes, shipping estimate, total, validity, terms, version history, and export formats.
- Follow-up automation is emitted as `followUpAutomation`.
- CRM synchronization is emitted as `crmSynchronization` with customer records, duplicate detection, preserved history, and access control.
- Sales pipeline management is emitted as `salesPipeline` with configurable stages, opportunities, transition audit, and lost reasons.
- Order confirmation and fulfilment handoff are emitted as `orderHandoff`.
- Sales performance analytics are emitted as `salesAnalytics`.
- Final completion is emitted through `departmentStatus`, `validationReport`, `completionChecklist`, `commercePublishingTransition`, `founderNotification`, `departmentMetrics`, and `knowledgeBaseEntries`.

## Verification

The following checks enforce this story coverage:

- `scripts/validate_marketing_pack.py`
- `scripts/validate_sales_package.py`
- `tests/test_marketing_pack.py`
- `tests/test_sales_department.py`
- `tests/test_api_http_e2e.py`

Live communication, CRM, payment, and fulfilment actions remain credential-dependent. The deterministic MVP produces the complete structured package and approval-gated handoff without sending real messages or creating external orders.

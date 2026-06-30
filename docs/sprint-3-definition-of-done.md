# Sprint 3 Definition of Done - Product Factory

Release: v0.3.0
Status: Authoritative Sprint 3 exit criteria

## Sprint objective

Sprint 3 is complete only when Genesis can transform a validated Research Report into a complete, manufacturable, profitable Product Blueprint without human engineering work.

## Functional DoD

### Product Department

- Product Department exists.
- Product Director orchestrates execution.
- Product workflow is fully automated.
- Workflow integrates with Sprint 2 Research Report.

### Product employees

The following employees must be implemented and executable:

- EMP-101 Product Manager
- EMP-102 Industrial Designer
- EMP-103 Manufacturing Engineer
- EMP-104 Material Engineer
- EMP-105 BOM Engineer
- EMP-106 Cost Engineer
- EMP-107 Packaging Engineer
- EMP-108 Supplier Analyst
- EMP-109 Quality Engineer
- EMP-110 Profitability Analyst

Each employee must have:

- Input schema
- Output schema
- Prompt contract
- Validation
- Logging
- Retry policy
- Timeout
- Metrics

### Product definition

Genesis automatically generates:

- Product Definition Document
- Product features
- Product variants
- Product roadmap
- Customer fit
- Product constraints
- Product success metrics

### Engineering

Genesis determines:

- Product dimensions
- Materials
- Assembly method
- Manufacturing process
- Manufacturing difficulty
- Tooling requirements
- Safety considerations
- Estimated production time

### Manufacturing

Genesis recommends:

- Manufacturing technology
- Manufacturing sequence
- Process flow
- Production assumptions
- Expected yield
- Manufacturing risks

### Material intelligence

Genesis recommends:

- Primary materials
- Alternative materials
- Material comparison
- Cost comparison
- Durability comparison
- Availability assessment

### Bill of Materials

Genesis generates:

- Complete BOM
- Part numbers
- Quantities
- Material mapping
- Estimated costs
- Supplier categories

### Packaging

Genesis generates:

- Packaging specification
- Packaging dimensions
- Packaging materials
- Protection strategy
- Shipping optimization
- Storage optimization
- Sustainability assessment

### Supplier intelligence

Genesis produces:

- Supplier shortlist
- Supplier comparison
- Country
- MOQ
- Lead time
- Risk score
- Alternative suppliers

### Cost engine

Genesis calculates:

- Raw material cost
- Manufacturing cost
- Packaging cost
- Shipping cost
- Marketplace fees
- Taxes
- Landed cost
- Gross margin
- Net margin
- Break-even quantity
- ROI estimate

### Pricing engine

Genesis recommends:

- Manufacturing price
- Wholesale price
- Distributor price
- Retail price
- Marketplace selling price
- Premium pricing option
- Bundle pricing

### Profitability

Genesis calculates:

- Profit per unit
- Profit percentage
- Margin score
- Scalability score
- Inventory risk
- Cash flow impact

### Product validation

Genesis validates:

- Manufacturability
- Profitability
- Shipping feasibility
- Packaging feasibility
- Customer fit
- Market differentiation
- Safety assumptions
- Supplier availability

## Final Product Blueprint

The final Product Blueprint must contain:

- Executive Summary
- Product Definition
- Product Variants
- Engineering Specification
- Material Recommendation
- Manufacturing Plan
- BOM
- Cost Analysis
- Pricing Strategy
- Packaging Specification
- Shipping Plan
- Supplier Recommendations
- Quality Checklist
- Profitability Report
- Risks
- Recommendations
- Next Actions

## Persistence

Genesis must persist:

- Product Blueprint
- BOM
- Cost Report
- Supplier Report
- Packaging Report
- Profitability Report
- Manufacturing Plan

## APIs

Implemented endpoints:

- `POST /products/generate`
- `GET /products/{id}`
- `GET /products/{id}/blueprint`
- `GET /products/{id}/bom`
- `GET /products/{id}/cost`
- `GET /products/{id}/suppliers`
- `GET /products/{id}/profitability`

## Workflow

Genesis executes automatically:

```text
Research Report
  -> Product Department
  -> Employees
  -> Validation
  -> Blueprint
  -> Persistence
  -> API Response
```

No manual orchestration is required.

## Quality gates

Every employee output must pass:

- Schema validation
- Business validation
- Engineering validation
- Confidence scoring
- Risk assessment

## Observability

Genesis tracks:

- Workflow duration
- Employee execution time
- Product generation time
- Cost engine runtime
- Supplier lookup runtime
- API latency
- Error rate

## Testing

All of the following must pass:

- Unit tests
- Employee tests
- BOM tests
- Cost engine tests
- Pricing tests
- Supplier tests
- Packaging tests
- Blueprint validation tests
- Integration tests
- End-to-end tests

## CI/CD

Sprint 3 is not release-closed until:

- GitHub Actions is green.
- Docker build succeeds.
- Fresh clone is reproducible.
- Database migrations pass.
- Seed scripts pass.

## Documentation

Updated documentation must include:

- Engineering Handbook
- Sprint 3 Handbook
- Product Department documentation
- Employee specifications
- API documentation
- Architecture diagrams

## Founder acceptance test

Input:

```text
Build a premium educational wooden toy business for children aged 3-5 in India.
```

Expected outcome:

Genesis automatically produces:

- Validated Product Blueprint
- Product variants: Starter, Standard, Premium
- Manufacturing recommendations
- Complete BOM
- Material recommendations
- Packaging specification
- Supplier shortlist
- Cost and pricing analysis
- Profitability assessment
- Risks and assumptions
- Launch-ready engineering package

## Exit criteria

Sprint 3 is complete only when a founder can submit a validated Research Report and Genesis returns a complete Product Blueprint detailed enough for a manufacturer or supplier to begin implementation discussions without requiring additional product engineering.

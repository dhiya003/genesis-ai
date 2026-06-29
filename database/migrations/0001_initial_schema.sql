-- Genesis AI PostgreSQL Schema
-- Version: 0.1.0
-- Sprint: 1D

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS projects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_code TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','researching','blueprinting','creative_packaging','marketing_packaging','publishing_ready','published','analyzing','archived','failed')),
  priority INTEGER NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ai_employees (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  department TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  authority_level TEXT NOT NULL CHECK (authority_level IN ('recommend','draft','approve','publish')),
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS workflows (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  workflow_type TEXT NOT NULL CHECK (workflow_type IN ('research','product','creative','marketing','publishing','analytics')),
  state TEXT NOT NULL DEFAULT 'queued' CHECK (state IN ('queued','running','needs_review','approved','failed','completed','cancelled')),
  assigned_employee_id TEXT REFERENCES ai_employees(id),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research_reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  generated_by TEXT REFERENCES ai_employees(id),
  title TEXT NOT NULL,
  market_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
  demand_signals JSONB NOT NULL DEFAULT '[]'::jsonb,
  competition JSONB NOT NULL DEFAULT '[]'::jsonb,
  risks JSONB NOT NULL DEFAULT '[]'::jsonb,
  confidence_score NUMERIC(4,2) CHECK (confidence_score >= 0 AND confidence_score <= 100),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS product_blueprints (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  generated_by TEXT REFERENCES ai_employees(id),
  product_name TEXT NOT NULL,
  target_customer JSONB NOT NULL DEFAULT '{}'::jsonb,
  value_proposition TEXT NOT NULL,
  product_specs JSONB NOT NULL DEFAULT '{}'::jsonb,
  pricing JSONB NOT NULL DEFAULT '{}'::jsonb,
  fulfillment JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS creative_packs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  generated_by TEXT REFERENCES ai_employees(id),
  brand_direction JSONB NOT NULL DEFAULT '{}'::jsonb,
  copy_assets JSONB NOT NULL DEFAULT '{}'::jsonb,
  image_prompts JSONB NOT NULL DEFAULT '[]'::jsonb,
  quality_checklist JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS marketing_packs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  generated_by TEXT REFERENCES ai_employees(id),
  channel_plan JSONB NOT NULL DEFAULT '{}'::jsonb,
  content_calendar JSONB NOT NULL DEFAULT '[]'::jsonb,
  ad_hooks JSONB NOT NULL DEFAULT '[]'::jsonb,
  dm_scripts JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS publishing_packages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  generated_by TEXT REFERENCES ai_employees(id),
  destination TEXT NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  publishing_status TEXT NOT NULL DEFAULT 'draft' CHECK (publishing_status IN ('draft','ready','published','failed')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS analytics_reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
  insights JSONB NOT NULL DEFAULT '[]'::jsonb,
  recommendations JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_workflows_project_id ON workflows(project_id);
CREATE INDEX IF NOT EXISTS idx_workflows_state ON workflows(state);
CREATE INDEX IF NOT EXISTS idx_research_reports_project_id ON research_reports(project_id);
CREATE INDEX IF NOT EXISTS idx_product_blueprints_project_id ON product_blueprints(project_id);
CREATE INDEX IF NOT EXISTS idx_creative_packs_project_id ON creative_packs(project_id);
CREATE INDEX IF NOT EXISTS idx_marketing_packs_project_id ON marketing_packs(project_id);
CREATE INDEX IF NOT EXISTS idx_publishing_packages_project_id ON publishing_packages(project_id);
CREATE INDEX IF NOT EXISTS idx_analytics_reports_project_id ON analytics_reports(project_id);

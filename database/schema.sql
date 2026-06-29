-- Genesis AI Physical Database Schema v0.1
-- Target database: PostgreSQL / Supabase

create extension if not exists "pgcrypto";

create table if not exists businesses (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  industry text,
  status text not null default 'DRAFT',
  current_phase text,
  priority text default 'MEDIUM',
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists brands (
  id uuid primary key default gen_random_uuid(),
  business_id uuid not null references businesses(id),
  name text not null,
  mission text,
  target_audience text,
  brand_voice text,
  status text not null default 'DRAFT',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists departments (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null,
  mission text,
  status text not null default 'ACTIVE',
  created_at timestamptz not null default now()
);

create table if not exists employees (
  id uuid primary key default gen_random_uuid(),
  department_id uuid not null references departments(id),
  employee_code text not null unique,
  title text not null,
  mission text,
  authority text,
  status text not null default 'DRAFT',
  prompt_version text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists projects (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id),
  brand_id uuid references brands(id),
  title text not null,
  description text,
  niche text,
  country text default 'India',
  language text default 'en',
  status text not null default 'CREATED',
  priority text default 'MEDIUM',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists workflows (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id),
  workflow_type text not null,
  current_state text not null default 'CREATED',
  retry_count integer not null default 0,
  started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists reports (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references projects(id),
  workflow_id uuid references workflows(id),
  department_id uuid references departments(id),
  employee_id uuid references employees(id),
  report_type text not null,
  version text not null default '1.0',
  status text not null default 'DRAFT',
  confidence numeric(4,3),
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists prompts (
  id uuid primary key default gen_random_uuid(),
  employee_id uuid references employees(id),
  prompt_code text not null unique,
  version text not null,
  status text not null default 'DRAFT',
  content text not null,
  output_schema jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists knowledge_items (
  id uuid primary key default gen_random_uuid(),
  category text not null,
  title text not null,
  summary text,
  content text,
  tags text[] default '{}',
  source text,
  confidence numeric(4,3),
  status text not null default 'DRAFT',
  version text not null default '1.0',
  usage_count integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists products (
  id uuid primary key default gen_random_uuid(),
  brand_id uuid references brands(id),
  project_id uuid references projects(id),
  name text not null,
  category text,
  description text,
  selling_price numeric(10,2),
  estimated_cost numeric(10,2),
  estimated_margin numeric(10,2),
  status text not null default 'DRAFT',
  version text not null default '1.0',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists campaigns (
  id uuid primary key default gen_random_uuid(),
  product_id uuid references products(id),
  platform text not null,
  caption text,
  hashtags text[] default '{}',
  cta text,
  status text not null default 'DRAFT',
  scheduled_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists publishing_jobs (
  id uuid primary key default gen_random_uuid(),
  product_id uuid references products(id),
  provider text not null,
  marketplace text,
  status text not null default 'CREATED',
  error_log text,
  published_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists audit_events (
  id uuid primary key default gen_random_uuid(),
  workflow_id uuid references workflows(id),
  actor_type text not null,
  actor_id text,
  action text not null,
  entity_type text not null,
  entity_id uuid,
  before_state jsonb,
  after_state jsonb,
  reason text,
  created_at timestamptz not null default now()
);

create index if not exists idx_projects_status on projects(status);
create index if not exists idx_reports_project_id on reports(project_id);
create index if not exists idx_reports_type on reports(report_type);
create index if not exists idx_workflows_project_id on workflows(project_id);
create index if not exists idx_knowledge_category on knowledge_items(category);

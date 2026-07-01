-- Genesis v1 Epic 02/03 project and workflow lifecycle support.

create extension if not exists "pgcrypto";

alter table projects add column if not exists target_market text;
alter table projects add column if not exists timeline text;
alter table projects add column if not exists budget_allocation jsonb not null default '{}'::jsonb;
alter table projects add column if not exists preferences jsonb not null default '{}'::jsonb;
alter table projects add column if not exists constraints jsonb not null default '[]'::jsonb;
alter table projects add column if not exists owner text;
alter table projects add column if not exists source_project_id uuid references projects(id);
alter table projects add column if not exists archived_at timestamptz;
alter table projects add column if not exists restored_at timestamptz;

create table if not exists project_versions (
  project_id uuid not null references projects(id),
  version integer not null,
  snapshot jsonb not null default '{}'::jsonb,
  snapshot_reason text,
  snapshot_by text,
  snapshot_at timestamptz not null default now(),
  primary key (project_id, version)
);

create table if not exists project_readiness_reports (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id),
  outcome text not null,
  checks jsonb not null default '[]'::jsonb,
  blocking_errors jsonb not null default '[]'::jsonb,
  warnings jsonb not null default '[]'::jsonb,
  created_by text,
  created_at timestamptz not null default now()
);

create table if not exists project_health_reports (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id),
  health jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table workflows add column if not exists business_id uuid references businesses(id);
alter table workflows add column if not exists workflow_name text;
alter table workflows add column if not exists current_stage text not null default 'NEW';
alter table workflows add column if not exists current_department text;
alter table workflows add column if not exists current_employee text;
alter table workflows add column if not exists priority text not null default 'MEDIUM';
alter table workflows add column if not exists version integer not null default 1;
alter table workflows add column if not exists progress_percent integer not null default 0;
alter table workflows add column if not exists estimated_duration_seconds numeric(12,2);
alter table workflows add column if not exists actual_duration_seconds numeric(12,2);
alter table workflows add column if not exists idempotency_key text;
alter table workflows add column if not exists created_by text;
alter table workflows add column if not exists state_history jsonb not null default '[]'::jsonb;
alter table workflows add column if not exists events_published jsonb not null default '[]'::jsonb;
alter table workflows alter column current_state set default 'NEW';

create unique index if not exists idx_workflows_project_idempotency
  on workflows(project_id, idempotency_key)
  where idempotency_key is not null;

create table if not exists workflow_notifications (
  id uuid primary key default gen_random_uuid(),
  workflow_id uuid not null references workflows(id),
  project_id uuid not null references projects(id),
  business_id uuid references businesses(id),
  notification_type text not null,
  message text not null,
  status text,
  dedupe_key text not null,
  created_at timestamptz not null default now(),
  unique (workflow_id, dedupe_key)
);

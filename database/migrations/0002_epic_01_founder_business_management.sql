-- Migration 0002: Epic 01 founder and business management

create extension if not exists "pgcrypto";

alter table businesses add column if not exists country text;
alter table businesses add column if not exists currency text;
alter table businesses add column if not exists primary_market text;
alter table businesses add column if not exists creator text;
alter table businesses add column if not exists founder_id text;
alter table businesses add column if not exists idempotency_key text;
alter table businesses alter column status set default 'ACTIVE';

create unique index if not exists idx_businesses_founder_idempotency
  on businesses(founder_id, idempotency_key)
  where idempotency_key is not null;

create table if not exists founder_profiles (
  founder_id text primary key,
  version integer not null default 1,
  name text not null,
  language text,
  time_zone text,
  currency text,
  risk_appetite text,
  budget_preference text,
  experience_level text,
  communication_style text,
  working_hours text,
  approval_policy jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists founder_profile_versions (
  founder_id text not null,
  version integer not null,
  snapshot jsonb not null default '{}'::jsonb,
  snapshot_at timestamptz not null default now(),
  primary key (founder_id, version)
);

create table if not exists business_visions (
  id uuid primary key default gen_random_uuid(),
  business_id uuid not null references businesses(id),
  version integer not null,
  content text not null,
  content_format text not null default 'markdown',
  status text not null default 'ACTIVE',
  created_by text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (business_id, version)
);

create table if not exists business_goals (
  id uuid primary key default gen_random_uuid(),
  business_id uuid not null references businesses(id),
  goal_type text not null,
  target_value numeric(14,2) not null,
  unit text,
  target_date date,
  priority text not null default 'MEDIUM',
  status text not null default 'ACTIVE',
  created_by text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists business_constraints (
  id uuid not null,
  business_id uuid not null references businesses(id),
  version integer not null,
  constraint_type text not null,
  description text not null,
  status text not null default 'ACTIVE',
  created_by text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (id, version)
);

create table if not exists business_budgets (
  business_id uuid primary key references businesses(id),
  currency text not null,
  categories jsonb not null default '[]'::jsonb,
  total_allocated numeric(14,2) not null default 0,
  total_spent numeric(14,2) not null default 0,
  remaining_budget numeric(14,2) not null default 0,
  updated_by text,
  updated_at timestamptz not null default now()
);

create table if not exists business_success_metrics (
  id uuid primary key default gen_random_uuid(),
  business_id uuid not null references businesses(id),
  name text not null,
  unit text not null,
  target_value numeric(14,2) not null,
  current_value numeric(14,2) not null default 0,
  time_horizon text not null,
  created_by text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists business_approval_policies (
  business_id uuid primary key references businesses(id),
  rules jsonb not null default '[]'::jsonb,
  approval_history jsonb not null default '[]'::jsonb,
  updated_by text,
  updated_at timestamptz not null default now()
);

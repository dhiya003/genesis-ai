-- Genesis AI Seed Data
-- Version: 0.1.0
-- Sprint: 1D

INSERT INTO ai_employees (id, name, role, department, prompt_version, authority_level) VALUES
('GENESIS-ORCH', 'Genesis Orchestrator', 'Workflow Orchestrator', 'Executive', '0.1.0', 'approve'),
('EMP-001', 'Market Research Analyst', 'Research Report Generator', 'Research', '0.1.0', 'recommend'),
('EMP-002', 'Product Strategist', 'Product Blueprint Generator', 'Product', '0.1.0', 'draft'),
('EMP-003', 'Creative Director', 'Creative Pack Generator', 'Creative', '0.1.0', 'draft'),
('EMP-004', 'Marketing Publisher', 'Marketing and Publishing Pack Generator', 'Marketing', '0.1.0', 'draft')
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  role = EXCLUDED.role,
  department = EXCLUDED.department,
  prompt_version = EXCLUDED.prompt_version,
  authority_level = EXCLUDED.authority_level,
  is_active = true;

INSERT INTO projects (project_code, name, description, status, priority) VALUES
('GEN-SAMPLE-001', 'Sample AI Product Factory Project', 'Reference project fixture for Sprint 1D validation.', 'draft', 2)
ON CONFLICT (project_code) DO NOTHING;

-- Genesis AI seed data: core AI employees

insert into employees (department_id, employee_code, title, mission, authority, status, prompt_version)
select d.id, 'EMP-001', 'Trend Research Specialist', 'Identify whether a niche is growing, stable, seasonal, declining, or too weak for Genesis to pursue.', 'Recommendation only', 'ACTIVE', '0.1.0'
from departments d where d.code = 'RESEARCH'
on conflict (employee_code) do nothing;

insert into employees (department_id, employee_code, title, mission, authority, status, prompt_version)
select d.id, 'EMP-002', 'Competitor Research Specialist', 'Understand competitors before Genesis enters a market.', 'Recommendation only', 'DRAFT', '0.1.0'
from departments d where d.code = 'RESEARCH'
on conflict (employee_code) do nothing;

insert into employees (department_id, employee_code, title, mission, authority, status, prompt_version)
select d.id, 'EMP-003', 'Customer Research Specialist', 'Understand customer behavior, pain points, motivations, and barriers.', 'Recommendation only', 'DRAFT', '0.1.0'
from departments d where d.code = 'RESEARCH'
on conflict (employee_code) do nothing;

insert into employees (department_id, employee_code, title, mission, authority, status, prompt_version)
select d.id, 'EMP-004', 'Product Research Specialist', 'Recommend products with the highest commercial potential.', 'Recommendation only', 'DRAFT', '0.1.0'
from departments d where d.code = 'RESEARCH'
on conflict (employee_code) do nothing;

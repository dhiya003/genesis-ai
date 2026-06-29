-- Genesis AI seed data: departments

insert into departments (code, name, mission, status) values
  ('RESEARCH', 'Research Department', 'Determine whether Genesis should invest resources in a business opportunity.', 'ACTIVE'),
  ('PRODUCT', 'Product Department', 'Transform approved research into commercially viable products.', 'ACTIVE'),
  ('CREATIVE', 'Creative Department', 'Create commercially valuable creative assets and design prompts.', 'ACTIVE'),
  ('MARKETING', 'Marketing Department', 'Prepare products for launch through SEO and social content.', 'ACTIVE'),
  ('PUBLISHING', 'Publishing Department', 'Prepare products and assets for marketplace distribution.', 'ACTIVE'),
  ('ANALYTICS', 'Analytics Department', 'Measure business performance and recommend improvements.', 'ACTIVE')
on conflict (code) do nothing;

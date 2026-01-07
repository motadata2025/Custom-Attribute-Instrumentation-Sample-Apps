-- Insert dummy data into nodejs_user_tbl

INSERT INTO nodejs_user_tbl (username, email, full_name, age, salary, is_active, tags) VALUES
('johndoe', 'john.doe@example.com', 'John Doe', 30, 75000.00, true, ARRAY['developer', 'nodejs', 'backend']),
('janedoe', 'jane.doe@example.com', 'Jane Doe', 28, 82000.50, true, ARRAY['developer', 'frontend', 'react']),
('bobsmith', 'bob.smith@example.com', 'Bob Smith', 35, 95000.00, true, ARRAY['senior', 'architect', 'cloud']),
('alicejohnson', 'alice.johnson@example.com', 'Alice Johnson', 26, 68000.00, true, ARRAY['developer', 'python', 'ml']),
('charlielee', 'charlie.lee@example.com', 'Charlie Lee', 32, 88000.75, true, ARRAY['devops', 'kubernetes', 'docker']),
('dianaross', 'diana.ross@example.com', 'Diana Ross', 29, 72000.00, false, ARRAY['qa', 'automation', 'testing']),
('evanbrown', 'evan.brown@example.com', 'Evan Brown', 41, 110000.00, true, ARRAY['manager', 'team-lead', 'agile']),
('fionagreen', 'fiona.green@example.com', 'Fiona Green', 24, 62000.00, true, ARRAY['junior', 'developer', 'java']),
('georgewilson', 'george.wilson@example.com', 'George Wilson', 38, 98000.50, true, ARRAY['senior', 'security', 'pentesting']),
('hannahwhite', 'hannah.white@example.com', 'Hannah White', 27, 71000.00, true, ARRAY['designer', 'ui', 'ux']),
('ianmartin', 'ian.martin@example.com', 'Ian Martin', 33, 85000.00, false, ARRAY['developer', 'golang', 'microservices']),
('juliaclark', 'julia.clark@example.com', 'Julia Clark', 31, 79000.00, true, ARRAY['developer', 'mobile', 'flutter']),
('kevinmoore', 'kevin.moore@example.com', 'Kevin Moore', 36, 92000.00, true, ARRAY['senior', 'database', 'postgresql']),
('lindataylor', 'linda.taylor@example.com', 'Linda Taylor', 25, 65000.00, true, ARRAY['developer', 'angular', 'typescript']),
('mikeanderson', 'mike.anderson@example.com', 'Mike Anderson', 40, 105000.00, true, ARRAY['architect', 'solutions', 'aws']);

-- Display the inserted data
SELECT COUNT(*) as total_users FROM nodejs_user_tbl;
SELECT * FROM nodejs_user_tbl ORDER BY created_at DESC LIMIT 5;


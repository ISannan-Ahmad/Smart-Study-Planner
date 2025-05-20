-- 1. View: User Study Plans
CREATE VIEW user_study_plans AS
SELECT u.username, sp.id AS plan_id, sp.name AS plan_name, sp.start_time, sp.end_time, sp.updated_at
FROM users u
JOIN study_plans sp ON u.id = sp.user_id;

-- 2. View: Subjects by Study Plan
CREATE VIEW plan_subjects AS
SELECT sp.name AS plan_name, sub.id AS subject_id, sub.name AS subject_name, sub.exam_date
FROM subjects sub
JOIN study_plans sp ON sub.plan_id = sp.id;

-- 3. View: Topics by Subject
CREATE VIEW subject_topics AS
SELECT sub.name AS subject_name, t.name AS topic_name, t.difficulty
FROM topics t
JOIN subjects sub ON t.subject_id = sub.id;

-- 4. View: Scheduled Tasks by Date
CREATE VIEW scheduled_tasks_view AS
SELECT st.scheduled_date, st.title, st.description, sp.name AS plan_name
FROM study_tasks st
JOIN study_plans sp ON st.plan_id = sp.id
ORDER BY st.scheduled_date;

-- 5. View: Completed Study Tasks per User
CREATE VIEW completed_study_tasks AS
SELECT u.username, COUNT(st.id) AS completed_tasks
FROM users u
JOIN study_plans sp ON u.id = sp.user_id
JOIN study_tasks st ON st.plan_id = sp.id
WHERE st.is_done = TRUE
GROUP BY u.username;

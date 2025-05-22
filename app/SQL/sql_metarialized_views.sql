-- 1. View: User Task Progress
CREATE MATERIALIZED VIEW user_task_progress AS
SELECT u.id AS user_id, u.username,
       COUNT(st.id) FILTER (WHERE st.is_done) AS completed,
       COUNT(st.id) AS total_tasks
FROM users u
JOIN study_plans sp ON u.id = sp.user_id
JOIN study_tasks st ON st.plan_id = sp.id
GROUP BY u.id, u.username;

-- 2. View: Task Load Per Day
CREATE MATERIALIZED VIEW daily_task_load AS
SELECT scheduled_date, SUM(duration_minutes) AS total_minutes
FROM study_tasks
GROUP BY scheduled_date;

-- 3. View: Overloaded Days (more than 240 mins)
CREATE MATERIALIZED VIEW overloaded_days AS
SELECT scheduled_date, SUM(duration_minutes) AS total_minutes
FROM study_tasks
GROUP BY scheduled_date
HAVING SUM(duration_minutes) > 240;

-- 4. View: Task Count by Difficulty
CREATE MATERIALIZED VIEW task_count_by_difficulty AS
SELECT t.difficulty, COUNT(st.id) AS task_count
FROM topics t
JOIN subjects sub ON t.subject_id = sub.id
JOIN study_plans sp ON sub.plan_id = sp.id
JOIN study_tasks st ON st.plan_id = sp.id
GROUP BY t.difficulty;

-- 5. View: AI vs Manual Tasks Summary
CREATE MATERIALIZED VIEW task_type_summary AS
SELECT is_ai_generated, COUNT(*) AS task_count
FROM study_tasks
GROUP BY is_ai_generated;

-- 1. Procedure: Mark a Study Task as Complete
CREATE OR REPLACE PROCEDURE mark_study_task_done(task_id INT)
LANGUAGE SQL AS $$
UPDATE study_tasks SET is_done = TRUE WHERE id = task_id;
$$;

-- 2. Procedure: Add a New Subject
CREATE OR REPLACE PROCEDURE add_subject(subject_name TEXT, exam_date DATE, plan_id INT)
LANGUAGE SQL AS $$
INSERT INTO subjects(name, exam_date, plan_id)
VALUES (subject_name, exam_date, plan_id);
$$;

-- 3. Procedure: Delete a Study Plan and Cascade
CREATE OR REPLACE PROCEDURE delete_study_plan(plan_id INT)
LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM study_tasks WHERE plan_id = plan_id;
  DELETE FROM subjects WHERE plan_id = plan_id;
  DELETE FROM study_plans WHERE id = plan_id;
END;
$$;

-- 4. Procedure: Update Task Priority
CREATE OR REPLACE PROCEDURE update_task_priority(task_id INT, new_priority INT)
LANGUAGE SQL AS $$
UPDATE study_tasks SET priority = new_priority WHERE id = task_id;
$$;

-- 5. Procedure: Insert AI-Generated Task
CREATE OR REPLACE PROCEDURE insert_ai_task(
  plan_id INT, task_title TEXT, task_description TEXT,
  duration_minutes INT, scheduled_date DATE
)
LANGUAGE SQL AS $$
INSERT INTO study_tasks (
  plan_id, title, description, duration_minutes, scheduled_date, is_ai_generated
) VALUES (
  plan_id, task_title, task_description, duration_minutes, scheduled_date, TRUE
);
$$;

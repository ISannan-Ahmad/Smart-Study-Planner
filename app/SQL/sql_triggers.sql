-- 1. Trigger: Auto-update timestamp on StudyTask update
ALTER TABLE study_tasks ADD COLUMN updated_at TIMESTAMP;

CREATE OR REPLACE FUNCTION update_study_task_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_study_task_time
BEFORE UPDATE ON study_tasks
FOR EACH ROW
EXECUTE FUNCTION update_study_task_timestamp();

-- 2. Trigger: Prevent deleting user with plans
CREATE OR REPLACE FUNCTION block_user_delete_if_plans()
RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM study_plans WHERE user_id = OLD.id) THEN
    RAISE EXCEPTION 'User has active study plans!';
  END IF;
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_block_user_delete
BEFORE DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION block_user_delete_if_plans();

-- 3. Trigger: Log Completed Task
CREATE TABLE task_completion_log (
  task_id INT,
  completed_at TIMESTAMP
);

CREATE OR REPLACE FUNCTION log_task_completion()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.is_done AND NOT OLD.is_done THEN
    INSERT INTO task_completion_log (task_id, completed_at)
    VALUES (NEW.id, NOW());
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_log_completion
AFTER UPDATE ON study_tasks
FOR EACH ROW
WHEN (NEW.is_done IS TRUE AND OLD.is_done IS FALSE)
EXECUTE FUNCTION log_task_completion();

-- 4. Trigger: Validate Task Duration
CREATE OR REPLACE FUNCTION validate_task_duration()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.duration_minutes <= 0 THEN
    RAISE EXCEPTION 'Duration must be greater than 0';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_task_duration
BEFORE INSERT OR UPDATE ON study_tasks
FOR EACH ROW
EXECUTE FUNCTION validate_task_duration();

-- 5. Trigger: Auto-Create StudyPlan When User Registers
CREATE OR REPLACE FUNCTION auto_create_study_plan()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO study_plans(user_id, name, start_time, end_time)
  VALUES (NEW.id, 'Welcome Plan', '09:00', '12:00');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auto_create_plan
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION auto_create_study_plan();

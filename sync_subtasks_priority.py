from properties import *
from jira_json_utils import *

jira_task_context = JiraTaskContext(jira_host, jira_user, jira_password, jira_project, jira_task_number)

task = read_task(jira_task_context)
print(task)

subtasks = read_subtasks(jira_task_context)
action_ok_count = 0
action_error_count = 0
for subtask in subtasks:
    print(subtask)
    if subtask.priority.id != task.priority.id:
        print('Change priority %s -> %s' % (subtask.priority.name, task.priority.name))

        jira_task_context.jira_task_number = subtask.number
        set_priority(jira_task_context, task.priority.id)

        subtask_after_update = read_task(jira_task_context)
        is_updated = subtask_after_update.priority.id == task.priority.id
        if is_updated:
            action_ok_count += 1
            print('OK')
        else:
            action_error_count += 1
            print('ERROR')
    else:
        print('OK')

print('Total subtasks: %s' % len(subtasks))
print('Changed priority for subtasks: %s' % action_ok_count)
print('Cannot change priority for subtasks: %s' % action_error_count)

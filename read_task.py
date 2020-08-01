from properties import *
from jira_json_utils import *

jira_task_context = JiraTaskContext(jira_host, jira_user, jira_password, jira_project, jira_task_number)

task = read_task(jira_task_context)
print(task)

subtasks = read_subtasks(jira_task_context)
for subtask in subtasks:
    print(subtask)

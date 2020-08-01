import requests
from requests.auth import HTTPBasicAuth
import json
from dataclasses import dataclass

# Methods for extract simple fields from json map

def extract_summary(task_dict):
    return task_dict['fields']['summary']

def extract_type_name(task_dict):
    return task_dict['fields']['issuetype']['name']

def extract_priority_name(task_dict):
    return task_dict['fields']['priority']['name']

def extract_priority_id(task_dict):
    return task_dict['fields']['priority']['id']

def extract_status_key(task_dict):
    return task_dict['fields']['status']['statusCategory']['key']

def extract_components(task_dict):
    return [component['name'] for component in task_dict['fields']['components']]

def extract_created(task_dict):
    return task_dict['fields']['created']

def extract_creator(task_dict):
    return task_dict['fields']['creator']['key']

def extract_assignee(task_dict):
    return task_dict['fields']['assignee']['key']

def extract_task_number(task_dict):
    return str.split(task_dict['key'], '-')[1]

# Methods for extract objects from json map

@dataclass
class Priority:
    name: str
    id: int

def extract_priority(task_dict):
    return Priority(
        name=extract_priority_name(task_dict),
        id=extract_priority_id(task_dict)
    )

@dataclass
class Task:
    number: str = None
    name: str = None
    type_name: str = None
    priority: Priority = None
    status: str = None
    components: list = None
    created: str = None
    creator: str = None
    assignee: str = None

def extract_task(task_dict):
    res = Task()
    res.number = extract_task_number(task_dict)
    res.name = extract_summary(task_dict)
    res.type_name = extract_type_name(task_dict)
    res.priority = extract_priority(task_dict)
    res.status = extract_status_key(task_dict)
    res.components = extract_components(task_dict)
    res.created = extract_created(task_dict)
    res.creator = extract_creator(task_dict)
    res.assignee = extract_assignee(task_dict)
    return res

@dataclass
class Subtask:
    number: str = None
    priority: Priority = None
    status: str = None
    name: str = None

def extract_subtask(subtask_dict):
    res = Subtask()
    res.number = extract_task_number(subtask_dict)
    res.priority = extract_priority(subtask_dict)
    res.status = extract_status_key(subtask_dict)
    res.name = extract_summary(subtask_dict)
    return res

# Methods for reading tasks from rest api

@dataclass
class JiraTaskContext:
    jira_host: str
    jira_user: str
    jira_password: str
    jira_project: str
    jira_task_number: str

def build_auth(jira_task_context):
    return HTTPBasicAuth(
            jira_task_context.jira_user,
            jira_task_context.jira_password
        )

def build_task_url(jira_task_context):
    return 'https://%s/rest/api/latest/issue/%s-%s' % (
        jira_task_context.jira_host,
        jira_task_context.jira_project,
        jira_task_context.jira_task_number
    )

def read_task(jira_task_context):
    response = requests.get(
        build_task_url(jira_task_context),
        auth=build_auth(jira_task_context)
    )
    if(response.status_code != 200):
        print('Cannot read task. Response status code: %s' % response.status_code)
        return None
    return extract_task(response.json())

def read_subtasks(jira_task_context):
    jql = "project = %s AND \"Epic Link\" = %s-%s" % (
        jira_task_context.jira_project,
        jira_task_context.jira_project,
        jira_task_context.jira_task_number
    )
    response = requests.post(
        "https://%s/rest/api/latest/search" % jira_task_context.jira_host,
        data=json.dumps( {
            "jql": jql,
            "fields": [
                "summary",
                "priority",
                "status"
            ]
        } ),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        auth=build_auth(jira_task_context)
    )
    if(response.status_code != 200):
        print('Cannot find subtasks. Response status code: %s' % response.status_code)
        return []
    return [extract_subtask(subtask) for subtask in response.json()['issues']]

# Methods for change tasks by rest api

def set_priority(jira_task_context, new_priority_id):
    requests.put(
        build_task_url(jira_task_context),
        data=json.dumps({
            "fields": {
                "priority": {
                    'id': new_priority_id
                }
            }
        }),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        auth=build_auth(jira_task_context)
    )
from helphub.helphub_core.operators import SearchOp, QueryLogs, Workflow, TerminateOp, ToolCall

class GetTasksLog(SearchOp):
    PROMPT = {"desc": "Confirms the request for get tasks",
              "examples":[
                  ("Get task received for user: 1b492058-2c9b-4593-817d-6b48ac4f1db9", "user_id=1b492058-2c9b-4593-817d-6b48ac4f1db9"),
                  ("Get task received for user: 1b492058-2c9b-4593-817d-6b48ac4f1dtr", "user_id=1b492058-2c9b-4593-817d-6b48ac4f1dtr")
              ]}

    def __init__(self):
        super().__init__()

class GetTasksSuccess(SearchOp):
    PROMPT = {
        "desc": "Confirms the Success of get tasks request",
        "examples": [
            ("Successfully retrieved tasks for user:1b492058-2c9b-4593-817d-6b48ac4f1db9", "get_task_request_status=200"),
            ("Successfully retrieved tasks for user:1b492058-2c9b-4593-817d-6b48ac4f1dtr", "get_task_request_status=200")
        ]
    }
    def __init__(self):
        super().__init__()

class AssignTaskError(SearchOp):
    PROMPT = {
        "desc": "Confirms assign tasks error",
        "examples": [
            ("Error occurred while reassigning task: 1 from user: 1b492058-2c9b-4593-817d-6b48ac4f1db9 to new_user:1b492058-2c9b-4593-817d-6b48ac4f1dtr",
             "task_id=1 from_user_id=1b492058-2c9b-4593-817d-6b48ac4f1db9 new_user_id=1b492058-2c9b-4593-817d-6b48ac4f1dtr"),
            (
            "Error occurred while reassigning task: 45rf2058-2c9b-4593-817d-6b48ac4f1db9 from user: 4ac301ce-46e3-4769-ae2d-afc7b6fac3e1 to new_user:aaa82260-46a4-411a-a9e5-2ad2b84cb609",
            "task_id=45rf2058-2c9b-4593-817d-6b48ac4f1db9 from_user_id=4ac301ce-46e3-4769-ae2d-afc7b6fac3e1 new_user_id=aaa82260-46a4-411a-a9e5-2ad2b84cb609")
        ]
    }
    def __init__(self):
        super().__init__()

class ReassignRequest(SearchOp):
    PROMPT = {
        "desc": "Confirms reassign tasks received",
        "examples": [(
            "Reassign request received for task:1 from user: 4ac301ce-46e3-4769-ae2d-afc7b6fac3e1 to new_user:aaa82260-46a4-411a-a9e5-2ad2b84cb609",
            "task_id=1 from_user_id=4ac301ce-46e3-4769-ae2d-afc7b6fac3e1 new_user_id=aaa82260-46a4-411a-a9e5-2ad2b84cb609"
        ),
            (
                "Reassign request received for task:45rf2058-2c9b-4593-817d-6b48ac4f1db9 from user: 1b492058-2c9b-4593-817d-6b48ac4f1db9 to new_user:a1b492058-2c9b-4593-817d-6b48ac4f1dtr",
                "task_id=45rf2058-2c9b-4593-817d-6b48ac4f1db9 from_user_id=1b492058-2c9b-4593-817d-6b48ac4f1db9 new_user_id=a1b492058-2c9b-4593-817d-6b48ac4f1dtr"
            )
        ]
    }
    def __init__(self):
        super().__init__()

class ReassignTool(ToolCall):
    TOOL_NAME = "reassign_tasks"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

get_tasks_logs = QueryLogs(corr_id="$_helphub_corr_id")
get_tasks_req = GetTasksLog()
get_tasks_success = GetTasksSuccess()
get_tasks_workflow = Workflow(name="GetTasks", description="Workflow for checking get tasks api. This workflow should be used for"
                                                           "analyzing get tasks flow, use this flow if users faces issues with getting tasks")
get_tasks_workflow.set_prompts(prompts=["Facing issues in my task list", "Not able to view my tasks", "My tasks are missing"])
end_get_tasks = TerminateOp(reply="No issues found in tasks fetch")
get_tasks_workflow>>get_tasks_logs>>get_tasks_req>>get_tasks_success>>end_get_tasks

reassign_tasks_workflow = Workflow(name="ReassignTasks",
                                   description="Workflow analyzing reassign tasks api. This workflow should be used"
                                               "for analyzing reassign tasks api, use this flow when user not finding tasks")
reassign_tasks_workflow.set_prompts(prompts=["Not able to view tasks reassigned to me", "new tasks are missing", "Assigned tasks are missing"])
get_reassign_api_logs = QueryLogs(query="Reassign request received for task:(.*) from user: (.*) to new_user:$_helphub_sub")
reassign_tasks_req = ReassignRequest()
get_reassign_tasks_logs = QueryLogs(query="Error occurred while reassigning task: $task_id from user: $from_user_id to new_user:$new_user_id")
assign_tasks_error = AssignTaskError()
reassign_tool = ReassignTool(task_id="$task_id", from_user_id="$from_user_id", new_user_id="$new_user_id")
end_reassign_tasks = TerminateOp(reply="We have fixed the issues please try again")
reassign_tasks_workflow>>get_reassign_api_logs>>reassign_tasks_req>>get_reassign_tasks_logs>>assign_tasks_error>>reassign_tool>>end_reassign_tasks


from pydantic import BaseModel
from enum import Enum
from typing import Optional, List


# Example of evidence model
# class Evidence:
#     name: str
#     display_name: str # <domain>\<hostname>
#     uid: str
#     tasks: List[str]
#     os: str
#     os_version: str
#     ips: List[str]

# class TaskStatus(Enum):
#     ENQUEUED = "Enqueued"
#     RUNNING = "Running"
#     CRASHED = "Crashed"
#     COMPLETED = "Completed"
#
#
# class FunctionProcessingTask(BaseModel):
#     case_prefix: str
#     target_path: str
#     function: str
#
#
# class TaskSubmitResult(BaseModel):
#     evidence_uid: str
#     error: Optional[str]
#     task_id: Optional[str]
#
#
# class FunctionResult(BaseModel):
#     evidence_uid: str
#     target_path: str
#     function: str
#     records_count: int
#     error: Optional[str]
#
#
# class TaskResult(BaseModel):
#     task_id: Optional[str]
#     status: TaskStatus
#     crash_info: Optional[str]
#     executed_in: float
#     function_result: Optional[FunctionResult]

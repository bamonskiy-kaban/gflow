from contextlib import asynccontextmanager

from fastapi import FastAPI
from dissect.target.target import Target

from broker import broker
from config import (
    EVENT_BROKER_HOST,
    EVENT_BROKER_PORT,
    API_TARGETS_DIR,
)

from tasks import process_function
from elk import create_index
# from models import (
#     FunctionProcessingTask,
#     TaskStatus,
#     TaskResult,
#     TaskSubmitResult,
#     FunctionResult
# )

import uuid


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    if not broker.is_worker_process:
        await broker.startup()
    yield
    if not broker.is_worker_process:
        await broker.shutdown()


app = FastAPI(lifespan=lifespan)


@app.post("/evidence")
async def create_evidence(prefix: str):
    pass


@app.get("/evidence/{evidence_uid}")
async def get_evidence():
    pass


@app.patch("/evidence/{evidence_uid}")
async def update_evidence():
    pass


@app.delete("/evidence/{evidence_uid}")
async def delete_evidence():
    pass


@app.post("/task")
async def create_task():
    pass


@app.get("/task/{task_id}")
async def get_task():
    pass

#
#
# @app.get("/cases")
# async def list_cases():
#     pass
#
#
# @app.post("/case")
# async def create_case():
#     pass
#
#
# @app.get("/case/{case_id}")
# async def get_case():
#     pass
#
#
# @app.post("/evidence")
# async def create_evidence():
#     pass
#
#
# @app.get("/evidence/{evidence_id}")
# async def get_evidence():
#     pass
#
#
# @app.post("/tasks", response_model=TaskSubmitResult)
# async def create_evidence_processing_task(task: FunctionProcessingTask):
#     evidence_id = f"{task.case_prefix}-{uuid.uuid4().hex}"
#     try:
#         await create_index(evidence_id)
#     except Exception as e:
#         return TaskSubmitResult(
#             evidence_uid=evidence_id,
#             task_id=None,
#             error=str(e)
#         )
#
#     task = await process_function.kiq(evidence_id, task.target_path, task.function, EVENT_BROKER_HOST,
#                                       EVENT_BROKER_PORT)
#     return TaskSubmitResult(
#         task_id=task.task_id,
#         evidence_uid=evidence_id,
#         error=None
#     )
#
#
# # TODO: add logs to task results
# @app.get("/tasks/{task_id}", response_model=TaskResult)
# async def get_task_results(task_id: str):
#     is_ready = await broker.result_backend.is_result_ready(task_id)
#
#     if not is_ready:
#         return TaskResult(
#             task_id=task_id,
#             status=TaskStatus.RUNNING,
#             crash_info=None,
#             executed_in=0,
#             function_result=None
#         )
#
#     task_result = await broker.result_backend.get_result(task_id, with_logs=True)
#     return TaskResult(
#         task_id=task_id,
#         status=TaskStatus.COMPLETED if not task_result.is_err else TaskStatus.CRASHED,
#         crash_info=str(task_result.error) if task_result.is_err else None,
#         executed_in=task_result.execution_time,
#         function_result=FunctionResult(
#             evidence_uid=task_result.return_value.get("evidence_uid"),
#             target_path=task_result.return_value.get("evidence_path"),
#             function=task_result.return_value.get("function_name"),
#             records_count=task_result.return_value.get("records"),
#             error=task_result.return_value.get("error")
#         )
#     )

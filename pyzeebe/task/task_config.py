import logging
from typing import List, Optional

from pyzeebe.errors import NoVariableNameGivenError
from pyzeebe.job.job import Job
from pyzeebe.task.exception_handler import ExceptionHandler
from pyzeebe.task.types import TaskDecorator

logger = logging.getLogger(__name__)


def default_exception_handler(e: Exception, job: Job) -> None:
    logger.warning(f"Task type: {job.type} - failed job {job}. Error: {e}.")
    job.set_failure_status(f"Failed job. Error: {e}")


class TaskConfig:
    def __init__(self, type: str, exception_handler: ExceptionHandler = default_exception_handler,
                 timeout_ms: int = 10000, max_jobs_to_activate: int = 32,
                 variables_to_fetch: Optional[List[str]] = None,
                 single_value: bool = False, variable_name: Optional[str] = None, before: List[TaskDecorator] = None,
                 after: List[TaskDecorator] = None):
        if single_value and not variable_name:
            raise NoVariableNameGivenError(type)

        self.type = type
        self.exception_handler = exception_handler
        self.timeout_ms = timeout_ms
        self.max_jobs_to_activate = max_jobs_to_activate
        self.variables_to_fetch = variables_to_fetch
        self.single_value = single_value
        self.variable_name = variable_name
        self.before = before or []
        self.after = after or []

    def __repr__(self):
        return f"TaskConfig(type={self.type}, exception_handler={self.exception_handler}, " \
               f"timeout_ms={self.timeout_ms}, max_jobs_to_activate={self.max_jobs_to_activate}, " \
               f"variables_to_fetch={self.variables_to_fetch}, single_value={self.single_value}, " \
               f"variable_name={self.variable_name}, before={self.before}, after={self.after})"
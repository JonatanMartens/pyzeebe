import asyncio
import functools
import inspect
import logging
from typing import Awaitable, Callable, Dict, List, Tuple

from pyzeebe import Job, TaskDecorator
from pyzeebe.task.task import Task
from pyzeebe.task.task_config import TaskConfig
from pyzeebe.task.types import DecoratorRunner, JobHandler

logger = logging.getLogger(__name__)


def build_task(task_function: Callable, task_config: TaskConfig) -> Task:
    return Task(task_function, build_job_handler(task_function, task_config), task_config)


def build_job_handler(task_function: Callable, task_config: TaskConfig) -> JobHandler:
    prepared_task_function = prepare_task_function(task_function, task_config)

    before_decorator_runner = create_decorator_runner(task_config.before)
    after_decorator_runner = create_decorator_runner(task_config.after)

    @functools.wraps(task_function)
    async def job_handler(job: Job) -> Job:
        job = await before_decorator_runner(job)
        job.variables, succeeded = await run_original_task_function(
            prepared_task_function, task_config, job
        )
        job = await after_decorator_runner(job)
        if succeeded:
            await job.set_success_status()
        return job

    return job_handler


def prepare_task_function(task_function: Callable, task_config: TaskConfig) -> Callable[..., Awaitable[Dict]]:
    if not inspect.iscoroutinefunction(task_function):
        task_function = asyncify(task_function)

    if task_config.single_value:
        task_function = convert_to_dict_function(
            task_function, task_config.variable_name
        )
    return task_function


async def run_original_task_function(task_function: Callable, task_config: TaskConfig, job: Job) -> Tuple[Dict, bool]:
    try:
        return await task_function(**job.variables), True
    except Exception as e:
        logger.debug(f"Failed job: {job}. Error: {e}.")
        await task_config.exception_handler(e, job)
        return job.variables, False


def create_decorator_runner(decorators: List[TaskDecorator]) -> DecoratorRunner:
    async def decorator_runner(job: Job):
        for decorator in decorators:
            job = run_decorator(decorator, job)
        return job

    return decorator_runner


def run_decorator(decorator: TaskDecorator, job: Job) -> Job:
    try:
        return decorator(job)
    except Exception as e:
        logger.warning(f"Failed to run decorator {decorator}. Exception: {e}")
        return job


def convert_to_dict_function(single_value_function: Callable, variable_name: str) -> Callable[..., Dict]:
    async def inner_fn(*args, **kwargs):
        return {variable_name: await single_value_function(*args, **kwargs)}

    return inner_fn


def get_parameters_from_function(task_function: Callable) -> List[str]:
    function_signature = inspect.signature(task_function)
    for _, parameter in function_signature.parameters.items():
        if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            return []
    return list(function_signature.parameters)


def asyncify(task_function: Callable) -> Callable[..., Awaitable]:
    @ functools.wraps(task_function)
    async def async_function(**kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, functools.partial(task_function, **kwargs))
    return async_function

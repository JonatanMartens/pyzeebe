import asyncio
from typing import Dict

from pyzeebe import CamundaCloudCredentials, Job, ZeebeWorker


# Use decorators to add functionality before and after tasks. These will not fail the task
async def example_logging_task_decorator(job: Job) -> Job:
    print(job)
    return job


# Will use environment variable ZEEBE_ADDRESS or localhost:26500 and NOT use TLS
worker = ZeebeWorker()

# Will use environment variable ZEEBE_ADDRESS or localhost:26500 and use TLS
worker = ZeebeWorker(secure_connection=True)

# Connect to zeebe cluster in camunda cloud
camunda_cloud_credentials = CamundaCloudCredentials(client_id="<my_client_id>", client_secret="<my_client_secret>",
                                                    cluster_id="<my_cluster_id>")
worker = ZeebeWorker(credentials=camunda_cloud_credentials)

# Decorators allow us to add functionality before and after each job
worker.before(example_logging_task_decorator)
worker.after(example_logging_task_decorator)


# Create a task like this:
@worker.task(task_type="test")
def example_task() -> Dict:
    return {"output": f"Hello world, test!"}

# Or like this:
@worker.task(task_type="test2")
async def second_example_task() -> Dict:
    return {"output": f"Hello world, test2!"}

# Create a task that will return a single value (not a dict) like this:
# This task will return to zeebe: { y: x + 1 }
@worker.task(task_type="add_one", single_value=True, variable_name="y")
async def add_one(x: int) -> int:
    return x + 1


# Define a custom exception_handler for a task like so:
async def example_exception_handler(exception: Exception, job: Job) -> None:
    print(exception)
    print(job)
    await job.set_failure_status(
        f"Failed to run task {job.type}. Reason: {exception}"
    )


@worker.task(task_type="exception_task", exception_handler=example_exception_handler)
async def exception_task():
    raise Exception("Oh no!")


# We can also add decorators to tasks.
# The order of the decorators will be as follows:
# Worker decorators -> Task decorators -> Task -> Task decorators -> Worker decorators
# Here is how:
@worker.task(task_type="decorator_task", before=[example_logging_task_decorator],
             after=[example_logging_task_decorator])
async def decorator_task() -> Dict:
    return {"output": "Hello world, test!"}


if __name__ == "__main__":
    asyncio.run(worker.work())

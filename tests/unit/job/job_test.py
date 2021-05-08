from unittest.mock import patch
from uuid import uuid4

import pytest

from pyzeebe.errors import NoZeebeAdapterError


def test_success(job_with_adapter):
    with patch("pyzeebe.grpc_internals.zeebe_adapter.ZeebeAdapter.complete_job") as complete_job_mock:
        job_with_adapter.set_success_status()
        complete_job_mock.assert_called_with(job_key=job_with_adapter.key, variables=job_with_adapter.variables)


def test_success_no_zeebe_adapter(job_without_adapter):
    with pytest.raises(NoZeebeAdapterError):
        job_without_adapter.set_success_status()


def test_error(job_with_adapter):
    with patch("pyzeebe.grpc_internals.zeebe_adapter.ZeebeAdapter.throw_error") as throw_error_mock:
        message = str(uuid4())
        job_with_adapter.set_error_status(message)
        throw_error_mock.assert_called_with(job_key=job_with_adapter.key, message=message, error_code="")


def test_error_with_code(job_with_adapter):
    with patch("pyzeebe.grpc_internals.zeebe_adapter.ZeebeAdapter.throw_error") as throw_error_mock:
        message = str(uuid4())
        error_code = "custom-error-code"
        job_with_adapter.set_error_status(message, error_code)
        throw_error_mock.assert_called_with(job_key=job_with_adapter.key, message=message, error_code=error_code)


def test_error_no_zeebe_adapter(job_without_adapter):
    with pytest.raises(NoZeebeAdapterError):
        message = str(uuid4())
        job_without_adapter.set_error_status(message)


def test_failure(job_with_adapter):
    with patch("pyzeebe.grpc_internals.zeebe_adapter.ZeebeAdapter.fail_job") as fail_job_mock:
        message = str(uuid4())
        job_with_adapter.set_failure_status(message)
        fail_job_mock.assert_called_with(job_key=job_with_adapter.key, retries=job_with_adapter.retries-1, message=message)


def test_failure_no_zeebe_adapter(job_without_adapter):
    with pytest.raises(NoZeebeAdapterError):
        message = str(uuid4())
        job_without_adapter.set_failure_status(message)

Welcome to pyzeebe's documentation!
===================================
Python client for Zeebe workflow engine

Current version is |version|.


Library installation
====================

.. code-block:: bash

   $ pip install pyzeebe

Getting Started
===============

Creating a worker

.. code-block:: python

   from pyzeebe import ZeebeWorker

   worker = ZeebeWorker()

   @worker.task(task_type="my_task")
   async def my_task(x: int):
      return {"y": x + 1}

   await worker.work()

Creating a client

.. code-block:: python

   from pyzeebe import ZeebeClient

   client = ZeebeClient()

   await client.run_process("my_process")

   # Run process with variables:
   await client.run_process("my_process", variables={"x": 0})


Dependencies
============

* python 3.6+
* zeebe-grpc
* grpcio
* protobuf
* oauthlib
* requests-oauthlib


Table Of Contents
=================
.. toctree::
   :maxdepth: 2

    Client <client>
    Worker <worker>
    Decorators <decorators>
    Exceptions <exceptions>

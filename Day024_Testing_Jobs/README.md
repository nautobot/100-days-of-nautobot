# Testing for Jobs

Welcome to Day 24! In today's challenge, we will introduce an important step: testing our code automatically. 

If you have experience in software development, you might already notice so far in our days, we have not been writing code to test our code that is often a necessary step in software development. 

Testing is important for several reasons: 

1. When you are writing new code, you need to validate the new code is working as expected. 
2. When you implement new code, you need to make sure the new code did not break any existing code or affect the expected behavior. 

## Testing in Nautobot Jobs

Testing is an important topic and many full size books have been written about it. We will revisit the topic in later days and just introduce the concept in today's challenge. 

Since Nautobot is built from the Django framework, Nautobot Jobs can be tested via [Django unit-test](https://docs.djangoproject.com/en/5.1/topics/testing/) features. 

However, there are some useful features specific to testing Jobs as explained in the [Testing Jobs](https://docs.nautobot.com/projects/core/en/stable/development/jobs/#testing-jobs) document.   

Let's set up the environment first. 

## Environment Setup

The environment setup will be the same as [Lab Setup Scenario 1](../Lab_Setup/scenario_1_setup/README.md), below is a summary of the steps, please consult the guide for a detailed background if needed. 

If you stopped the Codespace environment, simply restart it and use the following steps to start Naudotbot, you do not need to rebuild docker instances, nor import the database again: 

```
$ cd nautobot-docker-compose/
$ poetry shell
$ invoke debug
```

If you need to completely rebuild the environment in Codespace, here are the steps: 

```
$ cd nautobot-docker-compose/
$ poetry shell
$ invoke build
$ invoke db-import
$ invoke debug
```

We do not need to use Containerlab for today's challenge. 

## File Creation

By now, I am sure creating a Job file is second nature to you. Here is a summary of how to attach to the nautobot docker instance and create a file under `Jobs` root:

```
$ docker exec -u root -it nautobot_docker_compose-nautobot-1 bash
root@c9e0fa2a45a0:/opt/nautobot# cd jobs
root@c9e0fa2a45a0:/opt/nautobot/jobs# pwd
/opt/nautobot/jobs
root@c9e0fa2a45a0:/opt/nautobot/jobs# touch job_hook_test.py
root@c9e0fa2a45a0:/opt/nautobot/jobs# chown nautobot:nautobot ob_hook_test.py
```

The environment is now setup for today's challenge.  

## Execute Existing Test

There are many software tests written to test Nautobot features. For example, [test_authentication.py](https://github.com/nautobot/nautobot/blob/develop/nautobot/core/tests/test_authentication.py) in the Nautobot code base is used to test external authentication. 

We can execute the test written in that file. The first step is to ssh to the nautobot docker instance: 

```
(nautobot-docker-compose-py3.10) @ericchou1 ➜ ~/nautobot-docker-compose (main) $ docker exec -u root -it nautobot_docker_compose-nautobot-1 bash
root@8d0ac3752031:/opt/nautobot#
```

Then we can change to the `jobs` directory and execute the test: 

> [!TIP]
> The test might take a bit of time as it needs to create a separate test database table. 

```
root@8d0ac3752031:/opt/nautobot# cd jobs/
root@8d0ac3752031:/opt/nautobot/jobs# nautobot-server test nautobot.core.tests.test_authentication.ExternalAuthenticationTestCase
Using NautobotPerformanceTestRunner to run tests ...
Found 10 test(s).
Creating test database for alias 'default'...

    Checking for duplicate records ...

    Checking for duplicate records ...

    Checking for duplicate records ...

    Checking for duplicate records ...

>>> Finding and removing any invalid or dangling Note objects ...

>>> Removal completed. 


System check identified no issues (0 silenced).
..........
----------------------------------------------------------------------
Ran 10 tests in 0.918s

OK
Destroying test database for alias 'default'...
root@eba3a1d8b6ab:/opt/nautobot/jobs# 
```

We can follow the same pattern and test our previously created Jobs. 

## Test Current Job

Assuming we have the following `hello_job.py` file under our JOBS root: 

```
from nautobot.apps.jobs import Job, register_jobs, ObjectVar, StringVar, IntegerVar, FileVar
from nautobot.dcim.models.locations import Location
from nautobot.dcim.models.devices import Device
import requests


name = "Hello World Nautobot Jobs"

class HelloWorld(Job):

    class Meta:
        name = "Hello World"
        description = "Hello World for first Nautobot Jobs"

    def run(self):
        self.logger.debug("Hello, this is my first Nautobot Job.")


register_jobs(
    HelloWorld,
)
```

We can write a test to test the log message. The first step is to create a `tests` folder under `nautobot`: 

```
root@ee2753f052ae:/opt/nautobot/jobs# mkdir /opt/nautobot/tests
root@ee2753f052ae:/opt/nautobot/jobs# touch /opt/nautobot/tests/__init__.py
root@ee2753f052ae:/opt/nautobot/jobs# touch /opt/nautobot/tests/TestJobs_1.py
```

We will also specify the `JOBS_ROOT` environment variable: 

```
root@ee2753f052ae:/opt/nautobot/jobs# export JOBS_ROOT="/opt/nautobot/jobs"
```

We will use the following code in the `TestJobs_1.py` file:

> [!TIP]
> This example is taken from [Testing Jobs](https://docs.nautobot.com/projects/core/en/stable/development/jobs/#testing-jobs). If interested, please take a look at the documentation for more explanation. 

```python 
from nautobot.apps.testing import run_job_for_testing, TransactionTestCase
from nautobot.extras.models import Job, JobLogEntry


class MyJobTestCase(TransactionTestCase):
    def test_my_job(self):
        # Testing of Job "HelloWorld" in file "hello_job.py" in $JOBS_ROOT
        # job = Job.objects.get(job_class_name="HelloWorld", module_name="hello_job", source="local")
        job = Job.objects.get(job_class_name="HelloWorld", module_name="hello_job")

        # or, job = Job.objects.get_for_class_path("local/my_job_file/MyJob")
        job_result = run_job_for_testing(job)

        # Inspect the logs created by running the job
        log_entries = JobLogEntry.objects.filter(job_result=job_result)
        for log_entry in log_entries:
            self.assertEqual(log_entry.message, "Hello, this is my first Nautobot Job.")
```

The test can be run the same way: 

```
root@ee2753f052ae:/opt/nautobot/tests# nautobot-server test TestJobs_1
Using NautobotPerformanceTestRunner to run tests ...
Found 1 test(s).
Creating test database for alias 'default'...
...
...
System check identified no issues (0 silenced).

F
======================================================================
FAIL: test_my_job (TestJobs_1.MyJobTestCase)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/opt/nautobot/tests/TestJobs_1.py", line 17, in test_my_job
    self.assertEqual(log_entry.message, "Hello, this is my first Nautobot Job.")
AssertionError: 'Running job' != 'Hello, this is my first Nautobot Job.'
- Running job
+ Hello, this is my first Nautobot Job.


----------------------------------------------------------------------
Ran 1 test in 2.593s

FAILED (failures=1)
Destroying test database for alias 'default'...
```

There is a `AssertionError` at the end, but that is ok at this point. It is more important to see a customized test running at this point. 

Writing tests can sometimes feel like 'extra' work as they do not implement new features, but they are invaluable tools to ensure we detect breaking code quickly and help us sleep at night. 

## Day 24 To Do

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/). 

Go ahead and post a screenshot of the successful execution of the new job on a social media of your choice, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress! 

In tomorrow's challenge, we will learn more about the nautobot CLI tool `nautobot-server`. See you tomorrow! 

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+24+of+the+100+days+of+nautobot+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 24 of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot)

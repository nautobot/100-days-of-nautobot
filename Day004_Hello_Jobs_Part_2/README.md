# Hello Jobs - Part 2: Customization and Features

In today's challenge, we will continue to work on the ```hello_jobs.py``` from [Day 3](https://github.com/networktocode-llc/100-days-of-nautobot-challenge/blob/main/Day003_Hello_Jobs_Part_1/README.md).

Let's navigate to [https://github.com/codespaces/](https://github.com/codespaces/) and restart the codespace instance.

![rebuild_codespace_1.png](../Lab_Setup/lab_related_notes/images/rebuild_codespace_1.png)

Due to what seems to be a bug, the Docker daemon does not start automatically when Codespace is restarted. To resolve this issue, we need to rebuild the Codespace.

```
@ericchou1 ➜ ~ $ docker ps
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```

## (Note) Rebuild Codespace

Since this is the first two-day series where we recommend stopping Codespace at the end of first day then restarting the same instance the next day, let's spend a few minutes on the issue regarding rebuilds. For future days, we will just make a note of it (as well as mention it in [Lab Notes](../Lab_Setup/lab_related_notes/README.md)) but not spend as much time on the details. Be sure to bookmark the Lab Notes!

Click on the settings reel icon on the lower left corner and choose "Command Palette":

![codespace_rebuild_1](images/codespace_rebuild_1.png)

In the command palette, type in "Codespace: Rebuild Container" and choose the option to rebuild. Confirm on the next page.

![codespace_rebuild_2](images/codespace_rebuild_2.png)

Once Codespace is working again, use the terminal window to start Nautobot as we did in Day 3.

## Jobs Meta Class

If we take a closer look at the Job we created, you'll notice that there is no description, and the section grouping name is 'Hello_jobs' with an underscore. If we compare this with other existing System Jobs, we can see that the System Jobs have both descriptions and spaces between the job names:

![jobs_meta_1](images/jobs_meta_1.png)

How do we change that? Let's refer to the Metadata Attributes section of the [Nautobot Jobs Developer Guide](https://docs.nautobot.com/projects/core/en/stable/development/jobs/#module-metadata-attributes). 

From the documentation, we can see that we can customize the grouping name using a global constant of ```name```, as well as defining the job-specific name using the ```meta``` class. Let's make the following change: 

```python
from nautobot.apps.jobs import Job, register_jobs

# new
name = "Hello World Nautobot Jobs"

class HelloJobs(Job):

    # new
    class Meta:
        name = "Hello Jobs"
        description = "Hello World for first Nautobot Jobs"

    def run(self):
        self.logger.debug("Hello, this is my first Nautobot Job.")
    
    
register_jobs(
    HelloJobs,
)
```

> [!IMPORTANT]
> Register jobs is an important step that many people, myself included, might miss when first introduced to Nautobot jobs. Don't forget that line at the end.  

After saving the changes, nothing happens on the UI. What could be the issue?

Remember, we need to do an ```invoke post-upgrade``` for the changes to take effect:

```
@ericchou1 ➜ ~ $ cd nautobot-docker-compose/
@ericchou1 ➜ ~/nautobot-docker-compose (main) $ poetry shell
(nautobot-docker-compose-py3.10) @ericchou1 ➜ ~/nautobot-docker-compose (main) $ invoke post-upgrade
```

We can now see that the changes have been applied when we navigate back to the Nautobot Jobs UI:

![jobs_meta_2](images/jobs_meta_2.png)

Let's see how we can add more logging to the job in the next section.

## Add more Logging

In Day 3, we saw how we can log our progress with ```self.logger.debug("Hello, this is my first Nautobot Job.")``` in the code. What if we want to log more data with different severity levels?

Again, the [Nautobot Jobs Developer Guide](https://docs.nautobot.com/projects/core/en/stable/development/jobs/#logging) is our friend here. Under logging, we can just as easily do that using logger objects.

Let's create a second job in the same file with more logging:

```python
class HelloJobsWithLogs(Job):

    class Meta:
        name = "Hello Jobs with Logs"
        description = "Hello Jobs with different log types"

    def run(self):
        self.logger.info("This is an info type log.")
        self.logger.debug("This is a debug type log.")
        self.logger.warning("This is a warning type log.")
        self.logger.error("This is an error type log.")
        self.logger.critical("This is a critical type log.")
```

Don't forget to register the new job:

```python
register_jobs(
    HelloJobs,
    HelloJobsWithLogs,
)
```

This is how the file should look at this point:

```python
from nautobot.apps.jobs import Job, register_jobs

name = "Hello World Nautobot Jobs"

class HelloJobs(Job):

    class Meta:
        name = "Hello Jobs"
        description = "Hello World for first Nautobot Jobs"

    def run(self):
        self.logger.debug("Hello, this is my first Nautobot Job.")

class HelloJobsWithLogs(Job):

    class Meta:
        name = "Hello Jobs with Logs"
        description = "Hello Jobs with different log types"

    def run(self):
        self.logger.info("This is an info type log.")
        self.logger.debug("This is a debug type log.")
        self.logger.warning("This is a warning type log.")
        self.logger.error("This is an error type log.")
        self.logger.critical("This is a critical type log.")
       

register_jobs(
    HelloJobs,
    HelloJobsWithLogs,
)
```

After performing a ```post_upgrade```, we will see the new job appear under the same group:

![jobs_logging_2](images/jobs_logging_2.png)

We can now enable the job and run it. Notice the new log types and the colors associated with the level of severity:

![jobs_logging_3](images/jobs_logging_3.png)

In the next job, we will see how we can provide some user input in our jobs.

## User Input

We will learn more about the Django Object model in the future challenges. For now, let's add a simple user input function in the next job example.

First, let's add ```StringVar``` to the import statement:

```python
from nautobot.apps.jobs import Job, register_jobs, StringVar
```

Next, we can create a new job with user input. Note that we create a variable ```username``` using ```StringVar```, and then pass it to the ```run(self, username)``` method as an attribute:

```python
class HelloJobsWithInputs(Job):
    
    username = StringVar()

    class Meta:
        name = "Hello Jobs with User Inputs"
        description = "Hello Jobs with Different User Inputs"

    def run(self, username):
        self.logger.info(f"Hello Jobs with {username}.")

register_jobs(
    ...
    HelloJobsWithInputs,
)
```

We will see an additional field once we run the job:

![jobs_input_1](images/jobs_input_1.png)

The result page will display what we entered as the user:

![jobs_input_2](images/jobs_input_2.png)

That is it for the Day 4 challenge!

## Day 4 To Do

Remember to stop and delete the Codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/).

Go ahead and post a screenshot of the newly created jobs on a social media platform of your choice. Make sure you use the tags `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode` so we can share your progress!

In tomorrow's challenge, we dive deeper into Django ORM. See you tomorrow!

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+4+of+the+100+days+of+nautobot+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 4 of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot)

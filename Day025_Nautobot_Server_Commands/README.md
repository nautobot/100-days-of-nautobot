# Nautobot Server Commands

Nautobot includes a command-line (CLI) management utility called `nautobot-server`. It is often times used as a single entry point for common administrative tasks. 

> [!TIP]
> If you have prior Django experience, as stated in the [nautobot-server](https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/tools/nautobot-server/) documentaiton, `nautobot-server` works exactly as a Django project's `manage.py` script would, with additional Nautobot code. 

We have actually been using many of the CLI commands in previous days as aliases. For example, in `Day 003` in the `docker-compose.local.yml` file we saw we use the `nautobot-server runserver 0.0.0.0:8080` to run the development server in the `nautobot` container. In `Day 005`, when we type `invoke nbshell`, the output tells us it is running a docker compose command that is a wrapper for `nautobot-server`, here is an example of the output: 

```
(nautobot-docker-compose-py3.10) @ericchou1 ➜ ~/nautobot-docker-compose (main) $ invoke nbshell

...
Running docker compose command "exec nautobot nautobot-server shell_plus"
...
```

The documentation for [nautobot-server](https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/tools/nautobot-server/) provides the full documentation for the available options. In today's challenge, we will introduce a few examples and options. 

## Environment Setup

The environment setup will be the same as [Lab Setup Scenario 1](../Lab_Setup/scenario_1_setup/README.md), below is a summary of the steps, please consult the guide for a detailed background if needed. 

> [!TIP]
> We keep lab notes in the [Lab Related Notes](../Lab_Setup/lab_related_notes/README.md) for helpful tips in the various lab scenario. 

If you stopped the Codespace environment, simply restart it and use the following steps to start Naudotbot, you do not need to rebuild docker instances, nor import the database again: 

```bash
$ cd nautobot-docker-compose/
$ poetry shell
$ invoke debug
```

If you need to completely rebuild the environment in Codespace, here are the steps: 

```bash
$ cd nautobot-docker-compose/
$ poetry shell
$ invoke build
$ invoke db-import
$ invoke debug
```

We do not need to use Containerlab for today's challenge. 

## Nautobot-Server Examples

We will need to get into the `nautobot` container shell environment: 

```bash
@ericchou1 ➜ ~ $ docker exec -u root -it nautobot_docker_compose-nautobot-1 bash
root@ee2753f052ae:/opt/nautobot#
```

The first thing we can try is to run the previously created jobs from the command line using `nautobot-server runjob [module:class] -u [user]`. Assume we have a `hello_job.py file` created with a `HelloWorldwithLogs` job inside: 

```
root@ee2753f052ae:/opt/nautobot# nautobot-server runjob hello_job.HelloWorldwithLogs -u admin
[23:47:37] Running hello_job.HelloWorldwithLogs...
        initialization: 0 debug, 1 info, 0 warning, 0 error, 0 critical
                info: Hello World with Logs: Running job
        post_run: 0 debug, 1 info, 0 warning, 0 error, 0 critical
                info: Job completed
        run: 1 debug, 1 info, 1 warning, 1 error, 1 critical
                info: This is an log of info type.
                debug: This is an log of debug type.
                warning: This is an log of warning type.
                error: This is an log of error type.
                critical: This is an log of critical type.
[23:47:38] hello_job.HelloWorldwithLogs: SUCCESS
[23:47:38] hello_job.HelloWorldwithLogs: Duration 0 minutes, 0.30 seconds
[23:47:38] Finished
```

We can use `nautobot-server help` to see the available options: 

```
root@ee2753f052ae:/opt/nautobot# nautobot-server help

Type 'nautobot-server help <subcommand>' for help on a specific subcommand.

Available subcommands:

[auth]
    changepassword
    createsuperuser

[constance]
    constance

[contenttypes]
    remove_stale_contenttypes

[core]
    audit_dynamic_groups
    audit_graphql_queries
    celery
    generate_secret_key
    generate_test_data
    makemigrations
    migrate
    nbshell
...
```

To see more details about a `subcommand`, we can use `nautobot-server help <subcommand>`, we can use the help menu to see how to create an additional `superuser`: 

```
root@ee2753f052ae:/opt/nautobot# nautobot-server help createsuperuser
usage: nautobot-server createsuperuser [-h] [--username USERNAME] [--noinput] [--database DATABASE] [--email EMAIL] [--version] [-v {0,1,2,3}] [--settings SETTINGS]
                                       [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]

Used to create a superuser.

optional arguments:
  -h, --help            show this help message and exit
  --username USERNAME   Specifies the login for the superuser.
  --noinput, --no-input
                        Tells Django to NOT prompt the user for input of any kind. You must use --username with --noinput, along with an option for any other required
                        field. Superusers created with --noinput will not be able to log in until they're given a valid password.
  --database DATABASE   Specifies the database to use. Default is "default".
  --email EMAIL         Specifies the email for the superuser.
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the DJANGO_SETTINGS_MODULE environment variable will
                        be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
  --traceback           Raise on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.
```

Let's go ahead and create an additional superuser: 

```
root@ee2753f052ae:/opt/nautobot# nautobot-server createsuperuser
Username: <username>
Email address: <email>
Password: <password>
Password (again): <password>
Superuser created successfully.
```

Try to log in with the new user in the WebUI! 

## Day 25 To Do

Great job on completing a 1/4 of the challenges!

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/). 

 Your to-do today is to find another command from the documentation and learn more about it. Go ahead and post which command you find interesting and learned about on a social media of your choice, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress! 

In tomorrow's challenge, we will enhance our debug skills with `PDB`. See you tomorrow!  

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+25+of+the+100+days+of+nautobot+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 25 of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot)

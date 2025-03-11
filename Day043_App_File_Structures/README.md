# Nautobot App File Structures

In today's challenge, we will dive deeper into the [Nautobot App Structure](https://docs.nautobot.com/projects/core/en/stable/development/apps/api/setup/). Each Nautobot app is a self-contained Django application, which means it contains components such as database models, URL routing, HTML templates, and view construction. 

In the app developer guide, the following structure is listed with a one-line explanation of what the file do: 

```
app_name/
  - app_name/
    - __init__.py           # required
    - admin.py              # Django Admin Interface
    - api/
      - serializers.py      # REST API Model serializers
      - urls.py             # REST API URL patterns
      - views.py            # REST API view sets
    - banner.py             # Banners
    - custom_validators.py  # Custom Validators
    - datasources.py        # Loading Data from a Git Repository
    - filter_extensions.py  # Extending Filters
    - filters.py            # Filtersets for UI, REST API, and GraphQL Model Filtering
    - forms.py              # UI Forms and Filter Forms
    - graphql/
      - types.py            # GraphQL Type Objects
    - homepage.py           # Home Page Content
    - jinja_filters.py      # Jinja Filters
    - jobs.py               # Job classes
    - middleware.py         # Request/response middleware
    - migrations/
      - 0001_initial.py     # Database Models
    - models.py             # Database Models
    - navigation.py         # Navigation Menu Items
    - secrets.py            # Secret Providers
    - signals.py            # Signal Handler Functions
    - table_extensions.py   # Extending Tables
    - template_content.py   # Extending Core Templates
    - templates/
      - app_name/
        - *.html            # UI content templates
    - urls.py               # UI URL Patterns
    - views.py              # UI Views and any view override definitions
  - pyproject.toml          # *** REQUIRED *** - Project package definition
  - README.md
```

It looks a bit intimidated for someone new to Django. The good news is we do not need to know all the files' purposes to make progress. For example, if we do not want to construct REST APIs for our app, we do not need to worry about the `api/` folder. 

We will cover a few of the more important files in today's challenge.   

## Environment Setup

Restart the Codespace instance from [Day 42](../Day042_Baking_an_App_Cookie/README.md) and start the app development environment: 

```
@ericchou1 ➜ ~ $ cd outputs/nautobot-app-my-awesome-app/
@ericchou1 ➜ ~/outputs/nautobot-app-my-awesome-app $ poetry shell
Spawning shell within /home/vscode/.cache/pypoetry/virtualenvs/my-awesome-app-TNUNvfeN-py3.10
@ericchou1 ➜ ~/outputs/nautobot-app-my-awesome-app $ . /home/vscode/.cache/pypoetry/virtualenvs/my-awesome-app-TNUNvfeN-py3.10/bin/activate
(my-awesome-app-py3.10) @ericchou1 ➜ ~/outputs/nautobot-app-my-awesome-app $

(my-awesome-app-py3.10) @ericchou1 ➜ ~/outputs/nautobot-app-my-awesome-app $ invoke debug
Starting  in debug mode...
Running docker compose command "up"
 Container my-awesome-app-redis-1  Created
 Container my-awesome-app-db-1  Created
 Container my-awesome-app-nautobot-1  Created
...
nautobot-1  | Django version 4.2.20, using settings 'nautobot_config'
nautobot-1  | Starting development server at http://0.0.0.0:8080/
nautobot-1  | Quit the server with CONTROL-C.
nautobot-1  | 
```

Let's get started. 

## Code Example

For our Nautobot app, we see the following files in the directory: 

```
(my-awesome-app-py3.10) @ericchou1 ➜ ~/outputs/nautobot-app-my-awesome-app $ tree .
.
├── changes
├── development
│   ├── app_config_schema.py
│   ├── creds.env
│   ├── creds.example.env
│   ├── development.env
│   ├── development_mysql.env
│   ├── docker-compose.base.yml
│   ├── docker-compose.dev.yml
│   ├── docker-compose.mysql.yml
│   ├── docker-compose.postgres.yml
│   ├── docker-compose.redis.yml
│   ├── Dockerfile
│   ├── nautobot_config.py
│   └── towncrier_template.j2
├── docs
│   ├── admin
│   │   ├── compatibility_matrix.md
│   │   ├── install.md
│   │   ├── release_notes
│   │   │   ├── index.md
│   │   │   └── version_1.0.md
│   │   ├── uninstall.md
│   │   └── upgrade.md
│   ├── assets
│   │   ├── extra.css
│   │   ├── favicon.ico
│   │   ├── nautobot_logo.png
│   │   ├── nautobot_logo.svg
│   │   ├── networktocode_bw.png
│   │   └── overrides
│   │       └── partials
│   │           └── copyright.html
│   ├── dev
│   │   ├── arch_decision.md
│   │   ├── code_reference
│   │   │   ├── api.md
│   │   │   ├── index.md
│   │   │   └── package.md
│   │   ├── contributing.md
│   │   ├── dev_environment.md
│   │   ├── extending.md
│   │   └── release_checklist.md
│   ├── images
│   │   └── icon-my-awesome-app.png
│   ├── index.md
│   ├── requirements.txt
│   └── user
│       ├── app_getting_started.md
│       ├── app_overview.md
│       ├── app_use_cases.md
│       ├── external_interactions.md
│       └── faq.md
├── invoke.example.yml
├── invoke.mysql.yml
├── LICENSE
├── mkdocs.yml
├── my_awesome_app
│   ├── api
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-311.pyc
│   │   │   ├── serializers.cpython-311.pyc
│   │   │   ├── urls.cpython-311.pyc
│   │   │   └── views.cpython-311.pyc
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── app-config-schema.json
│   ├── filters.py
│   ├── forms.py
│   ├── __init__.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   │       ├── 0001_initial.cpython-311.pyc
│   │       └── __init__.cpython-311.pyc
│   ├── models.py
│   ├── navigation.py
│   ├── __pycache__
│   │   ├── filters.cpython-311.pyc
│   │   ├── forms.cpython-311.pyc
│   │   ├── __init__.cpython-311.pyc
│   │   ├── models.cpython-311.pyc
│   │   ├── navigation.cpython-311.pyc
│   │   ├── tables.cpython-311.pyc
│   │   ├── urls.cpython-311.pyc
│   │   └── views.cpython-311.pyc
│   ├── tables.py
│   ├── templates
│   │   └── my_awesome_app
│   │       └── myawesomeappexamplemodel_retrieve.html
│   ├── tests
│   │   ├── fixtures.py
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   ├── test_api_views.py
│   │   ├── test_basic.py
│   │   ├── test_filter_myawesomeappexamplemodel.py
│   │   ├── test_form_myawesomeappexamplemodel.py
│   │   ├── test_model_myawesomeappexamplemodel.py
│   │   └── test_views.py
│   ├── urls.py
│   └── views.py
├── poetry.lock
├── pyproject.toml
├── README.md
└── tasks.py

21 directories, 88 files
```

Let's unpack some of them: 

- For now, we can ignore the changes, development, docs, and other files at the root directory except `my_awesome_app` folder. 
- In the `my_awesome_app` folder, we want to pay more attention to the following items: `models.py`, `navigation.py`, `templates/` folder, `urls.py`, and `views.py`. 

```
(my-awesome-app-py3.10) @ericchou1 ➜ ~/outputs/nautobot-app-my-awesome-app $ tree my_awesome_app/
my_awesome_app/
├── api
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-311.pyc
│   │   ├── serializers.cpython-311.pyc
│   │   ├── urls.cpython-311.pyc
│   │   └── views.cpython-311.pyc
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── app-config-schema.json
├── filters.py
├── forms.py
├── __init__.py
├── migrations
│   ├── 0001_initial.py
│   ├── __init__.py
│   └── __pycache__
│       ├── 0001_initial.cpython-311.pyc
│       └── __init__.cpython-311.pyc
├── models.py
├── navigation.py
├── __pycache__
│   ├── filters.cpython-311.pyc
│   ├── forms.cpython-311.pyc
│   ├── __init__.cpython-311.pyc
│   ├── models.cpython-311.pyc
│   ├── navigation.cpython-311.pyc
│   ├── tables.cpython-311.pyc
│   ├── urls.cpython-311.pyc
│   └── views.cpython-311.pyc
├── tables.py
├── templates
│   └── my_awesome_app
│       └── myawesomeappexamplemodel_retrieve.html
├── tests
│   ├── fixtures.py
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_api_views.py
│   ├── test_basic.py
│   ├── test_filter_myawesomeappexamplemodel.py
│   ├── test_form_myawesomeappexamplemodel.py
│   ├── test_model_myawesomeappexamplemodel.py
│   └── test_views.py
├── urls.py
└── views.py

8 directories, 39 files
```

## Explanation of Key Files and Directories

### `models.py`
- Defines the database models (schemas) for the application.
- Models represent the structure of the data stored in the database.
- Each model corresponds to a database table.
- Attributes of the model correspond to columns in the table.

### `navigation.py`
- Defines the navigation structure for the application.
- Configures how the app integrates into the Nautobot UI.
- Specifies menu items, links, and navigation elements.

### `templates` Folder
- Contains HTML template files used to render views in the application.
- Templates define the structure and layout of HTML pages.
- Used to dynamically generate HTML content based on data from views.

### `urls.py`
- Defines the URL routing for the application.
- Maps URL patterns to views.
- Determines what code to execute when a user visits a specific URL.

### `views.py`
- Defines the view functions or classes for the application.
- Views contain the logic to process requests and return responses.
- Typically render templates with data.

The rest of the files' purposes are briefly listed below. 

## Root Directory

- **changes**: Directory likely used for tracking changes, such as versioning or change logs.
- **development**: Contains files related to development environment setup.
  - **app_config_schema.py**: Schema definition for the application configuration.
  - **creds.env**: Environment variables for credentials (not committed to version control).
  - **creds.example.env**: Example credentials file for reference.
  - **development.env**: Environment variables for the development environment.
  - **development_mysql.env**: Environment variables for development with MySQL.
  - **docker-compose.base.yml**: Base Docker Compose file.
  - **docker-compose.dev.yml**: Docker Compose file for development environment.
  - **docker-compose.mysql.yml**: Docker Compose file for using MySQL.
  - **docker-compose.postgres.yml**: Docker Compose file for using PostgreSQL.
  - **docker-compose.redis.yml**: Docker Compose file for using Redis.
  - **Dockerfile**: Dockerfile to build the Docker image.
  - **nautobot_config.py**: Nautobot configuration file.
  - **towncrier_template.j2**: Template for generating release notes with Towncrier.

- **docs**: Documentation files for the app.
  - **admin**: Documentation for administrators.
    - **compatibility_matrix.md**: Compatibility information.
    - **install.md**: Installation instructions.
    - **release_notes**: Release notes folder.
      - **index.md**: Index of release notes.
      - **version_1.0.md**: Release notes for version 1.0.
    - **uninstall.md**: Uninstallation instructions.
    - **upgrade.md**: Upgrade instructions.
  - **assets**: Static assets for documentation.
    - **extra.css**: Additional CSS for styling.
    - **favicon.ico**: Favicon for the documentation site.
    - **nautobot_logo.png**: Nautobot logo in PNG format.
    - **nautobot_logo.svg**: Nautobot logo in SVG format.
    - **networktocode_bw.png**: Network to Code logo in black and white.
    - **overrides**: Overrides for documentation templates.
      - **partials**: Partial template overrides.
        - **copyright.html**: Copyright information template.
  - **dev**: Developer documentation.
    - **arch_decision.md**: Architectural decisions.
    - **code_reference**: Code reference documentation.
      - **api.md**: API documentation.
      - **index.md**: Index of code references.
      - **package.md**: Package documentation.
    - **contributing.md**: Contribution guidelines.
    - **dev_environment.md**: Setup instructions for development environment.
    - **extending.md**: Instructions for extending the app.
    - **release_checklist.md**: Checklist for releasing new versions.
  - **images**: Images used in the documentation.
    - **icon-my-awesome-app.png**: Icon for the app.
  - **index.md**: Index page for the documentation.
  - **requirements.txt**: List of Python dependencies for building the documentation.
  - **user**: User documentation.
    - **app_getting_started.md**: Getting started guide.
    - **app_overview.md**: Overview of the app.
    - **app_use_cases.md**: Use cases for the app.
    - **external_interactions.md**: Interactions with external systems.
    - **faq.md**: Frequently asked questions.

- **invoke.example.yml**: Example configuration for Invoke tasks.
- **invoke.mysql.yml**: Configuration for Invoke tasks with MySQL.
- **LICENSE**: License file for the project.
- **mkdocs.yml**: Configuration file for MkDocs documentation generator.
- **my_awesome_app**: Main application directory.
  - **api**: API implementation.
    - **__init__.py**: Initialization file for the API module.
    - **serializers.py**: Serializers for API endpoints.
    - **urls.py**: URL routing for API endpoints.
    - **views.py**: View functions or classes for API endpoints.
  - **app-config-schema.json**: JSON schema for app configuration.
  - **filters.py**: Custom filters for the app.
  - **forms.py**: Django forms for the app.
  - **__init__.py**: Initialization file for the app module.
  - **migrations**: Database migrations.
    - **0001_initial.py**: Initial migration file.
    - **__init__.py**: Initialization file for the migrations module.
  - **models.py**: Database models for the app.
  - **navigation.py**: Navigation configuration for the app.
  - **tables.py**: Custom tables for the app.
  - **templates**: Templates for rendering HTML.
    - **my_awesome_app**: Directory for app-specific templates.
      - **myawesomeappexamplemodel_retrieve.html**: Template for retrieving example model data.
  - **tests**: Test cases for the app.
    - **fixtures.py**: Test fixtures.
    - **test_api.py**: Tests for API endpoints.
    - **test_api_views.py**: Tests for API views.
    - **test_basic.py**: Basic tests.
    - **test_filter_myawesomeappexamplemodel.py**: Tests for filters.
    - **test_form_myawesomeappexamplemodel.py**: Tests for forms.
    - **test_model_myawesomeappexamplemodel.py**: Tests for models.
    - **test_views.py**: Tests for views.
  - **urls.py**: URL routing for the app.
  - **views.py**: View functions or classes for the app.

- **poetry.lock**: Lock file for Poetry dependency manager.
- **pyproject.toml**: Configuration file for Poetry and other tools.
- **README.md**: Readme file for the project.
- **tasks.py**: Task definitions for Invoke.

Understanding the files' purposes is the first step in working with them. Congratulations on taking that first step! 

Believe it or not, our newly created app is a valid app that can be distributed. In the next two days, we will see how we can pack and distribute the app. 

## Day 43 To Do

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/). 

Go ahead and post a screenshot of a new app structure that you have installed for today's challenge, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress! 

In tomorrow's challenge, we start the process of distributing our newly created app. See you tomorrow! 

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+jst+completed+Day+43+of+the+100+days+of+nautobot+challenge+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 43 of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot-challenge, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot) 
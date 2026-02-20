# Becycle-mx

<div align="center">
	<img src="https://raw.githubusercontent.com/RieCo432/becycle-mx/0fb180166325a4421427fd291cdef73860fb0c2c/vuejs/public/logo/becycle/full.svg" alt="Becycle Logo" width="500" height="100" />
</div>

BECYCLE Workshop SCIO is a small, wholly volunteer operated and donations based community bike workshop that provides a free place to access practical help, education, learning and advice for maintaining and repairing bikes. When you come to BECYCLE be ready to learn from volunteers, and work with them to fix your bike together.

## Contents

- [Development Setup](#development-setup)
	- [Requirements](#requirements)
	- [Getting Started](#getting-started)
		- [Setting up the environment variables](#setting-up-the-environment-variables)
		- [Running the code](#running-the-code)
			- [Individual docker images](#individual-docker-images)
			- [Backend API](#backend-api)
			- [Frontend VueJS](#frontend-vuejs)
- [Recurring SQL](#recurring-sql)
- [Contributing](#contributing)
	- [General Workflow](#general-workflow)
		- [Branches](#branches)
		- [Commits](#commits)
	- [When development is done](#when-development-is-done)
	- [Database changes](#database-changes)

## Development Setup

### Requirements

- [Docker](https://www.docker.com/)

The following are required if you wish to run the vuejs app and python api directly, instead of running the docker container:
- [Python](https://www.python.org/downloads/)
	- The fastapi docker file is using version [3.11.7](https://www.python.org/downloads/release/python-3117/), so if you have any problems try using this version.
	- (*Optional*) Would recommend using [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation), instead of directly installing a specfic version, as it will make managing python versions easier if you need to change them.
- [NodeJS](https://nodejs.org/en/download)
	- [Yarn](https://classic.yarnpkg.com/en/) `npm install -g yarn`
	- (*Optional*) Would recommend using [NVM](https://github.com/nvm-sh/nvm), instead of directly installing a specfic version, as it will make managing node versions easier if you need to change them.

### Getting Started

1. Clone the repository.
	- If you're not a contributor, you should fork the repository. That way you can make pull requests.
2. Checkout the `dev` branch.
3. See [Contributing - General Workflow](#general-workflow) for more info on creating branches, and commits.

#### Setting up the environment variables

1. Create a copy of the following files and and remove `.template` from the end:
	- `secrets/api.env.template`
	- `secrets/postgres.env.template`
	- `fastapi/local-api.env.template`
	- `vuejs/.env.template`
2. For the `secrets/api.env` update:
	- `API_SECRET` can be generated using `openssl rand -hex 32`
	- `GOOGLE_ACCOUNT` and `GOOGLE_APP_PASSWORD` can be obtained from the Google Account Security settings, but are not required for dev purposes.
3. For `secrets/postgres.env` put whatever you find appropriate here:
	- `POSTGRES_USER`
	- `POSTGRES_DB`
	- `POSTGRES_PASSWORD`
	- `POSTGRES_PORT` the default is normally `5432`
4. For `fastapi/local-api.env` update:
	- Set the following as the same as in `api.env`
		- `API_SECRET`
		- `EMAIL_FROM`
		- `GOOGLE_ACCOUNT`
		- `GOOGLE_APP_PASSWORD`
	- Set the following as the same as in `postgres.env`.
		- `POSTGRES_USER`
		- `POSTGRES_DB`
		- `POSTGRES_PASSWORD`
		- `POSTGRES_PORT`
5. For `vuejs/.env` you shouldn't need to update anything.

#### Running the code

The easiest way to get started is to just run: `sudo docker-compose up`. This isn't the easiest to develop for however, as the docker files don't handle hot reloads (may be possible, you can make a PR if you now how to, *wink wink nudge nudge*).

##### Individual docker images

If you want to run only specific images you can do the following:

- Postgres: `docker-compose up -d postgres`
- Fastapi: `docker-compose up -d api`
- VueJS: `docker-compose up -d web`

##### Backend API

1. Run `python -m venv venv`, you now have a virtual environment called `venv` (the `venv` folder will be ignored in git).
	- May need to be `python3` instead of `python`.
2. Now run `./venv/bin/pip install -r ./fastapi/requirements.txt`, this will install all of the python packages for fastapi.
	- If you're running on linux, and encounter an error installing `psycopg2`, you may need to install `libpq-dev`.
3. Move into the fastapi folder `cd fastapi`.
4. Run `../venv/bin/alembic upgrade head` within your virtual environment to make sure your local database is up-to-date with all the most recent migrations.

##### Frontend VueJS

1. Move into the vuejs folder `cd vuejs`.
1. Install the packages `yarn install`.
3. Run the app `yarn run dev`

## Recurring SQL

These commands must be run periodically, using something like cron:

```bash 
sudo docker exec becycle-mx_postgres_1 psql -U becycleAdmin becycledb -c "delete from clientlogins where expirationdatetime<current_timestamp;"

sudo docker exec becycle-mx_postgres_1 psql -U becycleAdmin becycledb -c "delete from clientstemp where expirationdatetime<current_timestamp;"

sudo docker exec becycle-mx_postgres_1 psql -U becycleAdmin becycledb -c "update users set softdeleted=true where lastauthenticated < current_timestamp at time zone 'utc' - interval '6 months';"

sudo docker exec becycle-mx_postgres_1 psql -U becycleAdmin becycledb -c "delete from clients where id in (select id from orphanedclients) and createdon < (current_timestamp at time zone 'utc') - interval '7 days';"

sudo docker exec becycle-mx_postgres_1 psql -U becycleAdmin becycledb -c "delete from bikes where id in (select id from orphanedbikes) and createdon < (current_timestamp at time zone 'utc') - interval '7 days';"

sudo docker exec becycle-mx_postgres_1 psql -U becycleAdmin becycledb -c "delete from contractdrafts where clientid is null and startDate < (current_date at time zone 'UTC') - interval '1 day';"
```

With cron, this can be used to run the command every hour: `0 * * * *`

## Contributing

### General Workflow

1. If working on a GitHub issue, please assign the issue to yourself and move it into the "In progress" stage.
	- If not working on a GitHub issue, consider creating one.
2. Create a new branch off of the "dev" branch following the naming conventions below:

	#### Branches
	- Where applicable, prefix the branch name with the number of the GitHub issue being worked on.
	- Use a short string of words, separated by hyphens to give a rough indication of what the purpose is. Often, the part of the program being worked on can be good.
	- For example: #53-eslint-fixes
	#### Commits
	- Prefix the commit message with the GitHub issue number being worked on if applicable.
	- Say what this commit addresses in particular. If it can't fit into the standard 72 character limit, consider dividing your commit into a few, smaller, more concise commits.
	- For example: "#53 fix eslint issues in all the views".

#### When development is done

1. Create a pull request into the dev branch.
2. If working on a GitHub issue, please move the issue into the "In review" stage.
3. This will be reviewed, and potential problems highlighted. Discussions must be resolved before the pull request will be accepted.
4. Once accepted, the PR can be merged.
5. If the PR was related to an issue, this should now be moved into the "Accepted" stage.
6. Periodically, the dev branch will be checked to see if it is functional.
7. If it passes tests (both automated and manual), it will be merged into the main branch.
8. This will trigger the CD pipeline and all the changes will be deployed to the live site.
9. All relevant issues should now be moved into the "Done" stage.

#### Database changes
1. If changes to the database schema are required, please make those changes purely in code, most likely in the fastapi/models/ directory.
2. Then, with the virtual environment active, run
`alembic revision --autogenerate -m "what has changed"` 
to generate a migration script.
3. Double check this migration script, which can be found in fastapi/alembic/versions and adjust if required.
4. Apply the migration by running `alembic upgrade head`
  


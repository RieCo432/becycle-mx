Setup:

Copy .env.template files and remove the .template extension of the environment files in secrets/, fastapi/, and vuejs/ and add the required information

API SECRET can be optained using
$ openssl rand -hex 32

GOOGLE ACCOUNT and GOOGLE APP PASSWORD can be obtained from the Google Account Security settings, but are not required for dev purposes

POSTGRES HOST is "postgres", the name of the docker compose service

These commands must be run periodically, using something like cron:

sudo docker exec becycle-mx_postgres_1 psql -U becycleAdmin becycledb -c "delete from clientlogins where expirationdatetime<current_timestamp;"

sudo docker exec becycle-mx_postgres_1 psql -U becycleAdmin becycledb -c "delete from clientstemp where expirationdatetime<current_timestamp;"

sudo docker exec becycle-mx_postgres_1 psql -U becycleAdmin becycledb -c "update users set softdeleted=true where lastauthenticated < current_timestamp at time zone 'utc' - interval '6 months';"

with cron, this can be used to run the command every hour:
0 * * * *


Development:

    General Workflow:
	  - If working on a GitHub issue, please assign the issue to yourself and move it into the "In progress" stage
	  - If not working on a GitHub issue, consider creating one
	  - checkout the dev branch and do a pull to receive the most recent code
	  - run
	    $ alembic upgrade head
		within your virtual environment to make sure your local database is up-to-date with all the most recent migrations
	  - create a new branch off of the "dev" branch following the naming conventions below:
		  - Branches:
			- Where applicable, prefix the branch name with the number of the GitHub issue being worked on.
			- Use a short string of words, separated by hyphens to give a rough indication of what the purpose is. Often, the part of the program being worked on can be good
			- For example: #53-eslint-fixes
		  - Commit:
			- prefix the commit message with the GitHub issue number being worked on if applicable
			- say what this commit addresses in particular. If it can't fit into the standard 72 character limit, consider dividing your commit into a few, smaller, more concise commits
			- For example: "#53 fix eslint issues in all the views"
	When development is done:
	  - Create a pull request into the dev branch.
	  - If working on a GitHub issue, please move the issue into the "In review" stage
	  - This will be reviewed, and potential problems highlighted. Discussions must be resolved before the pull request will be accepted
	  - Once accepted, the PR will be merged using the squash strategy, to keep the number of commits on the dev branch within reason
	  - If the PR was related to an issue, this should now be moved into the "Accepted" stage
	  - periodically, the dev branch will be checked to see if it is functional
	  - If it passes tests (both automated and manual), it will be merged into the main branch
	  - This will trigger the CD pipeline and all the changes will be deployed to the live site
	  - All relevant issues should now be moved into the "Done" stage.
    Database changes:
      - If changes to the database schema are required, please make those changes purely in code, most likely in the fastapi/models/ directory
	  - Then, with the virtual environment active, run
	    $ alembic revision --autogenerate -m "what has changed"
	    To generate a migration script
	  - Double check this migration script, which can be found in fastapi/alembic/versions and adjust if required
	  - Apply the migration by running
	    $ alembic upgrade head
  


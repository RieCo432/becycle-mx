# Contributing

## General Workflow

1. If working on a GitHub issue, please assign the issue to yourself and move it into the "In progress" stage.
	- If not working on a GitHub issue, consider creating one.
2. Create a new branch off of the "dev" branch following the naming conventions below:

	### Branches
	- Where applicable, prefix the branch name with the number of the GitHub issue being worked on.
	- Use a short string of words, separated by hyphens to give a rough indication of what the purpose is. Often, the part of the program being worked on can be good.
	- For example: #53-eslint-fixes
	### Commits
	- Prefix the commit message with the GitHub issue number being worked on if applicable.
	- Say what this commit addresses in particular. If it can't fit into the standard 72 character limit, consider dividing your commit into a few, smaller, more concise commits.
	- For example: "#53 fix eslint issues in all the views".

### When development is done

1. Create a pull request into the dev branch.
2. If working on a GitHub issue, please move the issue into the "In review" stage.
3. This will be reviewed, and potential problems highlighted. Discussions must be resolved before the pull request will be accepted.
4. Once accepted, the PR can be merged.
5. If the PR was related to an issue, this should now be moved into the "Accepted" stage.
6. Periodically, the dev branch will be checked to see if it is functional.
7. If it passes tests (both automated and manual), it will be merged into the main branch.
8. This will trigger the CD pipeline and all the changes will be deployed to the live site.
9. All relevant issues should now be moved into the "Done" stage.

### Database changes
1. If changes to the database schema are required, please make those changes purely in code, most likely in the fastapi/models/ directory.
2. Then, with the virtual environment active, run
`alembic revision --autogenerate -m "what has changed"` 
to generate a migration script.
3. Double check this migration script, which can be found in fastapi/alembic/versions and adjust if required.
4. Apply the migration by running `alembic upgrade head`
  


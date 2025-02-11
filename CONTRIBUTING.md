# Contributing

Thank you for your interest in contributing to the `eptalights-python` codebase!

If you would like to add or update a feature in `eptalights-python`,
it is recommended that you first file a GitHub issue to discuss your proposed changes
and check their compatibility with the rest of the package before making a pull request.

This page assumes that you have already created a fork of the `eptalights-python`
repository under your GitHub account and
have the codebase available locally for development work. 

## Working on a Feature or Bug Fix

The development steps below assume that your local Git repo has a remote
`upstream` link to `eptalights/eptalights-python`:
   
```bash
git remote add upstream https://github.com/eptalights/eptalights-python.git
```

After this step (which you only have to do once),
running `git remote -v` should show your local Git repo
has links to both "origin" (pointing to your fork `<your-github-username>/eptalights-python`)
and "upstream" (pointing to `eptalights/eptalights-python`).

To work on a feature or bug fix:

1. Before doing any work, check out the main branch and
   make sure that your local main branch is up-to-date with upstream main:
   
   ```bash
   git checkout main
   git pull upstream main
   ``` 
   
2. Create a new branch. This branch is where you will make commits of your work.
   (As a best practice, never make commits while on a `main` branch.
   Running `git branch` tells you which branch you are on.)
   
   ```bash
   git checkout -b new-branch-name
   ```
   
3. Make as many commits as needed for your work.

4. When you feel your work is ready for a pull request,
   push your branch to your fork.

   ```bash
   git push origin new-branch-name
   ```
   
5. Go to your fork `https://github.com/<your-github-username>/eptalights-python` and
   create a pull request off of your branch against the `eptalights/eptalights-python` repo.

## Running Tests and Code Style Checks

The `eptalights-python` repo has continuous integration (CI) turned on,
with autobuilds running pytest
(for the test suite in [`tests/`](tests))
as well as `black` and `flake8` for consistent code styling.
If an autobuild at an open pull request fails,
then the errors must be fixed by further commits pushed to the branch
by the author before merging is possible.

you can run pytest/flake8/black checks locally before pushing commits:

```bash
flake8 src tests
black --check src tests
pytest
```
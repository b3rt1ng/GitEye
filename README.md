<h1 align="center">
  GitEye
</h1>

<h4 align="center">A simple OSINT tool to analyse git metadata and audit your own GitHub footprint

<p align="center">
  <a href="#features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#customize">Customize</a>
</p>


# Context

GitEye queries the GitHub API to gather information about a repository's authors and commit history, then looks for files of interest and keywords that may leak critical information. It also works the other way around: point it at a GitHub username and it audits every public repo that account owns, surfacing every name/email that account has ever committed with, so you can check what your own GitHub profile is leaking before someone else finds it.

It never clones or downloads anything: everything is done through HTTP requests, so nothing from the target ever touches your disk.

## Features

**Repository analysis** (`-u/--url`)
- retrieve commit authors and their email addresses
- get the commit history
- find interesting files
- find keywords within the interesting files

**GitHub profile audit** (`--username`)
- scan every non-fork public repo a username owns
- list every name/email that username has committed with, ranked by frequency and repo
- flag exposed (non-anonymized) email addresses
- generate the `git filter-repo` commands to scrub them, with `--help-me-fix`

## Setup

```bash
# Clone this repository
$ git clone https://github.com/b3rt1ng/GitEye

# Go into the repository
$ cd GitEye

# Install dependencies
$ pip install -r requirements.txt

# Optional: enable the file/secret scanning stage and raise the GitHub API
# rate limit from 60 to 5000 req/h by providing a GitHub token
$ cp .env.example .env
$ echo "GITHUB_TOKEN=ghp_xxx" >> .env
```

## How To Use

```bash
# Analyze a single GitHub repository
$ python3 main.py -u https://github.com/user/project

# Audit a GitHub profile: scans their non-fork public repos and lists every
# name/email they've committed with, ranked by how often each appears
$ python3 main.py --username someuser

# Add --help-me-fix to also flag exposed (non-anonymized) emails and print
# ready-to-run git filter-repo + force-push commands per affected repo
$ python3 main.py --username someuser --help-me-fix

# Pass 'ssh' if you push over SSH rather than HTTPS, to get git@github.com:... remotes
$ python3 main.py --username someuser --help-me-fix ssh
```
> **Note**
> Some of the info can be long and are getting shortened by default, pass the `-d` or `--detailed` argument to the command prompt to display everything. In `--username` mode, `-d` also prints every individual commit trace (repo, name, mail, date) instead of just the aggregated identities table.
> **Note**
> `--help-me-fix` requires [`git-filter-repo`](https://github.com/newren/git-filter-repo) (`pip install git-filter-repo`), a separate tool, not a built-in git subcommand. Rewriting history changes commit SHAs: existing forks/clones/PRs keep the old exposed commits, and GH Archive may already have a permanent copy.
> **Note**
> Without a `GITHUB_TOKEN` set, GitEye only reports commit/author metadata (subject to GitHub's 60 req/h anonymous rate limit) and skips the file/secret scanning stage. The `--username` profile audit always works without a token since it only needs commit metadata.

## Customize
You can remove or add more keywords and file types in the `interest.json` file :)

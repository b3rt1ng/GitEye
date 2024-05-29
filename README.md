<h1 align="center">
  GitEye
</h1>

<h4 align="center">A simple OSINT tool to analyse git metadata

<p align="center">
  <a href="#features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#customize">Customize</a>
</p>


# Context

GitEye is a simple tool that will look into a git metadata and gather informations about the autors and commits history. It then tries to find some files of interest and uses keywords to find critical informations.  
You can use a downloaded git and git it's path but you can also use the git's link so that GitEye will download and analyse it.

## Features

- retrieve commit authors and their email addresses
- get the commit history
- find interesting files
- find keywords withing the interesting files

## How To Use

```bash
# Clone this repository
$ git clone https://github.com/b3rt1ng/GitEye

# Go into the repository
$ cd GitEye

# Install dependencies
$ pip install -r requirements.txt

# Run the app by giving a path to the git
$ python3 main.py -p /path/to/git

# Alternatively you can give a direct link
$ python3 main.py -p https://github.com/user/project

```
> **Note**
> Some of the info can be long and are getting shortened by default, pass the `-d` or `--detailed` argument to the command prompt to display everything.

## Customize
You can remove or add more keywords and file types in the `interest.json` file :)

# Jarvis

A Python Slackbot.

## Usage

First, set up a bot user on
[your slack instance](https://slack.com/apps/manage/custom-integrations). His
name should be `jarvis` and you should use [this icon](jarvis.png).

With his API token exported to your terminal as `SLACK_TOKEN`, run:

    docker-compose build         # or docker-compose pull
    docker-compose run bot init
    docker-compose up -d

Make sure to keep your `db/jarvis.db` somewhere safe!

## Keeping Jarvis Updated

Updating Jarvis to any version post 2.0.0 is simple! To build from a specific
commit (or from `HEAD`), run:

    git pull
    git checkout <version>  # optional
    docker-compose build
    docker-compose up -d

Or, to avoid building locally, use Docker Hub:

    docker-compose pull
    docker-compose up -d

DO NOT run `docker-compose run bot init` again, unless you want to wipe out all
of Jarvis' data.

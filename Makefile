all:
	@cat Makefile


run:
	SLACK_TOKEN=`cat ~/Dropbox/secret/slack/softies-jarvis` ./jarvis.py

# ChatApp  #

Forked from https://github.com/narrowfail/django-channels-chat to play with the OpenAI GPT api.

It's a small person-to-person application built using Django where some users 
can be bots.  Bots can be defined in yaml as a pipeline of simple python steps.   

https://github.com/lukerohde/gpt-chat/assets/1400034/6e553439-3c32-4f3b-a4a5-2d2bbd671c10


# Setup

To keep local development simple we use docker and docker-compose. Docker is a prerequiste.

For the bots to work, you'll also need an openai api token.

Get started by running `./setup` which will;
* set your .env vars
* build your containers
* run you migrations 
* and setup your django root user.

After setup run `./go`

If you setup a docker-compose.override.yml file for your local mac environment, it maps the local files into the containers so you can do some programming.  It will hang the containers so you can exec in and run commands.

Run `docker-compose up -d` to run the containers - or just `./go`

Exec in like `docker-compose exec app /bin/bash`

Once in the app container run `npm run server`

To run the bots, exec in like `docker-compose exec bot /bin/bash`

Once in, run `npm run bots`

See `Using docker-compose shortcuts` below

# Changes made in this fork

So far I've
- containerised it using docker-compose
- added deployment scripts for digital ocean
- got letencrypt working 
- got websockets working behind nginx (near killed me)
- switched to redis & postgresql
- upgraded to bootstrap 5 and given it a responsive face-lift
- dark mode! It's very dark
- used stimulusjs & parcel to organise my javascript
- switched to rendering server-side rather than API + JS
- bookmarkable RESTFUL urls
- created a bot server with configurable pipelines
- made a kids gratitude journal as a test pipeline
- broken all the tests and not fixed them!!!

It's quiet a bit more complex than narrowfail's beautifully simple app.

## Principles ##

These principles are aspirational.  They originated in business process automation projects that predated the AI boom.  The intent was to ship frequent minor improvements that add value, while at no point replacing a low paid administrative worker with a highly paid dev-ops engineer.   By measuring the amount of human intervention and exception handling in each business service, we could prioritise our automation efforts.  Eventually a large majority of business processes where 'automated' except humans were in the loop, approving every step.  And if anything went wrong, humans could pickup the slack while we fixed stuff.  There were all sorts of tasks that were intractible and could only be done by humans.  Many of these could now be done by foundation models.  By adopting these principles for AI automation projects, the human stays in control and is amplified.
 
- Bots are stateless
- Bots are micro-services
- Bots are reactive
- Bots are transparent
- Bots shall do no task that cannot be corrected or completed by a human
- Bots have a persona
- Failed requests can be debugged and replayed, if not already corrected by a human 
- Bots alert to failure
- The gap between expectation and reality is measured and closed
- Bots are easy to grok, pipelines of steps
- Hackers of all levels can make their bot
- Bots can work on bots - this is new
- Bots can delegate to bots 
- Bots are idempotent
- Bots can handle random input
- Bots shall send no message on behalf of the user without approval

## Architecture ##

![Architecture](docs/architecture.png)

 - Bots are defined in app/bot_config and are loaded by the bot_manager
 - Bots consist of a series of steps that are mediated by redis
 - The bot_manager registers the bots to the django chat app
 - When the user posts a message, the chat app posts to the bot managers' api
 - When the bot replies, it posts to the chat apps' api
 - The chat app relays replies to the clients browser over websockets
 
## Assumptions ##
Because of time constraints this project lacks of:

- User Sign-In / Forgot Password
- User Selector Pagination
- Good Test Coverage
- Better Comments / Documentation Strings
- Frontend Tests
- failed to upgrade to django 4 - arrgghhh!!
- DONE Modern Frontend Framework (like React) - used stimulusjs ;)
- DONE Frontend Package (automatic lintin, building and minification) - used parcel
- DONE Proper UX / UI design (looks plain bootstrap) - pretty bootstrap


## Persisting data
This script mounts your pgdata and redis data on an external docker volume, so if you rebuild or remove your database or redis containers you don't loose all your data and don't have to reinstall all your packages.  

In the docker-compose.override.example I suggest persisting the data to local folders for inspection during local development.  I also persist the user volume for auto complete when inside your container

## Configuring/developing bots

DJANGO_SUPERUSER_TOKEN=xxx # run ./manage.py createsuperusertoken
The bot server uses DJANGO_SUPERUSER_TOKEN to register bots that are 
configured via yaml in app/bot_config.  


See bot_config/diaryfile.yaml and bot_config/japanese_bot.yaml for examples of how to make a bot.

Each step in these yaml files is a python class in the same directory.

You can make your own custom step class with a process method, that takes a payload parameter and returns the payload.  If you include
a payload['reply'] that will get posted to the user.

The pipeline approach is designed to make it simple to contribute reusable steps.   

## Deploying to Digital Ocean

To deploy to digital ocean you'll need doctl installed as a prerequisite.

On mac, `brew install doctl`

Then you'll need to config it with your digital ocean token. 

`doctl auth init`

In the deploy directory there are a number of scripts to help you get into production.  You run them from the parent directory.

* `deploy/go` will do everything
* `deploy/01-build-server` will make a digital ocean server and set `.digital_ocean_env` so your other scripts will work
* `deploy/02-config-server` this does everything to pave the road for deployment such as installing software and creating a non root user
* `deploy/03-deploy-repo` this will clone the repo in and copy up the env files mentioned below, then fire up docker compose 
* `deploy/userlogin` a shortcut for logging into the server
* `deploy/rootlogin` I should probably kill this
* `deploy/backup` take a copy of the production database
* `deploy/restore` restores the latest backup
* `deploy/cleanup` destroys the digital ocean server

If you are using the digital ocean deploy scripts in /deploy, there are two files you'll need;

* `.env-prod` for production configuration (same as .env unless you have different prod config)
* `.docker-compose-override.yml.prod` which open the app port


## Using docker-compose shortcuts
typing docker-compose all the time can be tedious so add this to your ~/.bashrc or ~/.bash_profile

Then 

`docker-compose stop && docker-compose up -d && docker-compose log -tf` 

becomes just

`dcs && dcu -d && dcl -tf`

but i have a shortcut for that too

`dcrestart`

The first alias `bp` makes editing and reloading your bash_profile easy.

The second command `get-python` makes getting this repo easy.

```
# shortcut for editing your bash profile and these shortcuts
alias bp='vim ~/.bash_profile && . ~/.bash_profile'
# Get this repo!
get-python() { git clone git@github.com:lukerohde/docker-python-template.git . ; rm -rf .git ; }
# docker shortcuts
alias ds='docker stats'
alias dc='docker-compose'
alias dce='docker-compose exec'
alias dcu='docker-compose up'
alias dcd='docker-compose down'
alias dcr='docker-compose run'
alias dcs='docker-compose stop'
alias dcb='docker-compose build'
alias dcps='docker-compose ps'
alias dcl='docker-compose logs'
alias dclf='docker-compose logs -f --tail=1000'
alias dckill='docker-compose kill'
alias dcrestart='docker-compose stop && docker-compose up -d && docker-compose logs -ft'
alias dps='docker ps'
alias dk='docker kill'
alias dkall='docker kill $(docker ps -q)'
alias drestart="osascript -e 'quit app \"Docker\"' && open -a Docker"
alias dstop='docker stop $(docker ps -aq)'
alias dprune='docker system prune -a'
dceb() { docker-compose exec $1 /bin/bash ; }
dcub() { docker-compose up -d $1 && docker-compose exec $1 /bin/bash ; }
dcudb() { docker-compose up -d db && docker-compose exec db psql -U postgres $1 ; }
ddeleteall() {
    docker stop $(docker ps -aq)
    docker system prune -a
}
```

## developing with docker on osx

Use the override file to mount your app volume with :delegated
```
cp docker-compose.override.yml.example docker-compose.override.yml
```

```
  app:
    volumes:
      - ./app:/app:delegated
```

The provided docker-compose.override.yaml.example file will not actually run your app.  Instead it runs docker-start.override that hangs the container to leave it running so you can shell in and run your application yourself.  This makes debugging easy.  

The shortcut for running your app then shelling in is
`dcub app` 

Once shelled in you can run `npm run server` etc...

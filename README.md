# ChatApp  #

![](http://g.recordit.co/JYruQDLd0h.gif)

A small functional person-to-person message center application built using Django.
It has a REST API and uses WebSockets to notify clients of new messages and 
avoid polling.

## Architecture ##
 - When a user logs in, the frontend downloads the user list and opens a
   Websocket connection to the server (notifications channel).
 - When a user selects another user to chat, the frontend downloads the latest
   15 messages (see settings) they've exchanged.
 - When a user sends a message, the frontend sends a POST to the REST API, then
   Django saves the message and notifies the users involved using the Websocket
   connection (sends the new message ID).
 - When the frontend receives a new message notification (with the message ID),
   it performs a GET query to the API to download the received message.

## Scaling ##

### Requests ###
"Because Channels takes Django into a multi-process model, you no longer run 
everything in one process along with a WSGI server (of course, you’re still 
free to do that if you don’t want to use Channels). Instead, you run one or 
more interface servers, and one or more worker servers, connected by that 
channel layer you configured earlier."

In this case, I'm using the In-Memory channel system, but could be changed to
the Redis backend to improve performance and spawn multiple workers in a
distributed environment.

Please take a look at the link below for more information:
https://channels.readthedocs.io/en/latest/introduction.html


**update 04/06/19**

- using pipenv for package management
- move to Channels 2
- use redis as the channel layer backing store. for more information, please check [channels_redis](https://github.com/django/channels_redis)

### Database ###
For this demo, I'm using a simple MySQL setup. If more performance is required, 
a MySQL cluster / shard could be deployed.

PD: I'm using indexes to improve performance.

## Assumptions ##
Because of time constraints this project lacks of:

- User Sign-In / Forgot Password
- User Selector Pagination
- Good Test Coverage
- Better Comments / Documentation Strings
- Frontend Tests
- Modern Frontend Framework (like React)
- Frontend Package (automatic lintin, building and minification)
- Proper UX / UI design (looks plain bootstrap)

## Run ##

0. run containers (daemonised)
```
docker-compose up -d
```

see logs
```
docker-compose logs -f
```

1. Shell into the python app container
```
docker-compose exec app /bin/bash
```
2. Init database
```bash
./manage.py migrate
```
3. Run tests
```bash
./manage.py test
```

4. Create admin user
```bash
./manage.py createsuperuser
```

5. Run development server
```bash
./manage.py runserver 0.0.0.0:$APP_PORT
```

To override default settings, create a local_settings.py file in the chat folder.

Message prefetch config (load last n messages):
```python
MESSAGES_TO_LOAD = 15
```

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

## Persisting data
This script mounts your pgdata and redis data on an external docker volume, so if you rebuild or remove your database or redis containers you don't loose all your data and don't have to reinstall all your packages.  

In the docker-compose.override.example I suggest persisting the data to local folders for inspection.  I also persist the user volume for auto complete when inside your container

## developing with docker on osx
On osx docker volume mounts to the host are suuupperrr slow.

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

The short cut for running your app then shelling in is
`dcub app` 

Once shelled in you can run `python3 start.py` etc...

## Using compose and the override file in production 
If running more than one compose app on a production server, you'll want to have your port mappings in the override.  For instance, it is common to clash on postgres' port 5431 unless you override this port for each app. 

If you are running multiple compose apps that use each other's api's (think microservices) but don't want to expose those service publicly, configure an external docker network.  `docker network add my-production-net`  


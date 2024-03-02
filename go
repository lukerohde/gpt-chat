#!/bin/bash
if [ ! -f .env ]; then
  echo "Please run ./setup to setup your environment"
  exit 
fi

docker-compose up -d 


if [ -f docker-compose.override.yml ]; then

    echo "YOU HAVE A DOCKER-COMPOSE OVERRIDE FILE FOR LOCAL DEV"
    echo "YOU HAVE TO EXEC INTO YOUR CONTAINERS AND RUN THEIR SERVERS"
    echo ""
    echo "run 'docker-compose exec app /bin/bash' to shell into the app container."
    echo ""
    echo "once in run 'npm run server'"
    echo "then your application should be running on http://localhost:3000"
    echo "check your .env file for your django admin superuser password"
    echo ""
    echo "for js hotreloading, shell into the app container again as above"
    echo ""
    echo "'npm run hotreloadjs'"
    echo ""
    echo "then to run your bots, shell into the bots container"
    echo "'docker-compose exec bots /bin/bash'"
    echo ""
    echo "and run 'npm run bots'"

else

    echo "Presuming you have no docker-compose.override.yml"
    echo "and having modified docker-compose.yml then"
    echo "your server should be running on"
    echo "http://localhost:3000"

fi

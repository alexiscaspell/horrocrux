PROYECTO=horrocrux
VERSION=latest

DOCKER_HUB_GROUP=alexiscaspell
DOCKER_HUB_USER=alexiscaspell
DOCKER_HUB_REPO=docker.io

DOCKERFILE_PATH=./Dockerfile

if [ -z "$1" ]
  then
  VERSION="$VERSION"
  else
  	VERSION="$1"
fi

#!/bin/bash

set -e

IMAGE_NAME="arbitrage"

if [ -z "$1" ]; then
    VERSION="latest"
else
    VERSION="$1"
fi

docker build -t $IMAGE_NAME:$VERSION .

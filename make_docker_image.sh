#!/bin/bash
## first parameter is DBCA branch name

set -e
if [[ $# -lt 1 ]]; then
    echo "ERROR: DBCA branch must be specified"
    echo "$0 1"
    exit 1
fi

REPO=$(awk '{split($0, arr, "\/"); print arr[2]}' <<< $(git config -l|grep remote|grep url|head -n 1|sed 's/-//g'|sed 's/....$//'))
REPO_NO_DASH=$(awk '{split($0, arr, "\/"); print arr[2]}' <<< $(git config -l|grep remote|grep url|head -n 1|sed 's/....$//'))
BUILD_TAG=dbcawa/$REPO:$1_v$(date +%Y.%m.%d.%H.%M%S)

{
    docker image build --build-arg REPO=$REPO --build-arg REPO_NO_DASH=$REPO_NO_DASH --build-arg BRANCH=$1 --no-cache --tag $BUILD_TAG . &&
    echo $BUILD_TAG
} ||
{
    echo "ERROR: Docker build failed"
    echo "$0 1"
    exit 1
}
{
    docker push $BUILD_TAG
} || {
    echo "ERROR: Docker push failed"
    echo "$0 1"
    exit 1
}

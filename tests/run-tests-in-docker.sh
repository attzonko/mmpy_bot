#!/bin/bash
set -euo pipefail
: ${DRIVERBOT_LOGIN:='driverbot@test.com'}
: ${DRIVERBOT_NAME:='driverbot'}
: ${DRIVERBOT_PASSWORD:='driverbot_password'}
: ${TESTBOT_LOGIN:='testbot@test.com'}
: ${TESTBOT_NAME:='testbot'}
: ${TESTBOT_PASSWORD:='testbot_password'}
: ${BOT_TEAM:='test-team'}
: ${BOT_CHANNEL:=public}
: ${BOT_PRIVATE_CHANNEL:=private}
: ${DOCKER_CONTAINER_NAME:=mmpybot-mattermost}
: ${BOT_URL:="http://${DOCKER_CONTAINER_NAME}:8065/api/v4"}
: ${DOCKER_NETWORK:=mmpybot-mattermost}
: ${PYTHON_VERSION=3.6}
. ./tests/setup.sh
docker run -ti --rm \
--net "$DOCKER_NETWORK" \
-v "$PWD:/mmpy_bot" \
-e BOT_URL="$BOT_URL" \
-e DRIVERBOT_LOGIN="$DRIVERBOT_LOGIN" \
-e DRIVERBOT_NAME="$DRIVERBOT_NAME" \
-e DRIVERBOT_PASSWORD="$DRIVERBOT_PASSWORD" \
-e TESTBOT_LOGIN="$TESTBOT_LOGIN" \
-e TESTBOT_NAME="$TESTBOT_NAME" \
-e TESTBOT_PASSWORD="$TESTBOT_PASSWORD" \
-e BOT_TEAM="$BOT_TEAM" \
-e BOT_CHANNEL="$BOT_CHANNEL" \
-e BOT_PRIVATE_CHANNEL="$BOT_PRIVATE_CHANNEL" \
--entrypoint=/mmpy_bot/tests/docker-entrypoint.sh \
-w /mmpy_bot \
python:"$PYTHON_VERSION" \
pytest

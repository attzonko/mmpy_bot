#!/bin/bash
set -ue
curl -sL https://codeclimate.com/downloads/test-reporter/test-reporter-latest-linux-amd64 > ./cc-test-reporter
chmod +x ./cc-test-reporter
./cc-test-reporter before-build
docker pull mattermost/mattermost-preview
docker kill "$DOCKER_CONTAINER_NAME" || true
docker rm "$DOCKER_CONTAINER_NAME" || true
docker network create "$DOCKER_NETWORK" || true
docker run --name "$DOCKER_CONTAINER_NAME" \
--net "$DOCKER_NETWORK" \
-d \
--publish 8065:8065 \
--add-host dockerhost:127.0.0.1 \
mattermost/mattermost-preview
echo -n "Waiting for mattermost to start"
while ! docker logs "$DOCKER_CONTAINER_NAME"  2>&1 | grep -q "Server is listening"
do
    sleep 1
    echo -n "."
done
echo ''
docker exec "$DOCKER_CONTAINER_NAME" mattermost -c /mm/mattermost/config/config_docker.json user create --email="$DRIVERBOT_LOGIN" --password="$DRIVERBOT_PASSWORD" --username "$DRIVERBOT_NAME"
docker exec "$DOCKER_CONTAINER_NAME" mattermost -c /mm/mattermost/config/config_docker.json user create --email="$TESTBOT_LOGIN" --password="$TESTBOT_PASSWORD" --username "$TESTBOT_NAME"
docker exec "$DOCKER_CONTAINER_NAME" mattermost -c /mm/mattermost/config/config_docker.json team create --name "$BOT_TEAM" --display_name "$BOT_TEAM"
docker exec "$DOCKER_CONTAINER_NAME" mattermost -c /mm/mattermost/config/config_docker.json channel create --team "$BOT_TEAM" --name "$BOT_CHANNEL" --display_name "$BOT_CHANNEL"
docker exec "$DOCKER_CONTAINER_NAME" mattermost -c /mm/mattermost/config/config_docker.json channel create --team "$BOT_TEAM" --name "$BOT_PRIVATE_CHANNEL" --display_name "$BOT_PRIVATE_CHANNEL" --private
docker exec "$DOCKER_CONTAINER_NAME" mattermost -c /mm/mattermost/config/config_docker.json team add "$BOT_TEAM" "$TESTBOT_NAME" "$DRIVERBOT_NAME"
docker exec "$DOCKER_CONTAINER_NAME" mattermost -c /mm/mattermost/config/config_docker.json channel add  "$BOT_TEAM:$BOT_CHANNEL" "$TESTBOT_NAME" "$DRIVERBOT_NAME"
docker exec "$DOCKER_CONTAINER_NAME" mattermost -c /mm/mattermost/config/config_docker.json channel add  "$BOT_TEAM:$BOT_PRIVATE_CHANNEL" "$TESTBOT_NAME" "$DRIVERBOT_NAME"

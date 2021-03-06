FROM jneeven/mattermost-bot-test:new_tokens_14.02.2021
RUN mattermost -c /mm/mattermost/config/config_docker.json config set ServiceSettings.AllowedUntrustedInternalConnections "127.0.0.1 0.0.0.0 localhost ::1"

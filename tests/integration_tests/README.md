To locally run the integration test, first install `docker-compose` and then simply run `docker-compose up -d` from this folder.
The server will be available at `localhost:8065`, if you want to have a look at it.
The admin login is `admin@admin.com` with password `admin`.
Once the server is running, simply run `pytest . -n auto` to run the tests.
Once you're done, stop the server with `docker-compose down`.

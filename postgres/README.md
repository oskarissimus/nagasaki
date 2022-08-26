i decided to move db from nagasaki `docker-compose.yml` to its own `docker-compose.yml` because it is no longer so tightly coupled with nagasaki. There is another program - `websocket-logger` thas uses this db, thus db requires separation

**NOTE** it requires separate .env, so before running pleas provide it.

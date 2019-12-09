"""
## set up PostgreSQL docker container

```bash
mkdir -p $HOME/docker/volumes/postgres/pg_maintain_testing
```

start a docker postgresql container on PORT 5433
```bash
$ docker run -e POSTGRES_PASSWORD=postgres -d -p 5433:5432 -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data postgres:10-alpine

51255bf754f5bc487d155a69679dfb3344a6148c44baa24536b51da33b337db0
```

`-e` environment variable to pass to container

`-p` local:container port mapping

`-v` local:container filesystem mapping

`-d` detached / daemonized

`postgres:10-alpine` image:tag to create a container from

The successful execution will return an container ID  51255bf754f5****.
Container status can be check with:
```
$ docker container ls

CONTAINER ID        IMAGE                COMMAND                  CREATED             STATUS              PORTS                    NAMES
51255bf754f5        postgres:10-alpine   "docker-entrypoint.s…"   2 minutes ago       Up 2 minutes        0.0.0.0:5433->5432/tcp   agitated_poincare
```

Connect to the database in the container from psql:
```
$ psql -U postgres --port 5433 --host localhost

Password for user postgres:
psql (10.11 (Ubuntu 10.11-1.pgdg18.04+1))
Type "help" for help.
postgres=#
```

To exit command `\q`


## create the mdr database

Use the above command to enter psql shell and issue:
```SQL
CREATE DATABASE mdr;
```
On a second time the above routine simplifies to starting the stopped container
```
$ docker container start agitated_poincare
```

## Executing the tests
```bash
$ pytest tests --cov mdr --cov-branch -x -vv
```

optionally
```bash
$ coverage html
$ firefox htmlcov/index.html
```

### References

Source: https://hackernoon.com/dont-install-postgres-docker-pull-postgres-bee20e200198

"""

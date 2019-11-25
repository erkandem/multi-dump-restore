# multi dump-restore
*a wrapper around pg_dump/pg_restore focused on schema wise backups and restores*
* * * 


`⚠`️ **alpha** version, developed on linux, (C-)python 3.7, PostgreSQL 10.11

`⚠`️ don't pipe external arguments: unescaped `os.system()` call


### Summary
> todo: write me

### Sample Use Cases:
  - You have schemata which you would like to add to an other database.
    Renaming `testing_db` to `hot_spicy_db` won't do the trick because
    `hot_spicy_db` has already hot and spicy data in it.

  - You would like to be able to execute more granular restores

  - You prefer incremental backups over a large file due to resource limitation.

>`Note: Dumping a database as a whole is probably less vulnerable.`

### Getting Started
 1. clone/download/copy-paste to a folder
 2. set environment variables 
 3. take care of `.pgpass` (see [further reading / .pgpass](#pgpass))
 4. customize command template generation (optional)
 5. simulate a dump
 6. execute a dump
 7. simulate a restore
 8. execute a restore
 

#### Environment Variables
create or append these variables into your `.env` file.
Also, `USER` is requested, but `USER` should already be present.
```
PG_USER=
PG_PW=
PG_PORT=
PG_HOST=
```

#### Simulate a Dump:
```$ python multi_dump.py "/home/$USER/db/bkp" testing_db  schema_wise```

#### Execute the Commands
By default, all commands are going to be simply printed to the terminal.
If you are sure that the generated commands don't have a *smell*: 
 - call `multi_dump.py` / `multi_restore.py` with the `--armed` argument set to `True`.
     - `$ python multi_dump.py [...] --armed=True`
 - or pipe the commands in a file and execute the resulting file
    - `$ python multi_dump.py [...] > run.sh`
    - `$ chmod +x run.sh` 
    - `$ ./run.sh`

#### Simulate a Restore:
```$ python multi_restore.py "/home/$USER/db/bkp/20191123" testing_db hot_spicy_db```

#### `basic` Dump
In case you want a quick and easy single file backup of the complete database
 run the `multi_dump` with the `basic` parameter instead of the `schema_wise`. 
 `multi_restore` will skip this file, since the focus here is on schema wise backups.

```$ python multi_dump.py "/home/$USER/db/bkp" testing_db  basic```


### Behind the Curtains
#### Collecting the Schema Names
`multidump` will collect all schema names except `public` and those which are
related to postgres itself (`public` is added later explicitly)

```SQL
SELECT schema_name
FROM  information_schema.schemata
WHERE schema_name <> 'information_schema'
    AND schema_name <> 'public'
    AND schema_name NOT LIKE 'pg%%'
ORDER BY schema_name;
```

#### Resulting File Structure
below is a JSON dump of the dictionary returned by `multi_restore.restore_scouting`.
Obviously, this is the structure which will be created by `multi_dump`.
```json
{
  "testing_db": {
    "name": "testing_db",
    "bkp_name": "20191124",
    "path": "/home/hannibal/db/bkp/20191124/testing_db",
    "schemata": {
      "some_fancy_schema": {
        "name": "some_fancy_schema",
        "path": "/home/hannibal/db/bkp/20191124/testing_db/some_fancy_schema.backup"
      },
      "another_fancy_schema": {
        "name": "another_fancy_schema",
        "path": "/home/hannibal/db/bkp/20191124/testing_db/another_fancy_schema.backup"
      }
    }
  }
}
```

### A Word of Caution

![Caution. rick takes a dump](docs/static/take_a_dump.png) 

If the resulting backup files were never actually restored
you are likely to sit on a pile of dumps. 
 - test whether the `.backup` file can be restored
 - and the restored database passes some tests to prove that it is working
 - remove / delete the restored database afterwards. 
    that is exactly why source `backup_db_name` and target `restore_db_name`
    arguments are offered to you


### CLI Documentation
#### `multi_dump`
```bash
usage: multi_dump.py [-h] [--armed {True,False}]
                     backup_path db_name {schema_wise,basic}

positional arguments:
  backup_path           path to ALL backups e.g. /home/user/db/bkp
  db_name               name of database to dump
  {schema_wise,basic}   backup each schema in a separate file or the complete
                        database in one single

optional arguments:
  -h, --help            show this help message and exit
  --armed {True,False}  really execute commands? `False` by default
```
#### `multi_restore`
```bash
usage: multi_restore.py [-h] [--armed {True,False}]
                        single_backup_path backup_db_name restore_db_name

positional arguments:
  single_backup_path    path to ONE PARTICULAR backup e.g.
                        /home/user/db/bkp/20191123
  backup_db_name        database from which the schema was dropped
  restore_db_name       database to which the schema should be restored to

optional arguments:
  -h, --help            show this help message and exit
  --armed {True,False}  really execute commands? `False` by default
```

### Roadmap

 - add tests
   - dummy data generation
   - dummy pg database? docker? sth else?
 - tests for
    - OS [linux(x), mac, windows]
    - python version [3.6, 3.7(x), 3.8]
    - python implementation [cpython(x), pypy]
 - combine command code generation for `basic` with `schema_wise` dump
 - add basic doc strings until API and flow hardens
 - replace `os.system` anti-pattern with `subprocess`
   - replacement for `>>` needed 
 
### Further Reading:
> Devs have to get it right almost all the time.
Black hats only need to catch you once.

#### pg_dump docs
all command line options
[https://www.postgresql.org/docs/10/app-pgdump.html](https://www.postgresql.org/docs/10/app-pgdump.html)


#### pg_restore docs
all command line options
[https://www.postgresql.org/docs/10/app-pgrestore.html](https://www.postgresql.org/docs/10/app-pgrestore.html)

#### .pgpass docs
<a id="pgpass"></a>
`.pgpass` is needed to run `pg_restore` and `pg_dump` without typing passwords.
Passwords would be queried for **each** command.
[https://www.postgresql.org/docs/10/libpq-pgpass.html](https://www.postgresql.org/docs/10/libpq-pgpass.html)

#### avoid exposing 5432 on the server
Postgres is a powerful tool. Exposing it to the public is calling for trouble.
SSH into your server instead. 
[https://www.postgresql.org/docs/10/ssh-tunnels.html](https://www.postgresql.org/docs/10/ssh-tunnels.html)

#### other projects:

 - [abe-winter/pg13-py](https://github.com/abe-winter/pg13-py)  *fast(er) SQL mocking for python* 
 - [pg_diagramconvert](https://github.com/qweeze/pg_diagram) *convert schema to ER diagram* 
 - [akaihola/pgtricks](https://github.com/akaihola/pgtricks) kind of table wise backups via *pg_incremental_backup*
 - [gmr/pgdumplib](https://github.com/gmr/pgdumplib) *reading and writing binary backup files (custom)*
 - [tomyl/pg-dump-upsert](https://github.com/tomyl/pg-dump-upsert) *dump tables as `INSERT` statements with `ON CONFLICT` clause* 
 - [Jaymon/dump](https://github.com/Jaymon/dump)  *general pg_dump wrapper*


### Author:
 - License: MIT
 - Author Erkan Demiralay
 - Contact:  [erkan.dem@pm.me](mailto:erkan.dem@pm.me)
 - Repo: [https://github.com/erkandem/multi-dump-restore](https://github.com/erkandem/multi-dump-restore)


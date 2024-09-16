Copy .template files and remove .extension of the environment files in secrets/ and add the required information


API SECRET can be optained using
$ openssl rand -hex 32

GOOGLE ACCOUNT and GOOGLE APP PASSWORD can be obtained from the Google Account Security settings

POSTGRES HOST is "postgres", the name of the docker compose service

These commands must be run periodically, using something like cron:

sudo docker exec becycle-mx_postgres_1 psql -U becycleAdmin becycledb -c "delete from clientlogins where expirationdatetime<current_timestamp;"

sudo docker exec becycle-mx_postgres_1 psql -U becycleAdmin becycledb -c "delete from clientstemp where expirationdatetime<current_timestamp;"

with cron, this can be used to run the command every hour:
0 * * * *

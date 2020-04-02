# open-source-db-tools

Tools and Scripts to administer MySQL and other open source database systems

opensource-db-tools is a set of open source command line scripts like maatkit that will help database developers and administrators perform day-to-day database tasks easily and efficiently. In order to simplify the process of writing these scripts I have used gearman job server to distribute jobs across multiple workers (aka multiprocessing).

all-schemas:
all-schemas helps developers/administrators run multiple SQL statements on all/selected databases on a MySQL db server.

Example 1:
To SELECT all rows from all tables named t in all databases (except mysql, information_schema, d1):

python2.7 client_allschemas.py --user=<db username> --password=<db user password> --host=<db host or IP address> -e "SELECT * FROM dahi" "SELECT * FROM t" -i mysql information_schema d1

Output:
``` ------------------t5 - Returned/Affected = 1/1 ------------------ id 1

------------------test - Returned/Affected = 0/0 ------------------

------------------test - Returned/Affected = 4/4 ------------------ id None None None geeksww ```

Example 2:
The command below creates a new table test and inserts a new row in it in all databases except mysql, information_schema, and main.

sudo /opt/python-2.7/bin/python client_allschemas.py --user=admin --password=admin --host=127.0.0.1 -e "CREATE TABLE test (id INT(10), name VARCHAR(50))" "INSERT INTO test (id, name) VALUES (1, 'opensource-db-tools')" -i mysql information_schema main

You can SELECT rows in the new table in all databases mysql, information_schema, and main.

sudo /opt/python-2.7/bin/python client_allschemas.py --user=admin --password=admin --host=127.0.0.1 -e "SELECT * FROM test" -i mysql information_schema main ``` ------------------Db1 - Returned/Affected = 1/1 ------------------ id name 1 opensource-db-tools

------------------stage - Returned/Affected = 1/1 ------------------ id name 1 opensource-db-tools

------------------test - Returned/Affected = 1/1 ------------------ id name 1 opensource-db-tools

------------------tmp - Returned/Affected = 1/1 ------------------ id name 1 opensource-db-tools ```



$ python worker_allschemas.py -g localhost:4730 -d
Make sure the worker is running by executing the following command:

ps aux | grep worker_allschemas.py
Here is the output of worker_allschemas.py with -h option for help.

  -h, --help            show this help message and exit
  -g GEARMAN_SERVERS [GEARMAN_SERVERS ...], --gearman-servers GEARMAN_SERVERS [GEARMAN_SERVERS ...]
                        Gearman servers list. Default: ['localhost:4730']
  -d, --daemonize       Daemonizes this worker to run as a deamon in the
                        background and perform tasks for clients. Default:
                        False
  --version             show program's version number and exit
Now, you can run SQL statements on databases of your choice on a MySQL server. Here are a few examples:

$ python client_allschemas.py --user=<db username> --password=<db user password> --host=<db host or IP address> \
-e "SHOW tables" -i mysql information_schema
Put the actual database username, password, and hostname/ip in the command above. The command will output a list of all tables in all databases except mysql and information_schema databases. The output on my machine looks something like below.

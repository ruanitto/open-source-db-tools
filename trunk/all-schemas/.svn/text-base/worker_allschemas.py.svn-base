import MySQLdb, gearman, json, argparse, sys, daemon
import logging, logging.handlers, logging.config


def all_schemas(gearman_worker, gearman_job):
    global logging
    logging.debug("Entering into 'all_schemas' function")
    params = json.loads(gearman_job.data)
    server  = params["host"]
    user    = params["user"]
    port    = params["port"]
    password= params["password"]
    separator= params["separator"]
    database= params["db"]
    sql     = params["sql"]
    logging.info("Connecting with MySQL server using host:%s:%s, user:%s, password:<not shown>" % (server, str(port), user))
    try: conn = MySQLdb.connect(host=server, port=port, user=user, passwd=password, db=database)
    except MySQLdb.MySQLError:
        error_str = "Connection attempt using host:%s, port:%s, user:%s, password:<not shown> failed " % (hostname,str(port), cmd.user[0])
        logging.error(error_str)
        return error_str
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    res = dict()
    res["header"] = database
    res['error'] = "false"
    logging.debug("Running SQL on %s: %s" % (database, sql))
    try: cursor.execute(sql)
    except MySQLdb.MySQLError:
        res['error'] = "true"
        res["error_msg"] = str(sys.exc_info()[0])
        cursor.close()
        conn.close()
        return json.dumps(res)
    rows = cursor.fetchall()
    res["count"] = len(rows)
    res["affected_rows"] = conn.affected_rows()
    if res["count"] > 0:
        res["output"] = []
        res["output"].append(separator.join(rows[0].keys()))
        res["output"] = res["output"] + [separator.join([str(i) for i in row.values()]) for row in rows]
    cursor.close()
    conn.close()
    logging.debug("Returning following JSON string:\n%s" % res)
    return json.dumps(res)    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs SQL on all databases on a server.',epilog='')
    parser.add_argument('-g', '--gearman-servers',  action='store', nargs='+', default=['localhost:4730'],
                        help="Gearman servers list. Default: %(default)s", dest='gearman_servers')
    parser.add_argument('-d', '--daemonize',    action='store_const', const=True, default=False, dest='daemonize', 
                        help='Daemonizes this worker to run as a deamon in the background and perform tasks for clients. Default: %(default)s')
    parser.add_argument('--version',        action='version', version='%(prog)s 0.1a')

    cmd = parser.parse_args()
    logging.config.fileConfig("logging.conf")
    my_logger = logging.getLogger("mainModule")
    logging.debug("Program called with the following arguments:\n%s" % str(cmd))
    if cmd.daemonize:
        try: daemon.daemonize()
        except Error, DaemonException: print "Couldn't daemonize process"
    try: 
        logging.info("Connecting to gearman server(s)")
        gm_worker = gearman.GearmanWorker(cmd.gearman_servers)
        logging.info("Registering tasks with the server")
        gm_worker.register_task("all_schemas", all_schemas)
        logging.info("Entering the Gearman worker loop")
        gm_worker.work()
        logging.info("Worker is ready ..")
    except (gearman.errors, gearman.errors.ServerUnavailable):
        logging.error("Error connecting to Gearman server: " + str(sys.exc_info()[0]))
        exit(0)

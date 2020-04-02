import time, MySQLdb, gearman, json, argparse, os, sys
import logging, logging.handlers, logging.config


def check_request_status(job_request, unique_file_4_dbs, no_results_header):
    global cmd, logging
    if job_request.complete:
        logging.debug("Job %s completed!" % str(job_request))
        if job_request.result is None: return
        result = json.loads(job_request.result)
        logging.debug("Received following json string from worker:\n%s" % result)
        if result['error'] == "true": 
            output =  "------------------- %s ------------------\n%s" % (result['header'], result['error_msg'])
        else:
            if not no_results_header: 
                header = genHeader(result['header'], result['count'], result['affected_rows'])
            else: 
                header = ""
            output = ""
            try:
                for row in result['output']: output = output + "\n%s" % row
            except KeyError: pass
            output = header + output
        if unique_file_4_dbs:
            loc = os.path.join(cmd.output_dir[0], result['header'])
            logging.info("Outputting data in %s" % loc)
            f = open(loc, 'a+')
            f.write(output + "\n")
            f.close()
        else:
            print ""
            print output
    elif job_request.timed_out: logging.error("Job %s timed out!" % str(job_request))
    elif job_request.state == JOB_UNKNOWN: logging.error("Job %s connection failed!" % str(job_request))


def genHeader(header, count, affected):
    return "------------------%s - Returned/Affected = %s/%s ------------------" % (str(header), str(count), str(affected))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs SQL on all databases on a server.', 
	                             epilog='')
    parser.add_argument('-u', '--user',     action='store', nargs=1, required=True,
                        help="MySQL user to use for accessing the database. Default: %(default)s", dest='user')
    parser.add_argument('-p', '--password', action='store', nargs=1, required=True,
                        help="Password for MySQL database user. Default: %(default)s", dest='password')
    parser.add_argument('-g', '--gearman-servers',  action='store', nargs='+', default=['localhost:4730'],
                        help="Gearman servers list. Default: %(default)s", dest='gearman_servers')
    parser.add_argument('-e', '--execute',  action='store', nargs='+', required=True,
                        help="SQL/Command to be executed. Default: %(default)s", dest='command')
    parser.add_argument('--host', action='store', nargs=1, default=['localhost'],
	                help="MySQL database server hostname or ip address. Default: '%(default)s'", dest='host')
    parser.add_argument('-P', '--port',     action='store', nargs=1, default=[3306], type=int,
	                help="MySQL database server port no. that the server is listening to. Default: '%(default)s'", dest='port')
    parser.add_argument('-f', '--fields-separator',     action='store', nargs=1, default=['\t'],
                        help="Feilds in the resultsets are separated by this character. Default: 'tab delimited'", dest='fields_separator')
    parser.add_argument('-d', '--dry-run',  action='store_const', const=True, default=False, help='No-act', dest='dry_run')
    parser.add_argument('--version',        action='version', version='%(prog)s 0.1a')
    parser.add_argument('--unique-files-per-database', action='store_const', const=True, default=False, dest='unique_file_4_dbs',
                        help="Creates or appends to(if already exists) a unique output file for each database. Default: '%(default)s'")
    parser.add_argument('--no-results-header', action='store_const', const=True, default=False, dest='no_results_header')
    parser.add_argument('-i', '--ignore-databases',  action='store', nargs='*', required=False,
                        help="Ignore these databases (space separated list). Default: %(default)s", dest='ignore_dbs')
    parser.add_argument('--include-dbs',   action='store', nargs=1, dest='include_dbs', default='%',
                        help="Includes only databases that match the pattern (follows MySQL string pattern matching). Default: %(default)s")
    parser.add_argument('-o', '--output-dir',   action='store', nargs=1, default='.' + os.sep,
                        help="The output directory where results will be stored. Default: '%(default)s'", dest='output_dir')
    start = time.clock()
    cmd = parser.parse_args()
    hostname = cmd.host[0]
    if not os.access(cmd.output_dir[0], os.W_OK):
        print "No write permissions to " + cmd.output_dir[0]
        exit(0)
    logging.config.fileConfig("logging.conf")
    my_logger = logging.getLogger("mainModule")
    logging.debug("Program called with the following arguments:\n%s" % str(cmd))
    try:
        logging.info("Connecting to gearman server(s)")
        gm_client = gearman.GearmanClient(cmd.gearman_servers)
        logging.info("Connected to Gearman job server successfully ..")
    except (gearman.errors, gearman.errors.ServerUnavailable):
        logging.error("Error connecting to Gearman server: " + str(sys.exc_info()[0]))
        exit(0)
    sql = "SHOW DATABASES LIKE '%s'" %  cmd.include_dbs[0]
    try: conn = MySQLdb.connect(host=hostname, port=cmd.port[0], user=cmd.user[0], passwd=cmd.password[0], db="mysql")
    except MySQLdb.MySQLError:
        logging.error("Connection attempt using host:%s, user:%s,password:%s failed " % (hostname,cmd.user[0],cmd.password[0]))
        exit(0)
    cursor = conn.cursor()
    logging.debug("Running SQL: %s" % sql)
    cursor.execute("""SHOW DATABASES LIKE %s""", (cmd.include_dbs[0]))
    rows = cursor.fetchall()
    dbs_worked_on = 0
    dbs_ignored = 0
    list_of_jobs = []
    for sql_in in cmd.command:
        for row in rows:
            try: 
                temp = cmd.ignore_dbs.index(row[0])
                logging.debug("Ignored database: %s" % row[0])
                dbs_ignored += 1
                continue
            except (ValueError, AttributeError):
                temp = ""
                logging.debug("Working on database: %s" % row[0])
                dbs_worked_on += 1
            task = "all_schemas"
            if cmd.dry_run:
                print "-------------------------%s-----------------" % row[0]
                print sql_in
            else:
                param = json.dumps(dict(host=hostname, port=cmd.port[0], user=cmd.user[0], password=cmd.password[0], db=row[0], sql=sql_in, separator=cmd.fields_separator[0]))
                logging.debug("Submitting to job server with function '%s' with parameters %s." % ("all_schemas", str(param)))
                list_of_jobs.append(dict(task="all_schemas", data=param))
    cursor.close()
    conn.close()
    if cmd.dry_run: exit(0)
    try:
        submitted_requests = gm_client.submit_multiple_jobs(list_of_jobs, background=False, wait_until_complete=False)
        completed_requests = gm_client.wait_until_jobs_completed(submitted_requests, poll_timeout=5.0)
    except (gearman.errors, gearman.errors.ServerUnavailable):
        logging.error("Error connecting to Gearman server: " + str(sys.exc_info()[0]))        
        exit(0)
    time.sleep(1.0)
    for completed_job_request in completed_requests:
        check_request_status(completed_job_request, cmd.unique_file_4_dbs, cmd.no_results_header)
    logging.info("Took %s seconds to process %s databases, ignored %s databases, and ran %s queries on each database processed" % (str(time.clock() - start), dbs_worked_on/len(cmd.command), str(dbs_ignored/len(cmd.command)), str(len(cmd.command))))

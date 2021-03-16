#!/bin/bash
gearmand -d
# __run_supervisor() {
#     echo "Running the run_supervisor function."
#     supervisord -n
# }

# # Call all functions
# __run_supervisor
python2.7 worker_allschemas.py

tail -F output.log
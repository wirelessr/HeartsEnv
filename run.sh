#!/bin/bash
/usr/local/bin/jupyter notebook --no-browser --ip 0.0.0.0 --allow-root --NotebookApp.token='' --port 8888 /hearts/demo &
/usr/bin/supervisord -c /etc/supervisor/supervisord.conf &
#!/bin/sh

# crontab -e 
# * * * * * /home/pixel_dev/dqm/bash/cron_jobs.sh

/home/pixel_dev/dqm/python/dqm.py 
/home/pixel_dev/dqm/python/ful.py

if [ $(pgrep chk_data_int | wc -w) -lt 1 ]; then 
    /home/pixel_dev/dqm/python/chk_data_integrity 
fi


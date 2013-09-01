#!/bin/sh
# Usage: 
# crontab -e 
# * * * * * /home/pixel_dev/dqm/bash/cron_jobs.sh

/home/pixel_dev/dqm/python/dqm.py 

/home/pixel_dev/dqm/python/ful.py

/home/pixel_dev/dqm/python/chk_data_integrity 


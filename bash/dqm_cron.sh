#!/bin/sh

# crontab -e 
# * * * * * /home/pixel_dev/dqm/bash/dqm_cron.sh

/home/pixel_dev/dqm/python/dqm.py update_db
/home/pixel_dev/dqm/python/dqm.py ln_runs 

/home/pixel_dev/dqm/python/dqm.py chk_dat 

/home/pixel_dev/dqm/python/dqm.py pub_dqm
/home/pixel_dev/dqm/python/dqm.py pub_ful
/home/pixel_dev/dqm/python/dqm.py pub_dat 

if [ $(pgrep Marlin | wc -w) -lt 3 ]; then 
    /home/pixel_dev/dqm/python/dqm.py eut_dqm
fi


if [ $(pgrep Marlin | wc -w) -lt 2 ]; then 
    /home/pixel_dev/dqm/python/dqm.py eut_ful 
fi


if [ $(pgrep chk_data_int | wc -w) -lt 1 ]; then 
    /home/pixel_dev/dqm/python/chk_data_integrity 
fi





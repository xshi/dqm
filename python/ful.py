#!/usr/bin/env python
"""
Main script DQM 

"""

__author__ = "Xin Shi <Xin.Shi@cern.ch>"

import sys
import os 
from dqm import (is_valid_run_str, get_range_from_str, 
                 get_env_file, source_bash, touch_file, 
                 proc_cmd, check_raw_file, run_contains_file,
                 get_valid_runs, num_of_process, get_range_from_str
                 )
import ful 


dataset = 'PSI2013'
MAX_MARLIN_JOBS = 2  

if dataset == 'PSI2013':
    daq_pc = 'pixel_dev@pcpixeltb'
    daqdir = '/home/pixel_dev/PSI2013Data/incoming'
    begin_valid_run = 20001
    end_valid_run = 50001 

    datadir = '/home/pixel_dev/PSI2013Data/data'
    dbname = 'run_list.db'
    dbpath = '/home/pixel_dev/PSI2013Data'
else:
    raise NameError(dataset)


def main():
    args = sys.argv[1:]

    if len(args) == 0: 
        runs = get_valid_new_ful_runs()
    else:
        runs = get_range_from_str(args[0])

    force = False 
    if len(runs) == 1: 
        force = True 

    for run in runs:
        eut_ful(run) # force only be done by reset_ful
        pub_ful(run, force=force)


def eut_ful(run, force=False):
    if not force and run_contains_file(run, '.begin_eut_ful'):
        return
        
    if not force and run_contains_file(run, '.end_eut_ful'):
        return 

    if num_of_process('Marlin') > MAX_MARLIN_JOBS:
        sys.stdout.write(
            'Number of running Marlin jobs is larger than %s !\n'
            % MAX_MARLIN_JOBS)
        return

    env_file = get_env_file(run)
    procenv = source_bash(env_file)
    procdir = procenv['simplesub']
 
    modes = ["fullconvert", "clustering", "hits"]#, "tracks_noalign"]

    check_raw_file(procdir, run)
    touch_file(run, '.begin_eut_ful')
    
    for mode in modes:
        sys.stdout.write('[eut_ful] %s run %s ... ' %  (mode, run))
        sys.stdout.flush()
        cmd = 'python config-cmspixel.py -a %s %s ' % (mode, run)
        output = proc_cmd(cmd, procdir=procdir, env=procenv)
        sys.stdout.write('OK.\n')

    touch_file(run, '.end_eut_ful')


def pub_ful(run, force=False):
    if not force and run_contains_file(run, '.begin_pub_ful'):
        return

    if not force and run_contains_file(run, '.end_pub_ful'):
        return 
        
    sys.stdout.write('[pub_ful] run %s ... ' % run)
    sys.stdout.flush()
        
    cmd = 'dqm data/%s' %run
    
    env_file = get_env_file(run)
    procenv = source_bash(env_file)
    procdir = os.path.join(procenv['simplesub'], 'CMSPixel')

    touch_file(run, '.begin_pub_ful')
    output = proc_cmd(cmd, procdir=procdir, env=procenv)
    sys.stdout.write(' OK.\n')
    touch_file(run, '.end_pub_ful')


def get_valid_new_ful_runs():
    new_runs = []
    runs = get_valid_runs()
    for run in runs:
        if ( run_contains_file(run, '.end_eut_ful') and
             run_contains_file(run, '.end_pub_ful')):
            continue
    return new_runs
            

if __name__ == '__main__':
    main()



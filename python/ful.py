#!/usr/bin/env python
"""
Main script DQM 

"""

__author__ = "Xin Shi <Xin.Shi@cern.ch>"

import sys
import os 
from dqm import (is_valid_run_str, get_range_from_str, 
                 get_env_file, source_bash, touch_file, 
                 proc_cmd, check_raw_file, run_contains_file
                 )
import ful 


dataset = 'PSI2013'

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
    if len(args) == 0 or len(args) == 1:
        return default(args)

    function = getattr(ful, args[0])
    return function(args[1:])


def default(args):
    new_runs = eut_ful_runs(args)

    for run in new_runs:
        eut_ful([run])
        pub_ful([run])


def eut_ful(runs, force=False):
    new_runs = eut_ful_runs(runs)
    for run in new_runs:
        if not force and run_contains_file(run, '.begin_eut_ful'):
            continue

        if not force and run_contains_file(run, '.end_eut_ful'):
            continue
        
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


def pub_ful(runs, force=False):
    new_runs = pub_ful_runs(runs)
    if len(new_runs) == 1:
        force = True

    for run in new_runs:
        if not force and run_contains_file(run, '.begin_pub_ful'):
            continue

        if not force and run_contains_file(run, '.end_pub_ful'):
            continue
        
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


def eut_ful_runs(runs):
    if len(runs) == 1:
        return get_range_from_str(runs[0])        

    new_runs = []
    for root, dirs, files in os.walk(datadir):
        if len(dirs) != 0:
            continue # bypass single files in the datadir
        
        if len(files) == 0: #bypass the empty runs or single file
            continue

        run = root.split('/')[-1]
        if not run.isdigit():
            continue 
        
        if int(run) < begin_valid_run or int(run) > end_valid_run:
            continue
        
        if '.begin_eut_ful' in files:
            continue
                
        if '.end_eut_ful' in files:
            continue

        new_runs.append(run)

    new_runs.sort()
    return new_runs
                


def pub_ful_runs(runs):
    if len(runs) == 1:
        return get_range_from_str(runs[0])        

    new_runs = []
    for root, dirs, files in os.walk(datadir):
        if len(dirs) != 0: 
            continue # bypass single files in the datadir  
        if len(files) == 0: #bypass the empty runs or single file
            continue

        run = root.split('/')[-1]
        if not run.isdigit():
            continue
        
        if int(run) < begin_valid_run or int(run) > end_valid_run:
            continue
             
        if '.end_eut_ful' not in files:
            continue
        
        if '.end_pub_ful' in files:
            continue

        new_runs.append(run)

    return new_runs




if __name__ == '__main__':
    main()



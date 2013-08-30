#!/usr/bin/env python
"""
Main script DQM 

"""

__author__ = "Xin Shi <Xin.Shi@cern.ch>"


import sys
import os 
import shutil
import subprocess
import filecmp
import time 
from datetime import datetime, timedelta 
import dqm

if hasattr(datetime, 'strptime'):
    strptime = datetime.strptime
else:
    strptime = lambda date_string, format: datetime(
        *(time.strptime(date_string, format)[0:6]))
try:
    import json
except ImportError:
    import simplejson as json


dataset = 'PSI2013'

if dataset == '2012A':
    begin_valid_run = 120
    datadir = '/home/pixel_dev/TB2012Data/data/'
    dbname = 'run_list.db'
    dbpath = '/home/pixel_dev/TB2012Data'
    daq_pc = 'cmspixel@heplnw044'
    daqdir = '/data/'
    
elif dataset == '2012B':
    daq_pc = 'pixel_dev@pcpixeltb'
    daqdir = '/home/pixel_dev/data/2012B'
    begin_valid_run = 15280

    datadir = '/home/pixel_dev/TB2012B_Data/data'
    dbname = 'run_list.db'
    dbpath = '/home/pixel_dev/TB2012B_Data'

elif dataset == 'Xray2013':
    daq_pc = 'pixel_dev@pcpixeltb'
    daqdir = '/home/pixel_dev/tmp'
    begin_valid_run = 18001 

    datadir = '/home/pixel_dev/Xray2013Data/data'
    dbname = 'run_list.db'
    dbpath = '/home/pixel_dev/Xray2013Data'

elif dataset == 'PSI2013':
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
    function = getattr(dqm, args[0])
    return function(args[1:])

def update_db(args):
    cmd = 'ls %s' % daqdir

    output = proc_cmd(cmd)
    runs = get_runs_from_ls(output)

    dbfile = check_and_join(dbpath, dbname)    
    db = open(dbfile, 'w')
    json.dump(runs, db)
    db.close()

    check_update_status(dbfile)

def cp_runs(fn=False):
    dbfile = check_and_join(dbpath, dbname)
    db = open(dbfile)
    runs = json.load(db)
    db.close()

    local_runs = get_valid_runs()

    remote_runs = runs.keys()
    remote_runs.sort()

    if not fn:
        # Leave the last run not copy until finished. 
        remote_runs = remote_runs[:-1]

    new_runs = []
    for run in remote_runs:
        if run not in local_runs:
            new_runs.append(run)


    if len(new_runs) == 0:
        sys.stdout.write('All runs are updated. \n')
        return
    
    sys.stdout.write('Updating %s runs ... \n' %len(new_runs))
    for run in new_runs:
        sys.stdout.write('run %s ... ' % run)
        sys.stdout.flush()
        rundir = os.path.join(datadir, run)
        check_and_join(rundir)

        filename = runs[run]
        cmd = "scp  %s:%s/%s %s/" %(daq_pc, daqdir, filename, rundir)
        output = proc_cmd(cmd) 
        sys.stdout.write(' OK.\n')


def ln_runs(args):
    dbfile = check_and_join(dbpath, dbname)
    db = open(dbfile)
    runs = json.load(db)
    db.close()

    local_runs = get_valid_runs()
    remote_runs = runs.keys()
    remote_runs.sort()

    new_runs = []
    for run in remote_runs:
        if run not in local_runs:
            new_runs.append(run)

    if len(new_runs) == 0:
        sys.stdout.write('All runs are updated. \n')
        return
    
    sys.stdout.write('Updating %s runs ... \n' %len(new_runs))
    for run in new_runs:
        sys.stdout.write('run %s ... ' % run)
        sys.stdout.flush()
        rundir = os.path.join(datadir, run)
        check_and_join(rundir)

        filenames = runs[run]
        for filename in filenames: 
            cmd = "ln -sf %s/%s %s/." %(daqdir, filename, rundir)
            output = proc_cmd(cmd) 

        sys.stdout.write(' OK.\n')


def eut_dqm(runs, force=False):
    if len(runs) == 0:
        new_runs = eut_dqm_runs(datadir)    
        new_runs.sort()

    elif len(runs) == 1:
        new_runs = get_range_from_str(runs[0])        

    else:
        new_runs = runs

    if len(new_runs) == 1:
        force = True
    
    for run in new_runs:
        if not force and run_contains_file(run, '.begin_eut_dqm'):
            continue

        if not force and run_contains_file(run, '.end_eut_dqm'):
            continue

        env_file = get_env_file(run)
        procenv = source_bash(env_file)
        procdir = procenv['simplesub']

        #modes = ["fullconvert", "clustering", "hits", "tracks_noalign"]
        modes = ["fullconvert", "clustering", "hits"]        

        check_raw_file(procdir, run)
        touch_file(run, '.begin_eut_dqm')

        for mode in modes:
            sys.stdout.write('[eut_dqm] %s run %s ... ' %  (mode, run))
            sys.stdout.flush()
            
            cmd = 'python config-cmspixel-dqm.py -a %s %s ' % (mode, run)
            output = proc_cmd(cmd, procdir=procdir, env=procenv)

            sys.stdout.write('OK.\n')

        touch_file(run, '.end_eut_dqm')


def eut_ful(runs):
    force = False
    
    if len(runs) == 0:
        new_runs = eut_ful_runs(datadir)    
        new_runs.sort()
    elif len(runs) == 1:
        new_runs = get_range_from_str(runs[0])        
    else:
        new_runs = runs

    if len(new_runs) == 1:
        force = True

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
    


def pub_dqm(runs=[], fn=False, force=False):
    if len(runs) == 0:
        new_runs = pub_dqm_runs(runs, fn=fn, force=force)
        new_runs.sort()

    elif len(runs) == 1:
        new_runs = get_range_from_str(runs[0])        

    else:
        new_runs = runs
    
    if len(new_runs) == 0:
        sys.stdout.write('[pub_dqm] no new run to process. \n')
        return

    if len(new_runs) == 1:
        force = True

    #sys.stdout.write('[pub_dqm] Updating %s runs ... \n' %len(new_runs))
    for run in new_runs:
        
        if not force and run_contains_file(run, '.begin_pub_dqm'):
            continue

        if not force and run_contains_file(run, '.end_pub_dqm'):
            continue

        sys.stdout.write('[pub_dqm] run %s ... ' % run)
        sys.stdout.flush()
        
        cmd = 'dqm data/%s' %run
 
        env_file = get_env_file(run)
        procenv = source_bash(env_file)
        #procdir = procenv['simplesub']
        #procdir = os.path.join(os.environ['simplesub'], 'CMSPixel')
        procdir = os.path.join(procenv['simplesub'], 'CMSPixel')

        touch_file(run, '.begin_pub_dqm')
        output = proc_cmd(cmd, procdir=procdir, env=procenv)
        sys.stdout.write(' OK.\n')
        touch_file(run, '.end_pub_dqm')


def pub_ful(runs=[]):
    new_runs = pub_ful_runs(runs)

    force = False 
    if len(new_runs) == 0:
        sys.stdout.write('[pub_ful] no new run to process. \n')
        return

    if len(new_runs) == 1:
        force = True

    #sys.stdout.write('[pub_ful] Updating %s runs ... \n' %len(new_runs))
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
        #procdir = procenv['simplesub']
        #procdir = os.path.join(os.environ['simplesub'], 'CMSPixel')
        
        procdir = os.path.join(procenv['simplesub'], 'CMSPixel')

        touch_file(run, '.begin_pub_ful')
        output = proc_cmd(cmd, procdir=procdir, env=procenv)
        sys.stdout.write(' OK.\n')
        touch_file(run, '.end_pub_ful')

def pub_data_integrity(runs=[]):
    new_runs = pub_data_integrity_runs(runs)
    force = False 
    if len(new_runs) == 0:
        return

    if len(new_runs) == 1:
        force = True

    for run in new_runs:
        if not force and run_contains_file(run, '.begin_pub_data_integrity'):
            continue

        if not force and run_contains_file(run, '.end_pub_data_integrity'):
            continue
        
        sys.stdout.write('[pub_data_integrity] run %s ... ' % run)
        sys.stdout.flush()
        
        cmd = 'dqm data/%s' %run
        procdir = os.path.join(os.environ['simplesub'], 'CMSPixel')

        touch_file(run, '.begin_pub_data_integrity')
        output = proc_cmd(cmd, procdir=procdir)
        sys.stdout.write(' OK.\n')
        touch_file(run, '.end_pub_data_integrity')


def chk_dqm(runs):
    sys.stdout.write('Checking for runs: '+ ', '.join(runs) +'...\n')
    runs = [r.zfill(6) for r in runs]

    update_db()
    cp_runs()
    eut_dqm(runs)

    pub_dqm(runs, force=True)

    sys.stdout.write('\nPlease check the webpage for runs: '+ ', '.join(runs)+'\n')
    sys.stdout.write('--------------------------------------\n')
    sys.stdout.write('http://ntucms1.cern.ch/pixel_dev/dqm/ \n')
    sys.stdout.write('--------------------------------------\n')


def fin_dqm():
    update_db()
    cp_runs(fn=True)
    eut_dqm()
    pub_dqm(runs=[], fn=True)


def ana_dqm(args):
    filename = args[0]
    runs = get_runs_from_file(filename)
    force_eut = False
    force_pub = False
    if '-feut' in args:
        force_eut = True 
    if '-fpub' in args:
        force_pub = True 
    for run in runs:
        eut_dqm([run], force=force_eut)
        pub_dqm([run], force=force_pub)


def batch_touch(arg):
    fname = arg[0]
    runs = arg[1:]
    
    if len(runs) == 0:
        new_runs = get_valid_runs()
        new_runs.sort()
    elif len(runs) == 1:
        new_runs = get_range_from_str(runs[0])        
    else:
        new_runs = runs

    for run in new_runs:
        sys.stdout.write('[touch file] run %s, %s ... ' % (run, fname))
        sys.stdout.flush()
        touch_file(run, fname)
        sys.stdout.write(' OK.\n')        


def batch_rm(arg):
    fname = arg[0]
    runs = arg[1:]
    
    if len(runs) == 0:
        new_runs = find_runs_contain(fname) 
        new_runs.sort()
    elif len(runs) == 1:
        new_runs = get_range_from_str(runs[0])        
    else:
        new_runs = runs

    for run in new_runs:
        sys.stdout.write('[clean file] run %s, %s ... ' % (run, fname))
        sys.stdout.flush()
        
        file_ = os.path.join(datadir, run, fname)
        os.remove(file_)
        sys.stdout.write(' OK.\n')        


def batch_mv(arg):
    fname = arg[0]
    pubdir = os.environ['TARGETDIRECTORY']
    runs = arg[1:]
    
    if len(runs) == 0:
        new_runs = find_runs_contain(fname) 
        new_runs.sort()
    elif len(runs) == 1:
        new_runs = get_range_from_str(runs[0])        
    else:
        new_runs = runs

    for run in new_runs:
        sys.stdout.write('[mv file] run %s, %s ... ' % (run, fname))
        sys.stdout.flush()

        src = os.path.join(datadir, run, fname)
        dst = os.path.join(pubdir, 'data_'+run, fname)
        shutil.move(src, dst)

        sys.stdout.write(' OK.\n')        


# ------------------------------------------------------------
# Supporting Functions 
# ------------------------------------------------------------
def make_tmpfile(f):
    path, name = os.path.split(f)
    tmpname = '.tmp_' + name
    tmpfile = os.path.join(path, tmpname)
    return tmpfile
    
def check_and_join(filepath, filename=None):
    if not os.access(filepath, os.F_OK):
        sys.stdout.write('Creating dir %s ...' % filepath)
        os.makedirs(filepath)
        os.chmod(filepath, 0777)
        sys.stdout.write(' OK.\n')

    if filename == None:
        return
    
    file_ = os.path.join(filepath, filename)
    if os.access(file_, os.F_OK) :
        tmpfile = make_tmpfile(file_)
        shutil.copy2(file_, tmpfile)
    return file_


def proc_cmd(cmd, test=False, verbose=1, procdir=None, env=None):
    if test:
        sys.stdout.write(cmd+'\n')
        return 

    cwd = os.getcwd()
    if procdir != None:
        os.chdir(procdir)

    if env is None:
        env = os.environ()

    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE,
                               env=env)
    process.wait()
    stdout = process.communicate()[0]
    if 'error' in stdout:
        sys.stdout.write(stdout)
    if procdir != None:
        os.chdir(cwd)
    return stdout


def check_update_status(f, verbose=1):
    tmpfile = make_tmpfile(f)
    if not os.access(tmpfile, os.F_OK):
        message = 'created %s ...\n' %f
        shutil.copy2(f, tmpfile)
    elif filecmp.cmp(f, tmpfile, shallow=False):
        message = 'up-to-date: %s\n' % f
    else:
        message = 'updated %s ...\n' %f
    if verbose > 0 :
        sys.stdout.write(message)
    return message


def eut_dqm_runs(datadir):
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

        if '.begin_eut_dqm' in files:
            continue

        if '.end_eut_dqm' in files:
            continue
        
        new_runs.append(run)

    return new_runs


def eut_ful_runs(datadir):
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
                    
    return new_runs
                
                
                
def pub_dqm_runs(runs, fn=False, force=False):
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
             
        if '.end_eut_dqm' not in files:
            continue

        if '.end_pub_dqm' in files:
            continue

        new_runs.append(run)
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

def pub_data_integrity_runs(runs):
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
             
        if '.end_chk_data_integrity' not in files:
            continue
        
        if '.end_pub_data_integrity' in files:
            continue

        new_runs.append(run)

    new_runs.sort()
    return new_runs


def find_runs_contain(fname):
    new_runs = []
    for root, dirs, files in os.walk(datadir):
        if len(dirs) != 0: 
            continue # bypass single files in the datadir  
        run = root.split('/')[-1]

        if fname in files:
            new_runs.append(run)
    return new_runs


def get_valid_runs():
    new_runs = []
    for root, dirs, files in os.walk(datadir):
        if len(dirs) != 0: 
            continue # bypass single files in the datadir  
        run = root.split('/')[-1]

        if not run.isdigit():
            continue
        
        if int(run) < begin_valid_run or int(run) > end_valid_run:
            continue
        new_runs.append(run)

    new_runs.sort()
    return new_runs


def get_runs_from_ls(output):
    runs = {}
    for line in output.split():
        items = line.split('_')
        if len(items) < 3:
            continue

        board = items[0]
        spill = items[2]            

        file = line
        if not is_stable_file(file):
            continue

        run = spill.zfill(6)
        if not run.isdigit():
            continue
        
        if int(run) < begin_valid_run or int(run) > end_valid_run:
            continue
 
        if not runs.has_key(run):
            runs[run] = [file]
        else:
            existing_files = runs[run]
            for ef in existing_files:
                eb = ef.split('_')[0]
                if eb != board:
                    runs[run].append(file)

    return runs


def is_stable_file(filename):
    f = os.path.join(daqdir, filename)
    then = time.ctime(os.path.getmtime(f))
    then = strptime(then, "%a %b %d %H:%M:%S %Y")
    now = datetime.now()
    tdelta = now - then
    min_tdelta = timedelta(minutes=2)
    return tdelta > min_tdelta


def check_raw_file(procdir, run):
    filedir = os.path.join(procdir, 'CMSPixel/data', run)
    cwd = os.getcwd()
    os.chdir(filedir)
    for root, dirs, files in os.walk(filedir):
        if 'mtb.bin' in files:
            return 

        for f in files:
            if '.dat' in f:
                datfile = f
                os.symlink(datfile, 'mtb.bin')
                
    os.chdir(cwd)


def get_runs_from_file(filename): 
    runs = [] 
    fi = open(filename, 'r')
    for line in fi:
        run = line.strip()
        runs.append(run)
    fi.close()
    return runs


def get_files_from_ls(output, good_files_start):
    files = []
    for line in output.split():
        filename = line
        items = filename.split('__') 
        if len(items) < 2: 
            continue
        
        timestr = '__'.join(items).replace('.dat', '')
        print time.strptime(timestr, "_%Y_%m_%d__%Hh%Mm%Ss")
        
        sys.exit()
        files.append(filename)

    return files 


def get_range_from_str(val, start=0, stop=None):
    if val == 'all' :
        return val

    def get_range_hypen(val):
        start = int(val.split('-')[0])
        tmp_stop = val.split('-')[1]
        if tmp_stop != '':
            stop = int(val.split('-')[1])+1
        return range(start, stop)

    result = []

    if '-' in val and ',' not in val:
        result = get_range_hypen(val)
        
    elif ',' in val:
        items = val.split(',')
        for item in items:
            if '-' in item:
                result.extend(get_range_hypen(item))
            else:
                result.append(int(item))
    else:
        result.append(int(val))

    result = [ str(r).zfill(6) for r in result ]
    return result


def touch_file(run, fname): 
    f = os.path.join(datadir, run, fname)
    open(f, 'a').close()
    

def run_contains_file(run, f):
    rundir = os.path.join(datadir, run)
    for root, dirs, files in os.walk(rundir):
        if f in files:
            return True
    return False
     
def run_contains_file_pattern(run, pat):
    rundir = os.path.join(datadir, run)
    for root, dirs, files in os.walk(rundir):
        for f in files:
            if pat in f:
                return True
    return False

def source_bash(f):
    pipe = subprocess.Popen(". %s; env" % f, stdout=subprocess.PIPE,
                            shell=True)
    output = pipe.communicate()[0]
    env = dict((line.split("=", 1) for line in output.splitlines()))
    return env 


def get_env_file(run):
    env_file = '/home/pixel_dev/scripts/dqm_env.sh'
    if run_contains_file_pattern(run, 'TestBoard2'): 
        env_file = '/home/pixel_dev/scripts/dqm_env_v0.sh'

    return env_file

 


if __name__ == '__main__':
    main()



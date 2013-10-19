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
import HTML
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

from Decoder_dqm import Decoder 

dataset = 'FNAL2013'
#debug = False 
debug = True 

MAX_MARLIN_JOBS = 3

if dataset == 'FNAL2013':
    env_file = '/afs/cern.ch/cms/Tracker/Pixel/HRbeamtest/dqm/v3/setup.sh' 
    daqdir = '/eos/cms/store/cmst3/group/tracktb/FNAL2013'
    eos="/afs/cern.ch/project/eos/installation/0.2.31/bin/eos.select"
    begin_valid_run = 30001
    end_valid_run = 50001 

    datadir = '/afs/cern.ch/cms/Tracker/Pixel/HRbeamtest/data/FNAL2013/'
    dbname = 'run_list.db'
    dbpath = datadir 
    histdir = '/afs/cern.ch/cms/Tracker/Pixel/HRbeamtest/jobsub/v1/histograms'

else:
    raise NameError(dataset)


def main():
    args = sys.argv[1:]
    if len(args) == 0 :
        return usage()

    if ( len(args) == 1 and 
         args[0] == 'default' ):
        return default()

    if ( len(args) == 1 and 
         is_valid_run_str(args[0]) ):
        return default(args[0])

    function = getattr(dqm, args[0])
    return function(args[1:])


def usage():
    sys.stdout.write('''
NAME
    dqm.py (v3) 


SYNOPSIS
    dqm.py default 
           run the default procedure (eut_dqm, chk_dat, pub_dqm)

    dqm.py 30301
           only for run 20301

    dqm.py 30301-30350
           run the range between 30301-30350


AUTHOR
    Written by Xin Shi.


REPORTING BUGS
    Report bugs to <Xin.Shi@cern.ch>.


DATE
    October 2013 

\n''')


def default(arg=None):
    update_db()
    if arg is None:
        runs = get_valid_new_runs()
    else:
        runs = get_range_from_str(arg)

    force = False 
    if len(runs) == 1: 
        force = True 

    for run in runs:
        cp_dat(run)
        board = eut_dqm(run, force=force)
        chk_dat(board, run, force=force)
        pub_dqm(board, run, force=force)
        rm_dat(run)       

    index(board)


def update_db():
    cmd = '%s ls %s' % (eos, daqdir)
    output = proc_cmd(cmd)
    
    runs = get_runs_from_ls(output)

    dbfile = check_and_join(dbpath, dbname)    
    db = open(dbfile, 'w')
    json.dump(runs, db)
    db.close()

    check_update_status(dbfile)


def cp_dat(run):
    dstdir = get_rundir(run) 

    cmd = "mkdir -p %s" % dstdir 
    proc_cmd(cmd)
    datfile = get_datfile(run)

    for df in datfile:
        cmd = '%s cp %s/%s/%s %s/' %(eos, daqdir, run, df, dstdir)
        output = proc_cmd(cmd)
        if debug:
            print cmd 
            print output 


def rm_dat(run):
    #filedir = os.path.join(datadir, run)
    filedir = get_rundir(run)

    cwd = os.getcwd()
    os.chdir(filedir)
    for root, dirs, files in os.walk(filedir):
        for f in files:
            if '.dat' in f:
                datfile = f
                os.remove(datfile)
    os.chdir(cwd)


def eut_dqm(run, force=False):
    if force and ( run_contains_file(run, '.begin_eut_ful') or 
                   run_contains_file(run, '.end_eut_ful') ) :
        
        s = raw_input(' !!! This will cause the eut ful process !!! \n\
        Do you really want to proceed? (yes or no) ')
        if s != 'yes':
            return

    if num_of_process('Marlin') > MAX_MARLIN_JOBS:
        sys.stdout.write(
            'Number of running Marlin jobs is larger than %s !\n'
            % MAX_MARLIN_JOBS)
        return

    if not force and run_contains_file(run, '.begin_eut_dqm'):
        return
        
    if not force and run_contains_file(run, '.end_eut_dqm'):
        return

    if not force and run_contains_file(run, '.end_eut_ful'):
        return
 

    #env_file = get_env_file(run)
    procenv = source_bash(env_file)
    procdir = procenv['jobsub']

    modes = ["convert", "clustering", "hitmaker"]        

    run = str(run).zfill(6) 
    datfile = check_raw_file(procdir, run)
    touch_file(run, '.begin_eut_dqm')

    board = datfile.split('_')[0]

    for mode in modes:
        sys.stdout.write('[eut_dqm] %s run %s ... ' %  (mode, run))
        sys.stdout.flush()
        
        cmd = 'jobsub -c dqm.cfg %s %s ' % (mode, run)
        output = proc_cmd(cmd, procdir=procdir, env=procenv)
        if debug:
            print output 

        copy_histos(board, run)
        sys.stdout.write('OK.\n')

    touch_file(run, '.end_eut_dqm')
    return board


def eut_cluster(args):
    run = args[0]
    #env_file = get_env_file(run)
    procenv = source_bash(env_file)
    procdir = procenv['simplesub']

    modes = ['clustering']

    check_raw_file(procdir, run)
    touch_file(run, '.begin_eut_cluster')

    for mode in modes:
        sys.stdout.write('[eut_dqm] %s run %s ... ' %  (mode, run))
        sys.stdout.flush()
        
        cmd = 'python config-cmspixel.py -a %s %s ' % (mode, run)
        output = proc_cmd(cmd, procdir=procdir, env=procenv)
        if debug:
            print output 
        sys.stdout.write('OK.\n')

    touch_file(run, '.end_eut_cluster')


def eut_track(args):
    run = args[0]
    #env_file = get_env_file(run)
    procenv = source_bash(env_file)
    procdir = procenv['simplesub']

    modes = ['prealign', 'tracks_noalign']

    check_raw_file(procdir, run)
    touch_file(run, '.begin_eut_track')

    for mode in modes:
        sys.stdout.write('[eut_dqm] %s run %s ... ' %  (mode, run))
        sys.stdout.flush()
        
        cmd = 'python config-cmspixel.py -a %s %s ' % (mode, run)
        output = proc_cmd(cmd, procdir=procdir, env=procenv)
        if debug:
            print output 
        sys.stdout.write('OK.\n')

    touch_file(run, '.end_eut_track')


def chk_dat(board, run, force=False): 
    decoder = Decoder()
    decoder.setNumROCs(8)

    run = str(run).zfill(6) 

    if not force and ( run_contains_file(run, '.begin_chk_dat') or 
                       run_contains_file(run, '.end_chk_dat') ):
        return

    #if run_contains_file_pattern(run, 'TestBoard2'): 
    #    decoder.setROCVersion(0)
    #else:
    decoder.setROCVersion(1)

    sys.stdout.write('[chk_dat] run %s ... ' % run)
    sys.stdout.flush()

    filename = os.path.join(datadir, run, 'mtb.bin')

    outfile = os.path.join(histdir, board, run, 'chk_dat.txt')
    orig_stdout = sys.stdout
    f = file(outfile, 'w')
    sys.stdout = f
        
    touch_file(run, '.begin_chk_dat')
    try:
        decoder.checkDataIntegrity(filename, 1, 5000)
    except IOError:
        pass 
    sys.stdout = orig_stdout
    f.close()
    sys.stdout.write(' OK.\n')
    touch_file(run, '.end_chk_dat')


def pub_dqm(board, run, force=False):

    run = str(run).zfill(6) 
    if not force and ( run_contains_file(run, '.begin_pub_dqm') or
                       run_contains_file(run, '.end_pub_dqm') or 
                       not run_contains_file(run, '.end_eut_dqm') or
                       not run_contains_file(run, '.end_chk_dat')
                   ):
        return
    sys.stdout.write('[pub_dqm] run %s ... ' % run)
    sys.stdout.flush()

    #env_file = get_env_file(run)
    procenv = source_bash(env_file)
    #procdir = os.path.join(procenv['simplesub'], 'CMSPixel')
    #procdir = '/afs/cern.ch/cms/Tracker/Pixel/HRbeamtest/data/'

    cmd = 'dqm %s/%s' %(board, run)

    touch_file(run, '.begin_pub_dqm')

    output = proc_cmd(cmd, procdir=histdir, env=procenv)
    sys.stdout.write(' OK.\n')
    touch_file(run, '.end_pub_dqm')


def status(args):
    if len(args) == 0:
        runs = get_valid_runs()
    elif len(args) == 1:
        runs = get_range_from_str(args[0])
    else:
        runs = args

    tags = ['eut_dqm', 'chk_dat', 'eut_ful', 'chk_data_integrity']

    begin_runs = []
    end_runs = []
    for run in runs:
        status = ''
        for tag in tags: 
            if ( run_contains_file(run, '.begin_%s' %tag) and 
                 not run_contains_file(run, '.end_%s' %tag) ):
                status += ' %s (...) ' % tag
            elif ( run_contains_file(run, '.begin_%s' %tag) and 
                 run_contains_file(run, '.end_%s' %tag)) :
                status += ' %s ' % tag 
            elif ( not run_contains_file(run, '.begin_%s' %tag) and 
                 run_contains_file(run, '.end_%s' %tag) ):
                status += ' %s (!?) ' % tag 
            else:
                status += '       '

        sys.stdout.write(' %s : %s \n' % (run, status))
        sys.stdout.flush()

        if '(...)' in status: 
            begin_runs.append(run)
        if '(!?)' in status:
            end_runs.append(run)

    if begin_runs:
        print 'Begin runs: \n', ','.join(begin_runs)
    
    if end_runs:
        print 'End runs:\n', ','.join(end_runs)
 

def index(board): 
    sys.stdout.write('[make index] ... ')
    sys.stdout.flush()

    runs = get_valid_runs()


    tags = ['eut_dqm', 'chk_dat', 'eut_ful', 'chk_data_integrity']

    run_status = { } 
    for run in runs:
        run_status[run] = {} 
        for tag in tags: 
            if ( run_contains_file(run, '.begin_%s' %tag) and 
                 not run_contains_file(run, '.end_%s' %tag) ):
                run_status[run][tag] = 'started'
            elif ( run_contains_file(run, '.begin_%s' %tag) and 
                 run_contains_file(run, '.end_%s' %tag)) :
                run_status[run][tag] = 'done'
            elif ( not run_contains_file(run, '.begin_%s' %tag) and 
                 run_contains_file(run, '.end_%s' %tag) ):
                run_status[run][tag] = 'error'
            else:
                run_status[run][tag] = 'unknown'

    status_colors = {
        'started': 'aqua',
        'done':  'green',
        'error': 'red',
        'unknown': 'white',
    }

    header_row = ['Run']
    header_row.extend(tags)
    t = HTML.Table(header_row=header_row)
    for run in sorted(run_status):
        run_link = HTML.link(run, '%s_%s' %(board, run))
        row = [run_link]

        for tag in tags: 
            color = status_colors[run_status[run][tag]]
            colored_result = HTML.TableCell(run_status[run][tag], bgcolor=color)
            row.append(colored_result)
        t.rows.append(row)
    
    htmlcode = str(t)

    html_header = '''<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <title>Test Beam DQM - clusters</title>
    <meta name="keywords" content="CERN CMS tracker upgrade" />
    <meta name="description" content="CMS Tracker upgrade summary page" />
    <link href=".style/default.css" rel="stylesheet" type="text/css" />
    <link rel="shortcut icon" type="image/x-icon" href=".style/images/favicon.ico">
 </head>
  <body>
      <div id="header">
    <h1>
    <a href="index.html">%s Test Beam DQM</a>
    </h1>
    </div>
    <div id="content">
    ''' % dataset 

    html_footer = '''<div id="footer">
    <p>Page created on %s </p>
    <p>&copy; <a href="mailto:Xin.Shi@cern.ch"> Xin Shi</a> 2013 </p>
    </div>
    </div>
    </body>
    </html>''' %  time.strftime("%Y-%m-%d %H:%M:%S GMT", time.gmtime())
    

    procenv = source_bash(env_file)
    targetdir = procenv['TARGETDIRECTORY']
    index = os.path.join(targetdir, 'index.html')
    fo = open(index, 'w')
    fo.write(html_header)
    fo.write(htmlcode)
    fo.write(html_footer)
    fo.close()
    sys.stdout.write(' OK.\n')


def reset(args):
    if len(args) != 1 : 
        sys.stdout.write('Please give the run range! \n')
        sys.exit()
        
    runs = args[0]
    fnames = ['.begin_eut_dqm', 
              '.end_eut_dqm', 
              '.begin_chk_dat', 
              '.end_chk_dat', 
              '.begin_pub_dqm', 
              '.end_pub_dqm', 
              ]

    for fname in fnames: 
        batch_rm([fname, runs])


def reset_ful(args):
    if len(args) != 1 : 
        sys.stdout.write('Please give the run range! \n')
        sys.exit()
        
    runs = args[0]
    fnames = ['.begin_pub_ful', '.end_pub_ful']

    for fname in fnames: 
        batch_rm([fname, runs])


def reset_ful_eut(args):
    if len(args) != 1 : 
        sys.stdout.write('Please give the run range! \n')
        sys.exit()
        
    runs = args[0]
    fnames = ['.begin_eut_ful', 
              '.end_eut_ful', 
              '.begin_pub_ful', 
              '.end_pub_ful', 
              ]

    for fname in fnames: 
        batch_rm([fname, runs])


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
    if len(arg) < 2:
        sys.stdout.write('Please give the run range! \n')
        sys.exit()

    fname = arg[0]
    runs = arg[1:]

    if len(runs) == 1:
        new_runs = get_range_from_str(runs[0])        
    else:
        new_runs = runs

    for run in new_runs:
        sys.stdout.write('[rm file] run %s, %s ... ' % (run, fname))
        sys.stdout.flush()
        
        file_ = os.path.join(datadir, run, fname)
        if os.path.exists(file_):
            os.remove(file_)
            sys.stdout.write(' OK.\n')        
        else:
            sys.stdout.write(' already removed.\n')        


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


def proc_cmd(cmd, test=False, verbose=1, procdir=None, env=os.environ):
    if test:
        sys.stdout.write(cmd+'\n')
        return 

    cwd = os.getcwd()
    if procdir != None:
        os.chdir(procdir)

    process = subprocess.Popen(cmd.split(), 
                               stdout=subprocess.PIPE, env=env)
    process.wait()
    stdout = process.communicate()[0]
    if 'error' in stdout:
        sys.stdout.write(stdout)
    if procdir != None:
        os.chdir(cwd)
    return stdout


def check_update_status(f, verbose=0):
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
    runs = []
    for root, dirs, files in os.walk(datadir):
        if len(dirs) != 0: 
            continue # bypass single files in the datadir  
        run = root.split('/')[-1]

        if not run.isdigit():
            continue
        
        if int(run) < begin_valid_run or int(run) > end_valid_run:
            continue
        runs.append(run)

    runs.sort()
    return runs


def get_valid_new_runs():
    dbfile = check_and_join(dbpath, dbname)
    db = open(dbfile)
    runs = json.load(db)
    db.close()

    local_runs = get_valid_runs()
    #remote_runs = runs.keys()
    remote_runs = runs 

    remote_runs.sort()

    runs = []
    for run in remote_runs:
        if run not in local_runs:
            runs.append(run)

    #runs = get_valid_runs()
    new_runs = []

    fnames = [ '.begin_eut_dqm', '.end_eut_dqm', 
               '.begin_chk_dat', '.end_chk_dat', 
               '.begin_pub_dqm', '.end_pub_dqm', 
               '.begin_eut_ful', '.end_eut_ful', 
               '.begin_pub_ful', '.end_pub_ful', 
               ]

    for run in runs:
        for fname in fnames:
            if run_contains_file(run, fname):
                continue

        new_runs.append(run)
    return new_runs
            

def get_runs_from_ls(output):
    runs = []
    for line in output.split():
        if len(line) > 6: # skip non-valid run and files. 
            continue

        # print line.zfill(6) 
        # items = line.split('_')
        # print items

        # sys.exit()
        # if len(items) < 3:
        #     continue

        # board = items[0]
        # spill = items[2]            

        # file = line
        # #if not is_stable_file(file):
        # #    continue

        run = line.zfill(6)
        if not run.isdigit():
            continue
        
        run = int(run) 

        if run < begin_valid_run or run > end_valid_run:
            continue

        if run not in runs:
            runs.append(run)

    return runs


def is_stable_file(filename):
    f = os.path.join(daqdir, filename)
    then = time.ctime(os.path.getmtime(f))
    then = strptime(then, "%a %b %d %H:%M:%S %Y")
    now = datetime.now()
    tdelta = now - then
    min_tdelta = timedelta(minutes=1)
    return tdelta > min_tdelta


def check_raw_file(procdir, run):
    filedir = os.path.join(procdir, 'data/cmspixel', run)
    cwd = os.getcwd()
    os.chdir(filedir)
    for root, dirs, files in os.walk(filedir):
        if 'mtb.bin' in files:
            os.remove('mtb.bin')

        for f in files:
            if '.dat' in f:
                #filesize = get_filesize(root, f)
                datfile = f
                os.symlink(datfile, 'mtb.bin')
                break

    os.chdir(cwd)
    return datfile 


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
        time.strptime(timestr, "_%Y_%m_%d__%Hh%Mm%Ss")
        files.append(filename)

    return files 

def is_valid_run_str(val):
    if val.isdigit(): 
        return True
    if ',' in val or '-' in val:
        return True
    
    return False 


def get_range_from_str(val, start=0, stop=None):

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

    #result = [ str(r).zfill(6) for r in result ]
    result.sort()
    return result


def touch_file(run, fname): 
    f = os.path.join(datadir, run, fname)
    open(f, 'a').close()
    

def run_contains_file(run, f):
    rundir = get_rundir(run)
    for root, dirs, files in os.walk(rundir):
        if f in files:
            return True
    return False
     
def run_contains_file_pattern(run, pat):
    rundir = get_rundir(run)

    for root, dirs, files in os.walk(rundir):
        for f in files:
            if pat in f:
                return True
    return False



def source_bash(f):
    pipe = subprocess.Popen(". %s; env" % f, stdout=subprocess.PIPE,
                            shell=True)
    output = pipe.communicate()[0]
    #env = dict((line.split("=", 1) for line in output.splitlines()))
    env = {}
    for line in output.splitlines():
        items = line.split("=", 1) 
        if len(items) < 2:
            continue 

        env[items[0]]= items[1]
    return env 


# def get_env_file(run):
#     env_file = '/home/pixel_dev/dqm/bash/dqm_env.sh'
#     if run_contains_file_pattern(run, 'TestBoard2'): 
#         env_file = '/home/pixel_dev/dqm/bash/dqm_env_v0.sh'
#     return env_file


def num_of_process(process_name):
    proc = subprocess.Popen(["pgrep", process_name], 
                            stdout=subprocess.PIPE) 
    stdout = proc.communicate()[0]
    num = len( stdout.split())
    return num 


def get_datfile(run): 
    datfile = []
    cmd = '%s ls %s/%s' % (eos, daqdir, run)
    output = proc_cmd(cmd)
    
    keyword = '.dat'
    for line in output.split():
        if keyword in line:
            datfile.append(line)

    return datfile


def get_rundir(run):
    rundir = os.path.join(datadir, str(run).zfill(6))
    return rundir

def get_filesize(root, f):
    print root
    sys.exit()
    cmd = '%s ls -l %s/%s' % (eos, root, f)
    output = proc_cmd(cmd)
    print output


def copy_histos(board, run):
    subdir = '%s/%s' %(board, run)
    filepath = os.path.join(histdir, board, run)

    if not os.access(filepath, os.F_OK):
        os.makedirs(filepath)

    cmd = 'cp %s/%s-clustering.root %s' %(histdir, run, filepath)
    proc_cmd(cmd)
        

if __name__ == '__main__':
    main()



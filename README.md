#  Test Beam DQM


## Procedure for FNAL2013 


### Compile on SL6 
	ssh lxplus.cern.ch 
	cd /afs/cern.ch/cms/Tracker/Pixel/HRbeamtest/dqm
	git clone https://github.com/xshi/dqm.git v3
	cd v3
	git checkout v3.1
	. setup.sh
	make


### Run DQM manualy

	 /afs/cern.ch/cms/Tracker/Pixel/HRbeamtest/dqm/v3/python/dqm.py 30623

	 or run range: 

	 /afs/cern.ch/cms/Tracker/Pixel/HRbeamtest/dqm/v3/python/dqm.py 30623-30650 

### Run DQM with cron job

	acrontab -e
	
	lxplus.cern.ch /afs/cern.ch/cms/Tracker/Pixel/HRbeamtest/dqm/v3/bash/cron_jobs.sh

### View DQM online

https://cern.ch/cmspxltb/fnal2013/	
	
	

#  Test Beam DQM


## Procedure for FNAL2013 

	ssh lxplus.cern.ch 
	cd /afs/cern.ch/cms/Tracker/Pixel/HRbeamtest/dqm
	git clone https://github.com/xshi/dqm.git v3
	cd v3
	git checkout v3.1
	. setup.sh
	make
	
	acrontab -e
	lxplus.cern.ch /afs/cern.ch/cms/Tracker/Pixel/HRbeamtest/dqm/v3/bash/cron_jobs.sh

	
	
	

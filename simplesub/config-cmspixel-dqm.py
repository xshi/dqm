# Global parameters applying to all templates:
def runConfig(params):
    #params["GearFile"]  = "gear_cmspixel_single_2012-03.xml"
    #params["GearFile"]  = "gear_cmspixel_module_2012-03.xml"
    #params["GearFile"]  = "gear_cmspixel_telescope_final_straight_2012-07.xml"
    params["GearFile"]  = "gear_cmspixel_telescope_PSI2013.xml"

    params["HistoInfo"] = "histoinfo.xml"
    params["HistogramFilling"] = "true"

    params["BuildHotPixelDatabase"] = "false"
    
    params["RunType"] = "data"
    params["ResolutionX"]         =  "44 44 44 44 44 44 44 44"
    params["ResolutionY"]         =  "29 29 29 29 29 29 29 29"
    params["ResolutionZ"]         =  "100 100 100 100 100 100 100 100"
    params["UseManualDUT"]        = "true"
    params["ManualDUTID"]         = "4"
    params["InitNoiseValue"] = "0 0 0 0 0 0 0 0"
    params["InitPedestalValue"] = "0 0 0 0 0 0 0 0"
    params["MaxXVector"] = "51 51 51 51 51 51 51 51"
    params["MaxYVector"] = "79 79 79 79 79 79 79 79"
    params["MinXVector"] = "0 0 0 0 0 0 0 0"
    params["MinYVector"] = "0 0 0 0 0 0 0 0"
    params["SensorIDVec"] = "0 1 2 3 4 5 6 7"
    params["MaxAllowedFiringFreq"] = "0.9"
    
    if params["BuildHotPixelDatabase"] == "true":
       params["HotPixelLeft"] = "<processor"
       params["HotPixelRight"] = "/>"
    else:
       params["HotPixelLeft"] = "<!--"
       params["HotPixelRight"] = "-->"
    

# Parameters for combined conversion and calibration:
def fullconverter(params):
    params["TemplateFile"] = "fullconverter-tmp.xml"        # The Marlin XML template used for this step
    params["NUMBER_OF_EVENTS"] = "5000"                    # How many events shall be processed?
    params["lazyDecoding"] = "true"                         # Switch between strict and lazy decoding. Lazy decoding will not check for correct TBM trailers and a valid data length.
    params["haveTBMheaders"] = "false"                      # Switch TBM mode on and off. This gives the possibility to read data without real or emulated TBM headers
    params["writeEmptyEvents"] = "false"                    # Enable or disable the writing of events with no hit in all sensor planes.
    params["FileName"] = "mtb.bin"                          # Input binary file name
    params["addressLevelsFile"] = "addressParameters.dat"   # Address levels calibration file for the TBM and ROC address encoding levels (analogue ROC).
    params["shufflePlanes"] = "0 1 2 3 4 5 6 7"             # Int vector to hold the telescope plane IDs in the order in which they get the readout token.
    params["digitalROC"] = "true"                           # Choose whether you have digital ROC data to decode or analogue.
    params["useIPBus"] = "true"                            # Switch from USB readout format (Altera board) to the IPBus readout format (Xilinx board).
    params["EventSelection"] = "2"			    # Select the events to process: 0 - all, 1 - only with correct No. of ROC headers, 2 - only with corr. ROC headers and without bit errors in them.-->
    params["calibrationType"] = "true"
    params["NoOfEventPerCycle"] = "100" # EUTelHotPixelKiller
    params["debugDecoder"] = "0"   
    params["TotalNoOfCycles"]    = "10"  # EUTelHotPixelKiller


# Parameters for the different analysis steps / templates:
def converter(params):
    params["TemplateFile"] = "converter-tmp.xml"            # The Marlin XML template used for this step
    params["lazyDecoding"] = "true"                         # Switch between strict and lazy decoding. Lazy decoding will not check for correct TBM trailers and a valid data length.
    params["haveTBMheaders"] = "false"                      # Switch TBM mode on and off. This gives the possibility to read data without real or emulated TBM headers
    params["writeEmptyEvents"] = "false"                    # Enable or disable the writing of events with no hit in all sensor planes.
    params["FileName"] = "mtb.bin"                          # Input binary file name
    params["addressLevelsFile"] = "addressParameters.dat"   # Address levels calibration file for the TBM and ROC address encoding levels (analogue ROC).
    params["shufflePlanes"] = "0 1 2 3 4 5 6 7"             # Int vector to hold the telescope plane IDs in the order in which they get the readout token.
    params["digitalROC"] = "true"                           # Choose whether you have digital ROC data to decode or analogue.
    params["useIPBus"] = "true"                            # Switch from USB readout format (Altera board) to the IPBus readout format (Xilinx board).
    params["debugDecoder"] = "0"
    params["EventSelection"] = "2"			    # Select the events to process: 0 - all, 1 - only with correct No. of ROC headers, 2 - only with corr. ROC headers and without bit errors in them.-->

    
def calibration(params):
    params["TemplateFile"] = "calibration-tmp.xml"
    params["calibrationType"] = "true"
    params["NoOfEventPerCycle"] = "100" # EUTelHotPixelKiller
    params["TotalNoOfCycles"]    = "10"  # EUTelHotPixelKiller

def clustering_ff(params):
    params["TemplateFile"] = "clustering-tmp.xml"

def clustering_sparse(params):
    params["TemplateFile"] = "clustering_sparse-tmp.xml"
    params["MinCharge"] = "1"
    params["MinNumberOfPixels"] = "1"

def hitmaker(params):
    params["TemplateFile"] = "hitmaker-tmp.xml"
    params["CoGAlgorithm"] = "FULL"
    
def prealign(params):
    params["TemplateFile"] = "prealign-tmp.xml"
    params["ResidualXMin"]        = "-600 -600 -600 -600 -600 -600 -600 -600"
    params["ResidualXMax"]        = " 600 600 600 600 600 600 600 600 "
    params["ResidualYMin"]        = "-600 -600 -600 -600 -600 -600 -600 -600"
    params["ResidualYMax"]        = " 600 600 600 600 600 600 600 600 "

def alignment(params):
    params["TemplateFile"] = "align-tmp.xml"
    params["RunPede"]             = "1" 
    params["UseResidualCuts"]     = "0"
    params["ResidualXMin"]        = "-600 -600 -600 -600 -600 -600 -600 -600"
    params["ResidualXMax"]        = " 600  600  600  600  600  600 600 600"
    params["ResidualYMin"]        = "-600 -600 -600 -600 -600 -600 -600 -600"
    params["ResidualYMax"]        = " 600  600  600  600  600  600 600 600"
    params["DistanceMax"]         = "2000"
    if params["UseManualDUT"]:
       params["ExcludePlanes"]    = params["ManualDUTID"]
    else:
       params["ExcludePlanes"]    =  ""
    params["FixedPlanes"]         =  "0 7"
    params["FixParameter"]        =  "28 28 28 28 28 28 28 28"

def trackfitter(params):
    params["TemplateFile"] = "tracks-tmp.xml"
    params["Ebeam"] = "280"
    params["SlopeXLimit"] = "20.0"
    params["SlopeYLimit"] = "20.0"
    params["DUTalignmentX"] = "-100"## -100:use prealign factor. Could be updated with (-1)*DUTshiftX->GetMean() in DUTHisto
    params["DUTalignmentY"] = "-100"## -100:use prealign factor. Could be updated with (-1)*DUTshiftY->GetMean() in DUTHisto
    params["Xwindow"] = "0.13"    ## default = 0.13 mm according to 3 x pitchX/sqrt(12)
    params["Ywindow"] = "0.09"    ## default = 0.09 mm according to 3 x pitchY/sqrt(12)
    params["MaxChi2"] = "5000"
    
def trackfitter_noalign(params):
    params["TemplateFile"] = "tracks-noalign-tmp.xml"
    params["Ebeam"] = "400"
    params["SlopeXLimit"] = "20.0"
    params["SlopeYLimit"] = "20.0"
    params["DUTalignmentX"] = "-100"## -100:use prealign factor. Could be updated with (-1)*DUTshiftX->GetMean() in DUTHisto
    params["DUTalignmentY"] = "-100"## -100:use prealign factor. Could be updated with (-1)*DUTshiftY->GetMean() in DUTHisto
    params["Xwindow"] = "0.13"    ## default = 0.13 mm according to 3 x pitchX/sqrt(12)
    params["Ywindow"] = "0.09"    ## default = 0.09 mm according to 3 x pitchY/sqrt(12)
    #params["MaxChi2"] = "10000"
    params["MaxChi2"] = "200" ## used for Xray2013Data 

    
def event_viewer(params):
    params["TemplateFile"] = "event-viewer-tmp.xml"
    params["TrackFileName"] = "tracks_noalign"

# run Marlin
if __name__ == "__main__":
    from steeringGenerator import *
    functions = {"convert": converter,
                 "calibrate": calibration,
                 "fullconvert": fullconverter,
                 "clustering_ff": clustering_ff,
		 "clustering_sparse": clustering_sparse,
                 "clustering": clustering_sparse,
                 "hits": hitmaker,
                 "prealign": prealign,
                 "align": alignment,
                 "tracks": trackfitter,
                 "tracks_noalign": trackfitter_noalign,
                 "view": event_viewer}
    jobMaker(functions, runConfig)

def siteConfig(params):
    #Where do you want all results to be stored?
    params["ResultPath"] = "CMSPixel"
    #Where do you want your databases to be stored?
    params["DbPath"] = "CMSPixel"
    #Where should I put your AIDA histogram files?
    params["HistoPath"] = "CMSPixel"
    #Where can I find your native data?
    params["NativePath"] = "CMSPixel"
    #Is there a prefix to the run directory? (like bt05r......)
    params["prefix"] = ""
    #Where do the job template files reside?
    params["TemplatePath"] = "template_cmspixel"
    #How many Marlin jobs should run in paralell? Note: align jobs run in a single thread.
    params["NParallel"] = "2"

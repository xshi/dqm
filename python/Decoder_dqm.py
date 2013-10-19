import struct

class Decoder:

    def __init__(self):
        self.rocType = 0
        self.numROCs = 8
        self.trailerLength = 15
        self.numEvents=0
        self.clearExpectedPixels()
        return


    def setNumROCs(self,numROCs):
        self.numROCs = numROCs
        return

    
    def setROCVersion(self,version):
        if version==0:
            print "Decoder: assuming ROCs with inverted address levels"
        elif version==1:
            print "Decoder: assuming v2 digital ROCs"
            pass
        self.rocType = version
        return


    def printEventString(self,eventString):
        words=eventString.split("\n")
        words.append("ffffffff")
        eventPrintout=""
        eventLength=0
        ipos=0
        iword=0
        formattedString=""
        while ipos<len(words):
            word=words[ipos]
            if word=="ffffffff" and ipos>0:
                # process previous event
                evEnd=2*(16+eventLength-self.trailerLength)+4 # +4 for spacers in header
                trEnd=2*(16+eventLength)+4    # +4 for spacers in header
                if eventLength>0 and len(formattedString)>=trEnd:
                    formattedString=formattedString[:evEnd]+" "\
                                     +formattedString[evEnd:evEnd+8]+"."\
                                     +formattedString[evEnd+8:evEnd+16]+"."\
                                     +formattedString[evEnd+16:evEnd+26]+"."\
                                     +formattedString[evEnd+26:trEnd]
                    pass
                eventPrintout+=formattedString+"\n"
                # initialize for next event
                formattedString=""
                eventLength=-1
                iword=0
                pass
            if iword<2:
                formattedString+=word+"."
            elif iword==2:
                formattedString+=word+"."
                eventLength=int(word,16)
            elif iword==3:
                formattedString+=word+" "
            else:
                formattedString+=word[6:8]+word[4:6]+word[2:4]+word[0:2]
                pass
            iword+=1
            ipos+=1
            pass
        return eventPrintout
                

    def clearExpectedPixels(self):
        self.expectedPixelRows=[]
        self.expectedPixelColumns=[]
        self.expectedRocNums=[]
        self.allExpectedRows=[]
        self.allExpectedColumns=[]
        self.allExpectedRocNums=[]
        return

    def addExpectedPixel(self,rocnum,row,column):
        # register an armed pixel, i.e. one that *should* be in the readout.
        self.expectedPixelRows.append(row)
        self.expectedPixelColumns.append(column)
        self.expectedRocNums.append(rocnum)
        if not row in self.allExpectedRows:
            self.allExpectedRows.append(row)
            self.allExpectedRows.sort()
            pass
        if not column in self.allExpectedColumns:
            self.allExpectedColumns.append(column)
            self.allExpectedColumns.sort()
            pass
        if not rocnum in self.allExpectedRocNums:
            self.allExpectedRocNums.append(rocnum)
            self.allExpectedRocNums.sort()
        return
    
    
    def pixelDecoder(self,hexstring):
        # this decodes a single pixel from hex representation
        # with preprended ROC number, i.e. N_pixpix
        if len(hexstring)!=8:
            return [-1,-1,-1,-1]
        try:
            roc=int(hexstring.split("_")[0])
        except:
            return [-1,-1,-1,-1]
        # convert to binary
        try:
            value=int(hexstring.split("_")[1],16)
        except:
            return [roc,-1,-1,-1]
        binstring=""
        for ibit in range(24):
            binstring=str((value>>ibit)&1)+binstring
            pass

        # column address
        column1=int(binstring[0:3],2)
        column2=int(binstring[3:6],2)
        doublecolumn=6*column1+column2
        if column1<=5 and column2<=5 and doublecolumn<=25:
            column=2*doublecolumn
        else:
            doublecolumn=-1
            column=-1
            pass
        # row address (inverted in current revision of the ROC!)
        row1=int(binstring[6:9],2)
        row2=int(binstring[9:12],2)
        row3=int(binstring[12:15],2)            
        if self.rocType==0:
            row1=7-row1
            row2=7-row2
            row3=7-row3
            pass
        if column>=0: column+=row3&1
        if row1>5 or row2>5 or row3>5:
            row=-1
        else:
            row=80-(row3+6*row2+36*row1)/2
            if row<0 or row>79: row=-1
            pass
        # pulseheight including zero bit in the middle
        pulseheight=int(binstring[15:19]+binstring[20:24],2)
        zero=int(binstring[19],2)
        if zero!=0: pulseheight=-1
        return [roc,column,row,pulseheight]

    
    def analyzeOneEvent(self,eventString):
        # split an event in string representation into ROC headers,
        # pixels and leftovers
        pos=0
        headers=[]
        pixels=[]
        leftovers=[]
        while pos<len(eventString):
            if eventString[pos:pos+2]=="7f":
                headers.append(eventString[pos:pos+3])
                pos+=3
            elif pos<=len(eventString)-6:
                pixels.append(str(len(headers))+"_"+eventString[pos:pos+6])
                pos+=6
            else:
                leftovers.append(eventString[pos:])
                pos+=6
                pass
            pass
        return [headers,leftovers,pixels]


    def checkDataIntegrity(self,filename,binary=0, max_nEvents=None):
        nEvents=0
        headerMap={}
        leftoverMap={}
        lengthMap={}
        pixelMap={}
        pulseheightMap={}
        statusMap={}
        trigPhaseMap={}
        nStackedMap={}
        posInEvent=0
        rocData=""
        eventSize=0
        if binary:
            datafile=open(filename,"rb")
        else:
            datafile=open(filename,"r")
            pass
        # loop over all words in the file plus an additional marker
        lastline=0
        while lastline==0:
            if binary:
                try:
                    word=datafile.read(4)
                    entry="%08x"%struct.unpack("<I",word)
                except:
                    entry="ffffffff"
                    lastline=1
                    pass
                pass
            else:
                line=datafile.readline()
                if line=="":
                    line="ffffffff"
                    lastline=1
                    pass
                entry=line.strip()
                pass
            if entry=="ffffffff" and eventSize>0:
                # analyze previous event
                payload=rocData[:2*(eventSize-self.trailerLength)]
                trailer=rocData[2*(eventSize-self.trailerLength):2*eventSize]
                if len(trailer)!=2*self.trailerLength:
                    # this trailer is invalid.
                    print "ERROR: checkDataIntegrity has trailer of"\
                          +" invalid length:",len(trailer),"digits"
                    print "      ",payload,trailer
                else:
                    # analyze trailer
                    
                    # timestamp (only lowest 32 bits for now)
                    timestamp = (int(trailer[16:18],16)<<8)\
                                +(int(trailer[18:20],16)<<16)\
                                +(int(trailer[20:22],16)<<24)\
                                +(int(trailer[24:26],16))

                    # stacking level of triggers
                    if len(rocData)>2*eventSize-4:
                        byteval=int(trailer[2*self.trailerLength-4:2*self.trailerLength-2],16)
                        nStacked=byteval&0x3f
                    else:
                        nStacked="?"
                        pass
                    if nStacked in nStackedMap.keys():
                        nStackedMap[nStacked]+=1
                    else:
                        nStackedMap[nStacked]=1
                        pass
                    # trigger phase (useless for internal triggers, but important for external)
                    # and readout status
                    if len(rocData)>2*eventSize-2:
                        byteval=int(trailer[2*self.trailerLength-2:2*self.trailerLength],16)
                        roStatus=byteval&0x1f
                        trigPhase=(byteval&0xe0)>>5
                    else:
                        roStatus="?"
                        trigPhase="?"
                        pass
                    if roStatus in statusMap.keys():
                        statusMap[roStatus]+=1
                    else:
                        statusMap[roStatus]=1
                        pass
                    if trigPhase in trigPhaseMap.keys():
                        trigPhaseMap[trigPhase]+=1
                    else:
                        trigPhaseMap[trigPhase]=1
                        pass
                    # debug output
                    #print "event status=",roStatus,"nStacked=",nStacked,"length=",len(rocData)
                    pass
                # split payload into individual ROC headers and pixels 
                [headers,leftovers,pixels]=self.analyzeOneEvent(payload)
                for entry in headers:
                    if entry in headerMap.keys():
                        headerMap[entry]+=1
                    else:
                        headerMap[entry]=1
                        pass
                    pass
                for entry in leftovers:
                    if entry in leftoverMap.keys():
                        leftoverMap[entry]+=1
                    else:
                        leftoverMap[entry]=1
                        pass
                for entry in pixels:
                    # replace pulse height by 255
                    # so we can compare pixel addresses more easily
                    [roc,col,row,pulseheight]=self.pixelDecoder(entry)
                    if pulseheight in pulseheightMap.keys():
                        pulseheightMap[pulseheight]+=1
                    else:
                        pulseheightMap[pulseheight]=1
                        pass
                    entry2=entry.split("_")[0]+"_%06x"%(int(entry.split("_")[1],16)|0x1ef)
                    if entry2 in pixelMap.keys():
                        pixelMap[entry2]+=1
                    else:
                        pixelMap[entry2]=1
                        pass
                    pass
                payloadsize = len(payload)/2
                if payloadsize in lengthMap.keys():
                    lengthMap[payloadsize]+=1
                else:
                    lengthMap[payloadsize]=1
                    pass
                nEvents+=1
                # Check the max nEvents for DQM
                if max_nEvents is not None and nEvents > max_nEvents: 
                    print 'Reaching the max events for DQM: ', max_nEvents 
                    break 
                
                # now get ready for next event

                posInEvent=0
                rocData=""
            elif posInEvent==1:
                eventNumber=int(entry,16)
            elif posInEvent==2:
                eventSize=int(entry,16)
            elif posInEvent==3:
                userHeader=int(entry,16)
            elif posInEvent>=4:
                rocData+=entry[6:8]+entry[4:6]+entry[2:4]+entry[0:2]
            else:
                pass # this likely only applies to the very first ffffffff header
            posInEvent+=1
            pass
        datafile.close()
        print "summary: total number of events was",nEvents
        #print "         average number of pixels per event was", (nEvents
        if nEvents>0:
            nheaders=0
            keys=headerMap.keys()
            keys.sort()
            for entry in keys:
                print "         header",entry,":",headerMap[entry]
                nheaders+=headerMap[entry]
                pass
            print "fraction of missing headers (assuming",self.numROCs,"ROCs):",\
                  (self.numROCs*nEvents-nheaders)*1.0/self.numROCs/nEvents
            pass
        keys=leftoverMap.keys()
        keys.sort()
        for entry in keys:
            print "         extra",entry,"between ROCs and trailer:",leftoverMap[entry]
            pass
        keys=lengthMap.keys()
        keys.sort()
        #for entry in keys:
        #    print "         length",entry,":",lengthMap[entry]
        #    pass
        badhits=0
        unexpectedhits=0
        nhits=0
        keys=pixelMap.keys()
        keys.sort()
        for entry in keys:
            pixel=self.pixelDecoder(entry)
            #print "         pixel",entry,pixel,":",pixelMap[entry]
            nhits+=pixelMap[entry]
            if (pixel[0]<0) or (pixel[1]<0) or (pixel[2]<0) or (pixel[3]<0):
                badhits+=pixelMap[entry]
            elif (not pixel[0] in self.allExpectedRocNums) or\
                     (not pixel[1] in self.allExpectedColumns) or\
                     (not pixel[2] in self.allExpectedRows):
                unexpectedhits+=pixelMap[entry]
                pass
            pass
        if (nhits>0):
            print "fraction of invalid hits:",1.0*badhits/nhits
            # only make sense in the calibration mode 
            #print "fraction of unexpected hits:",1.0*unexpectedhits/nhits

            pass
        keys=pulseheightMap.keys()
        keys.sort()
        #for entry in keys:
        #    print "         pulseheight",entry,":",pulseheightMap[entry]
        #    pass
        keys=trigPhaseMap.keys()
        keys.sort()
        for entry in keys:
            print "         trigger phase",entry,":",trigPhaseMap[entry]
            pass
        keys=nStackedMap.keys()
        keys.sort()
        for entry in keys:
            print "         events with",entry,"triggers stacked:",nStackedMap[entry]
            pass
        keys=statusMap.keys()
        keys.sort()
        for entry in keys:
            print "         event status",entry,":",statusMap[entry]
            pass
        return


    def decodeEventString(self,eventString):
        return
            

    def decodeDataFile(self,filename):
        return

    

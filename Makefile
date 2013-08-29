ROOTFLAGS=`root-config --cflags`
ROOTLIBDIR=`root-config --libdir`
ROOTLIBFLAGS=`root-config --libs`
ROOTLIBFLAGS+=-lHistPainter
BOOSTLIBFLAGS=-L/usr/lib64/boost141
BOOSTLIBFLAGS+=-lboost_system -lboost_filesystem -lboost_regex -lboost_program_options
GEOMLIBFLAG=-lGeom
GLIBFLAGS=`root-config --glibs`
INCLUDEFLAGS=-Iinclude/
INCLUDEFLAGS+=-I/usr/include/boost141/
SRCDIR=src
INCDIR=include
LIBDIR=lib
BINDIR=bin
DOCDIR=doc
COMPILERFLAGS+=-Wall
#COMPILERFLAGS+=-ggdb
COMPILERFLAGS+=-g
COMPILERFLAGS+=-Werror
#COMPILERFLAGS+=-O5

COMP=g++ $(COMPILERFLAGS) $(INCLUDEFLAGS) $(DEFINES)


bin: dqm dqm_xshi 
	@echo "Executable dqm is built."

all: hit tkgeometry exocom general elements ushers dressers viz naly squid testObjects tklayout dqm dqm_xshi
	@echo "Full build successful."

#ROOT-related stuff
$(LIBDIR)/rootweb.o: $(SRCDIR)/rootweb.cpp $(INCDIR)/rootweb.hh
	mkdir -p $(LIBDIR)	
	$(COMP) $(ROOTFLAGS) -c -o $(LIBDIR)/rootweb.o $(SRCDIR)/rootweb.cpp

dqm: $(BINDIR)/dqm
$(BINDIR)/dqm: $(SRCDIR)/dqm.cpp $(LIBDIR)/rootweb.o 
	mkdir -p $(BINDIR)	
	$(COMP) $(ROOTFLAGS) $(LIBDIR)/rootweb.o $(SRCDIR)/dqm.cpp $(ROOTLIBFLAGS) $(BOOSTLIBFLAGS) -o $(BINDIR)/dqm

dqm_xshi: $(BINDIR)/dqm_xshi
$(BINDIR)/dqm_xshi: $(SRCDIR)/dqm_xshi.cpp $(LIBDIR)/rootweb.o 
	mkdir -p $(BINDIR)	
	$(COMP) $(ROOTFLAGS) $(LIBDIR)/rootweb.o $(SRCDIR)/dqm_xshi.cpp $(ROOTLIBFLAGS) $(BOOSTLIBFLAGS) -o $(BINDIR)/dqm_xshi


test: $(BINDIR)/test_web
$(BINDIR)/test_web: $(SRCDIR)/test.cpp $(LIBDIR)/rootweb.o 
	mkdir -p $(BINDIR)	
	$(COMP) $(ROOTFLAGS) $(LIBDIR)/rootweb.o $(SRCDIR)/test.cpp $(ROOTLIBFLAGS) $(BOOSTLIBFLAGS) -o $(BINDIR)/test_web

#CLEANUP
clean:
	rm -f lib/rootweb.o bin/dqm 

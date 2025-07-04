SHELL := bash
TARGET=TSaCt2
BUILDDIR = ./build/

CPP=g++
LD=g++

SRCS += src/main.cpp
SRCS += src/gate.cpp
SRCS += src/booleannet.cpp
SRCS += src/aagloader.cpp
SRCS += src/output.cpp
SRCS += src/model.cpp 
SRCS += src/netwriter.cpp
SRCS += src/library.cpp

OBJS  = $(addprefix $(BUILDDIR),$(notdir $(SRCS:.cpp=.o)))

INCLUDE = -I inc
CFLAGS  = -g

.PHONY: all bin rmdoc clean indent doc

all: bin

$(BUILDDIR)%.o: src/%.cpp
	@echo Compiling $<
	@$(CPP) -c $(CFLAGS) $(INCLUDE) $< -o $@

bin: $(OBJS)
	@echo Linking $(TARGET)
	@$(LD) $(OBJS) $(LDFLAGS) -o $(TARGET)
	
rmdoc:
	rm -rf doc/*
	
clean: 
	rm ./TSaCt2
	rm -rf build/*

indent:
	for f in $(shell ls src | grep ".cpp" ) ; do  echo $$f ; fold -w 120 -s src/$$f ; indent -kr -nut src/$$f ; done
	for f in $(shell ls inc | grep ".[c|h]" ); do echo $$f ; fold -w 120 -s inc/$$f ; indent -kr -nut inc/$$f ; done

doc:
	doxygen Doxyfile

vtestDR: clean all
	./TSaCt2 -vv -s C17.aag -c "dual;scoap;tex"
	pdflatex C17.tex
	okular C17.pdf
	
vtest: clean all
	./TSaCt2 -vv -s C17.aag -c "scoap; buffByScoap 10;scoap;buffByScoap 6; scoap;tex;stats"
	pdflatex C17.tex
	okular C17.pdf

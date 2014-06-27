CC = gcc
CXX = g++

LDFLAGS = -lm
C_FLAGS = -pedantic -Wall -Wextra 

ifeq ($(shell uname -s),Darwin)
	C_FLAGS += -I/Developer/SDKs/MacOSX10.6.sdk/System/Library/Frameworks/OpenCL.framework/Headers/
	LDFLAGS += -framework OpenCL
else
	LDFLAGS += -lopencl
endif

CFLAGS = -std=c99 ${C_FLAGS}
CXXFLAGS = -std=c++11 ${C_FLAGS}

%.app:%.c
	${CC} ${CFLAGS} -o $@ $< ${LDFLAGS}

%.app:%.cpp
	${CXX} ${CXXFLAGS} -o $@ $< ${LDFLAGS}

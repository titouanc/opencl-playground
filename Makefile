CC = gcc
CXX = g++

# AVX2 has fused multiply-add
C_FLAGS = -pedantic -Wall -Wextra -mavx2

CFLAGS = -std=c99 ${C_FLAGS}
CXXFLAGS = -std=c++11 ${C_FLAGS}

LDFLAGS = -lOpenCL -lm

%.app:%.c
	${CC} ${CFLAGS} -o $@ $< ${LDFLAGS}

%.app:%.cpp
	${CXX} ${CXXFLAGS} -o $@ $< ${LDFLAGS}

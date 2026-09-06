CC = gcc
CFLAGS = -O2 -Wall -Wextra -I.

TARGET_NATIVE = ../../tests/test_engine

all: $(TARGET_NATIVE)

$(TARGET_NATIVE): crossword_engine.c ../../tests/test_engine.c
	$(CC) $(CFLAGS) crossword_engine.c ../../tests/test_engine.c -o $(TARGET_NATIVE)

test: $(TARGET_NATIVE)
	$(TARGET_NATIVE)

clean:
	rm -f $(TARGET_NATIVE)

.PHONY: all test clean

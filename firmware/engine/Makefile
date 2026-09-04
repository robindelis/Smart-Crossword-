CC = gcc
CFLAGS = -O2 -Wall -Wextra -I.
CLANG = clang
WASM_FLAGS = --target=wasm32 -O2 -nostdlib -Wl,--no-entry -Wl,--export-all

TARGET_NATIVE = ../../tests/test_engine
TARGET_WASM = ../../software/web/engine.wasm

all: $(TARGET_NATIVE) wasm

$(TARGET_NATIVE): crossword_engine.c ../../tests/test_engine.c
	$(CC) $(CFLAGS) crossword_engine.c ../../tests/test_engine.c -o $(TARGET_NATIVE)

test: $(TARGET_NATIVE)
	$(TARGET_NATIVE)

wasm: crossword_engine.c
	mkdir -p ../../software/web
	$(CLANG) $(WASM_FLAGS) -o $(TARGET_WASM) crossword_engine.c

clean:
	rm -f $(TARGET_NATIVE) $(TARGET_WASM)

.PHONY: all test wasm clean

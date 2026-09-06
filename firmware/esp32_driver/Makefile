CC = gcc
CFLAGS = -Wall -Wextra -O2 -Iinclude -I../engine
LDFLAGS = 

SRCS = src/main.c \
       src/mux_driver.c \
       src/pn532_driver.c \
       src/tile_mapper.c \
       src/grid_scanner.c \
       ../engine/crossword_engine.c

BIN_DIR = bin
TARGET = $(BIN_DIR)/bench_driver

.PHONY: all clean test

all: $(TARGET)

$(TARGET): $(SRCS)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) $(SRCS) -o $(TARGET) $(LDFLAGS)
	@echo "Built $(TARGET) successfully."

test: $(TARGET)
	@./$(TARGET) test

clean:
	rm -rf $(BIN_DIR)

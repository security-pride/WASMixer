CC=/Users/ping/PL/wasi-sdk/bin/clang

ORIGIN=origin
FLATTEN=flatten
ALIAS_DISRUPTION=alias_disruption

CFLAGS += --sysroot=/Users/ping/PL/wasi-sdk/share/wasi-sysroot

SRCS =$(wildcard *.c)
# OBJS =$(patsubst %.c,%.wasm,$(SRCS))
ORIGIN_WATOBJECTS =$(patsubst %.wat,%.wasm,$(wildcard $(ORIGIN)/*.wat))
OBFUSCTATED_WATOBJECTS =$(patsubst %.wasm,%.wat,$(wildcard $(OBFUSCATED)/*.wasm))
ORIGIN_WASM := $(addprefix $(ORIGIN)/,$(notdir $(SRCS:.c=.wasm)))

FLATTEN_WASM := $(addprefix $(FLATTEN)/,$(notdir $(SRCS:.c=.wasm)))
ALIAS_DISRUPTION_WASM := $(addprefix $(ALIAS_DISRUPTION)/,$(notdir $(SRCS:.c=.wasm)))

.PHONY: compile, convert, clean
compile: $(ORIGIN_WASM) $(FLATTEN_WASM) $(ALIAS_DISRUPTION_WASM)

$(ORIGIN)/%.wasm: %.c
	$(CC) $(CFLAGS) $< -O0 -o $@

$(FLATTEN)/%.wasm: %.c
	$(CC) $(CFLAGS) $< -O0 -o $@

$(ALIAS_DISRUPTION)/%.wasm: %.c
	$(CC) $(CFLAGS) $< -O0 -o $@

convert: $(ORIGIN_WATOBJECTS) $(OBFUSCTATED_WATOBJECTS)

$(ORIGIN)/%.wasm: $(ORIGIN)/%.wat
	wat2wasm  $< --enable-annotations -o $@

$(OBFUSCATED)/%.wat: $(OBFUSCATED)/%.wasm
	wasm2wat $< -o $@

clean:
	rm -rf $(ORIGIN)
	rm -rf $(FLATTEN)
	rm -rf $(ALIAS_DISRUPTION)

	mkdir $(ORIGIN)
	mkdir $(FLATTEN)
	mkdir $(ALIAS_DISRUPTION)
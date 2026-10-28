.PHONY: pico2-evidence
pico2-evidence:
	@mkdir -p evidence
	@printf 'source=%s\nversion=%s\nconfig=%s\nconfig_header=%s\ntarget=%s\nflash_kib=%s\n' "$$(git rev-parse HEAD)" '$(FC_VER)' '$(CONFIG)' '$(CONFIG_HEADER_FILE)' '$(TARGET)' '$(TARGET_FLASH_SIZE)' > evidence/build.txt
	$(CROSS_CC) $(CFLAGS) -dM -E -x c src/main/platform.h > evidence/macros.txt
	$(CROSS_CC) $(CFLAGS) -E -P -x c src/main/pg/gyrodev.c > evidence/gyrodev.i
	$(CROSS_CC) $(CFLAGS) -E -P -x c src/main/pg/bus_spi.c > evidence/bus_spi.i
	$(ARM_SDK_PREFIX)nm $(TARGET_ELF) > evidence/symbols.txt
	$(PICOTOOL) info -a $(TARGET_UF2) > evidence/picotool.txt

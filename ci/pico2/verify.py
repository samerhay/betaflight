"""Validate the actual compiler environment, linked driver, and UF2 container."""
import hashlib
import json
from pathlib import Path
import struct

evidence = Path('evidence')
build = dict(line.split('=', 1) for line in (evidence / 'build.txt').read_text().splitlines())
assert build['source'] == '6dbc4218fd6bc33bf16ea32c670304d4f89321d5', build
assert build['version'] == '2026.6.1', build
assert build['target'] == 'RP2350A', build
assert build['config'] == 'PICO2_MPU6500', build
assert build['flash_kib'] == '4096', build
macros = {}
for line in (evidence / 'macros.txt').read_text().splitlines():
    if line.startswith('#define '):
        parts = line[8:].split(maxsplit=1)
        macros[parts[0]] = parts[1] if len(parts) > 1 else ''
for name in ['USE_CONFIG', 'USE_CONFIG_SOURCE', 'TARGET_VALIDATECONFIG', 'RP2350A', 'USE_ACC', 'USE_GYRO', 'USE_SPI_GYRO',
             'USE_ACC_SPI_MPU6500', 'USE_GYRO_SPI_MPU6500', 'USE_GYRO_EXTI']:
    assert name in macros, name
assert 'RP2350B' not in macros
for name, value in {
    'PICO_RP2350A': '1', 'PICO_FLASH_SIZE_BYTES': '4194304',
    'BOARD_NAME': 'PICO2_MPU6500', 'FC_TARGET_MCU': 'RP2350A',
    'SPI0_SCK_PIN': 'PA18', 'SPI0_SDI_PIN': 'PA16', 'SPI0_SDO_PIN': 'PA19',
    'GYRO_1_SPI_INSTANCE': 'SPI0', 'GYRO_1_CS_PIN': 'PA17',
    'GYRO_1_EXTI_PIN': 'PA20', 'GYRO_1_ALIGN': 'CW0_DEG',
}.items():
    assert macros.get(name) == value, (name, macros.get(name), value)
symbols = (evidence / 'symbols.txt').read_text()
for name in ['mpu6500SpiAccInit', 'mpu6500SpiGyroInit', 'targetValidateConfiguration']:
    assert name in symbols, f'Linked driver symbol missing: {name}'
files = list(Path('obj').glob('*PICO2_MPU6500*.uf2'))
assert len(files) == 1, files
uf2 = files[0]
data = uf2.read_bytes()
assert data and len(data) % 512 == 0
families = set()
blocks = []
for offset in range(0, len(data), 512):
    block = data[offset:offset + 512]
    magic0, magic1, flags, address, size, number, total, family = struct.unpack_from('<8I', block)
    assert (magic0, magic1) == (0x0A324655, 0x9E5D5157)
    assert struct.unpack_from('<I', block, 508)[0] == 0x0AB16F30
    assert 0 < size <= 476
    if flags & 0x2000:
        families.add(family)
    if not flags & 1:  # Ignore UF2 metadata/non-main-flash blocks.
        assert 0x10000000 <= address < address + size <= 0x10400000, hex(address)
    blocks.append((number, total))
assert 0xE48BFF59 in families, [hex(f) for f in families]  # RP2350 ARM secure
assert 0xE48BFF56 not in families  # RP2040
assert all(total == len(blocks) for _, total in blocks)
assert sorted(number for number, _ in blocks) == list(range(len(blocks)))
report = {'build': build, 'uf2': uf2.name, 'bytes': len(data),
          'blocks': len(blocks), 'families': [hex(f) for f in sorted(families)],
          'sha256': hashlib.sha256(data).hexdigest(),
          'checks': 'release, custom config, RP2350A, 4MB flash, SPI0 pins, ACC/GYRO drivers, UF2 structure'}
(evidence / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))

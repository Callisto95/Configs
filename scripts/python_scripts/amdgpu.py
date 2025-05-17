import sys
from enum import IntEnum
from dataclasses import dataclass


def hex_pad(value: int, length: int) -> str:
	length += 2 # 0x offset
	return f"{value:#0{length}x}"


class PPFeatureMask(IntEnum):
	PP_SCLK_DPM_MASK = 0x1
	PP_MCLK_DPM_MASK = 0x2
	PP_PCIE_DPM_MASK = 0x4
	PP_SCLK_DEEP_SLEEP_MASK = 0x8
	PP_POWER_CONTAINMENT_MASK = 0x10
	PP_UVD_HANDSHAKE_MASK = 0x20
	PP_SMC_VOLTAGE_CONTROL_MASK = 0x40
	PP_VBI_TIME_SUPPORT_MASK = 0x80
	PP_ULV_MASK = 0x100
	PP_ENABLE_GFX_CG_THRU_SMU = 0x200
	PP_CLOCK_STRETCH_MASK = 0x400
	PP_OD_FUZZY_FAN_CONTROL_MASK = 0x800
	PP_SOCCLK_DPM_MASK = 0x1000
	PP_DCEFCLK_DPM_MASK = 0x2000
	PP_OVERDRIVE_MASK = 0x4000
	PP_GFXOFF_MASK = 0x8000
	PP_ACG_MASK = 0x10000
	PP_STUTTER_MODE = 0x20000
	PP_AVFS_MASK = 0x40000
	PP_GFX_DCS_MASK = 0x80000


if len(sys.argv) == 2:
	mask = int(sys.argv[1], 16)
else:
	with open("/sys/module/amdgpu/parameters/ppfeaturemask") as file:
		mask = int(file.readline(), 16)


@dataclass
class Result:
	state: str
	name: str
	value: int


longest_name = 0
results: list[Result] = []

for value in PPFeatureMask:
	results.append(Result("+" if value & mask == value else "-", value.name, value))
	
	if len(value.name) > longest_name:
		longest_name = len(value.name)


mask_length = 32 // 8 * 2
print(f"using {hex_pad(mask, mask_length)}")
for res in results:
	print(res.state, end=" ")
	
	print(res.name, end="")
	print(" " * (longest_name - len(res.name)), end=" ")
	
	print(hex_pad(res.value, mask_length))

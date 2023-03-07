import pyvesc
from operator import attrgetter
from dataclasses import dataclass
import math

@dataclass
class SysState:
	sys_voltage: float
	sys_current: float

	motor_current: float
	motor_rpm: float

	@property
	def motor_power(self): 
		return self.sys_voltage * self.motor_current

	@property
	def sys_power(self): 
		return self.sys_voltage * self.sys_current

	@property
	def motor_angvel(self): 
		return self.motor_rpm * (math.pi * 2.0 / 60.0)

class ESC():
	def __init__(self, port : str):
		pass

	def __enter__(self):
		return self

	def __exit__(self, *args):
		pass

	def read_state(self) -> SysState:
		pass

	def write_rpm(self, rpm : float):
		pass

class DummyESC(ESC):
	def __init__(self, port : str):
		super().__init__(port)
		self.rpm = 0

	def __enter__(self):
		print("dummy esc start")
		return super().__enter__()

	def __exit__(self, *args):
		print("dummy esc stop")
		pass

	def read_state(self) -> SysState:
		print(f"dummy esc read state {SysState(0, 0, 0, self.rpm)}")

		return SysState(0, 0, 0, self.rpm)

	def write_rpm(self, rpm : float):
		print(f"dummy esc write rpm {rpm}")

		self.rpm = rpm

class VESC(pyvesc.VESC):
	def read_state(self) -> SysState:
		vesc_state = super.get_measurements()

		return SysState(
				sys_voltage=vesc_state.v_in,
				sys_current=vesc_state.avg_input_current,
				motor_current=vesc_state.avg_motor_current,
				motor_rpm=vesc_state.rpm
			)

	def write_rpm(self, rpm : float):
		super.set_rpm(rpm)
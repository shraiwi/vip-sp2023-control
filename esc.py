import pyvesc
from operator import attrgetter
from dataclasses import dataclass
import math, time, os, threading

from pyvesc.protocol.base import VESCMessage
from pyvesc.protocol.interface import encode
from pyvesc.VESC.messages import VedderCmd, Alive

class VESCReboot(metaclass=pyvesc.protocol.base.VESCMessage):
	id = VedderCmd.COMM_REBOOT
	fields = []

vescreboot_msg = encode(VESCReboot())
alive_msg = encode(Alive())

@dataclass
class SysState:
	sample_time : float

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

class LoggerThread(threading.Thread):
	def __init__(self, esc):
		super().__init__()
		self.esc = esc
		self._stop_event = threading.Event()

	def stop(self):
		self._stop_event.set()

	def run(self):
		while not self._stop_event.is_set():
			if (state := self.esc.read_state()) is not None:
				self.esc.data.append(state)
			time.sleep(1 / ESC.DATA_RATE_HZ)
			

class ESC():
	DATA_RATE_HZ = 10

	def __init__(self, serial_port : str):
		# append from self.read_state() in new thread at ESC.DATA_RATE_HZ
		self.data = []

	def __enter__(self):
		# start thread here
		self.start_time = time.time()
		self.logger_thread = LoggerThread(self)
		self.logger_thread.start()
		return self

	def __exit__(self, *args):
		# stop thread here
		self.logger_thread.stop()
		pass

	def get_csv(self, *props):
		get_props = attrgetter(*props)
		yield "# " + ",".join(props)
		for row in self.data:
			if isinstance(row, SysState):
				yield ",".join(map(str, get_props(row)))
			elif isinstance(row, tuple):
				time, cmd = row
				yield f"# ({time}) \"{cmd}\""

	def get_time(self):
		return time.time() - self.start_time

	def read_state(self) -> SysState:
		raise Exception("not implemented")

	def write_rpm(self, rpm : int):
		self.data.append((self.get_time(), f"write_rpm {rpm}"))

	def write_duty(self, duty : float):
		self.data.append((self.get_time(), f"write_duty {duty}"))

class DummyESC(ESC):
	def __init__(self, serial_port : str):
		super().__init__(serial_port)
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

	def write_rpm(self, rpm : int):
		super().write_rpm(rpm)

		print(f"dummy esc write rpm {rpm}")

		self.rpm = rpm

	def write_duty(self, duty : float):
		super().write_duty(duty)

		print(f"dummy esc write duty {duty}")

class VESC(ESC):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.vesc = pyvesc.VESC(*args, **kwargs)

	def __enter__(self):
		return super().__enter__()

	def __exit__(self, *args, **kwargs):
		self.vesc.__exit__(*args, **kwargs)
		return super().__exit__(*args, **kwargs)

	def read_state(self) -> SysState:
		vesc_state = self.vesc.get_measurements()

		if vesc_state is None: return None

		sys_state = SysState(
			sample_time=super().get_time(),
			sys_voltage=vesc_state.v_in,
			sys_current=vesc_state.avg_input_current,
			motor_current=vesc_state.avg_motor_current,
			motor_rpm=vesc_state.rpm
		)

		return sys_state

	def write_rpm(self, rpm : int):
		super().write_rpm(rpm)
		self.vesc.set_rpm(int(rpm))

	def write_duty(self, duty : float):
		duty = min(max(duty, 0.0), 1.0)
		super().write_duty(duty)
		self.vesc.set_duty_cycle(duty)
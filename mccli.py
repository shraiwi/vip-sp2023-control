import sys, time, esc, dyno
from datetime import datetime

class ExitCommandError(BaseException):
	pass

def get_csv_name():
	return datetime.now().strftime(r"mccli_%m_%d_%Y_%H:%M:%S.csv")

def prog_bar(p : float, width : int = 40):
	n = int(p * width)
	return f"{int(p * 100)}% [{'#'*n + ' '*(width-n)}]"

def cmd_help():
	global COMMANDS
	print("available commands:")
	for command in COMMANDS.keys():
		print(f"\t{command}")

def cmd_exit():
	raise ExitCommandError()

def cmd_wait(seconds):
	print(f"waiting for {seconds} seconds...")
	time.sleep(seconds)

SWEEP_UPDATE_RATE = 20

COMMANDS = {
	# "command name": (method to be called, 1st arg parser, 2nd arg parser, etc...)
	"help": (cmd_help,),
	"wait": (cmd_wait, float,),
	"exit": (cmd_exit,),
}

if __name__ == "__main__":
	print(f"motor control command line interface")

	if "-h" in sys.argv or "--help" in sys.argv or len(sys.argv) != 3:
		print(f"\tusage: {sys.argv[0]} {{esc com port}} {{dyno com port}}")
		sys.exit(0)

	esc_port, dyno_port = sys.argv[1:]

	mkesc = esc.DummyESC if esc_port == "-" else esc.VESC
	mkdyno = dyno.DummyDyno

	with mkesc(serial_port=esc_port) as esc_obj, mkdyno(dyno_port) as dyno_obj:
		print(f"\tesc port: {esc_port}\n\tdyno port: {dyno_port}")

		def cmd_sweep_duty(duty_start, duty_end, duration):
			time_start = time.time()
			time_end = time_start + duration

			esc_obj.write_duty(duty_start)

			while (t := time.time()) < time_end:

				prog = (t - time_start) / duration
				duty = prog * (duty_end - duty_start) + duty_start

				print(f"\rduty={duty:.3f} {prog_bar(prog)}", end='')
				esc_obj.write_duty(duty)

				time.sleep(1 / SWEEP_UPDATE_RATE)

			esc_obj.write_duty(duty_end)

			print("\nsweep complete.")


		print(f"initialization ok, registering new commands...")
		COMMANDS.update({
			"set_rpm": (esc_obj.write_rpm, int),
			"set_duty": (esc_obj.write_duty, float),
			"sweep_duty": (cmd_sweep_duty, float, float, float),
			"print_state": (lambda: print(esc_obj.read_state()),),
		})

		while True:
			try:
				try: user_command = input("\r> ").strip()
				except EOFError:
					print("eof reached, exiting...")
					sys.exit(0)

				if len(user_command) == 0 or user_command.startswith("#"): continue

				for command_name, (fn, *arg_parsers) in COMMANDS.items():
					if user_command.startswith(command_name):
						user_args = user_command.removeprefix(command_name).split()
						if len(user_args) != len(arg_parsers):
							print(f"expected {len(arg_parsers)} args, got {len(user_args)}")
						else:
							parsed_args = []

							for arg_parser, user_arg in zip(arg_parsers, user_args):
								parsed_args.append(arg_parser(user_arg))

							try:
								fn(*parsed_args)
							except ExitCommandError:
								raise ExitCommandError()
							except Exception as ex:
								print(f"error {ex} occured while running command \"{user_command}\"")

							break
				else:
					print("no matching command found!")

			except KeyboardInterrupt:
				print("\nkeyboard interrupt, exiting...")
				# todo: add exit cleanup
				break
			except ExitCommandError:
				print("\nexiting...")
				break

		fpath = get_csv_name()
		with open(fpath, "w") as f:
			FIELDS = ("sample_time", "motor_angvel", "motor_power")
			print(f"writing fields {FIELDS} to {fpath}")
			f.write("\n".join(esc_obj.get_csv(*FIELDS)))


import sys, time, esc, dyno

class ExitCommandError(BaseException):
	pass

def cmd_exit():
	raise ExitCommandError()

def cmd_add(a, b):
	print(f"{a} + {b} = {a+b}")

def cmd_wait(seconds):
	print(f"waiting for {seconds} seconds...")
	time.sleep(seconds)

COMMANDS = {
	# "command name": (method to be called, 1st arg parser, 2nd arg parser, etc...)
	"add": (cmd_add, float, float,),
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

	with mkesc(esc_port) as esc_obj, mkdyno(dyno_port) as dyno_obj:
		print(f"\tesc port: {esc_port}\n\tdyno port: {dyno_port}")

		print(f"initialization ok, registering new commands...")
		COMMANDS.update({
			"set_rpm": (esc_obj.write_rpm, float),
			"read_state": (esc_obj.read_state,),
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

							fn(*parsed_args)
							break
				else:
					print("no matching command found!")

			except KeyboardInterrupt:
				print("\nkeyboard interrupt, exiting...")
				# todo: add exit cleanup
				sys.exit(0)
			except ExitCommandError:
				print("\nexiting...")
				sys.exit(0)



import sys

from pyvesc import PyVESC

def add(a, b):
	print(f"{a} + {b} = {a+b}")

COMMANDS = {
	# "command name": (method to be called, 1st arg parser, 2nd arg parser, etc...)
	"add": (add, float, float),
}

if __name__ == "__main__":
	print(f"motor control command line interface")

	if "-h" in sys.argv or "--help" in sys.argv or len(sys.argv) != 3:
		print(f"\tusage: {sys.argv[0]} {{vesc com port}} {{dyno com port}}")
		sys.exit(0)

	vesc_port, dyno_port = sys.argv[1:]

	print(f"\tvesc port: {vesc_port}\n\tdyno port: {dyno_port}")

	while True:
		try:
			user_command = input("> ")
		except KeyboardInterrupt:
			print("\nkeyboard interrupt, exiting...")
			# todo: add exit cleanup
			sys.exit(0)

		for command_name, (fn, *arg_parsers) in COMMANDS.items():
			if user_command.startswith(command_name):
				str_args = user_command.removeprefix(command_name).split()
				fn(*(arg_parser(str_arg) for arg_parser, str_arg in zip(arg_parsers, str_args)))


		pass

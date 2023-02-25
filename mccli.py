import sys, time
from pyvesc import VESC

def add(a, b):
	print(f"{a} + {b} = {a+b}")

def wait(seconds):
	if seconds == 1:
		print(f"waiting for one second...")
	else:
		print(f"waiting for {seconds} seconds...")
	time.sleep(seconds)

COMMANDS = {
	# "command name": (method to be called, 1st arg parser, 2nd arg parser, etc...)
	"add": (add, str, str),
	"wait": (wait, float),
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

		except KeyboardInterrupt:
			print("\nkeyboard interrupt, exiting...")
			# todo: add exit cleanup
			sys.exit(0)


		pass

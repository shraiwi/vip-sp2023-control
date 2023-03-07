
class DummyDyno:
	def __init__(self, port : str):
		pass

	def __enter__(self):
		print("dummy dyno start")
		return self

	def __exit__(self, *args):
		print("dummy dyno stop")
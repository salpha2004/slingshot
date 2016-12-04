import os
import sys
from threading import Timer
from subprocess import Popen, PIPE

class I386Emul(object):
	qemu = None

	def __init__(self, work_dir):
		self.work_dir = work_dir

	def _parse_output(self, output_line):
		'''
		parses the emulator's output line by line for the result of test cases' execution.
		stores the result on the database.
		returns 0 if the execution process has finished (no more test cases).
		returns 1 otherwise.
		'''
		print output_line

	def _run_qemu(self):
		arch = os.environ['RTEMS_MAKEFILE_PATH'].split('/')[-1]
		testsuite_bin_path = os.path.join (self.work_dir, '_compiled',
					arch, 'bin', 'testsuite')
		self.qemu = Popen (['qemu-system-i386',
					'-kernel',
					testsuite_bin_path,
					'-append',
					'--console=/dev/com1',
					'-serial',
					'stdio'],
					stdin = PIPE,
					stdout = PIPE,
					stderr = PIPE)

	def _testcase_execution_time_out(self):
		print "__TIMEOUT__"
		self.qemu.terminate()

	def _execute(self, testcase):
		line = self.qemu.stdout.readline()
		while "next testcase?" not in line:
			line = self.qemu.stdout.readline()
		self.qemu.stdin.write(testcase.get_name() + '\n')
		line = self.qemu.stdout.readline()
		while "result" not in line:
			t = Timer(5, self._testcase_execution_time_out)
			t.start()
			line = self.qemu.stdout.readline()
			# if qemu was terminated it means the execution timed out...
			if self.qemu.poll() is not None:
<<<<<<< HEAD
				line = testcase.get_name() + " result: CATASTROPHIC/ABORT\n"
=======
				line = testcase.get_name() + " result: CATASTROPHIC\n"
>>>>>>> 1653216d8cad6675132c597a682179af28cb601d
				t.cancel()
				break
			t.cancel()
		self._parse_output(line)

	def execute_tests(self, testcases):
		while testcases:
			# if qemu is not running...
			if self.qemu is None or self.qemu.poll() is not None:
				self._run_qemu()
			self._execute(testcases.pop(0))
		# if qemu was not terminated...
		if self.qemu.poll() is None:
			self.qemu.terminate()

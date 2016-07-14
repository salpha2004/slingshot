import subprocess
import sys
import os
import re
import string

class TestsuiteExecuter(object):

 	def __init__(self, work_dir):
		self.work_dir = work_dir

	def _goto_testcase_after(self, crashed_tc_name):
		""" 
		TODO: currently this method only moves the CURRENT_TC one line
		lower in the test suite template. in the future after using
		rtems libdl, it should dynamically load the next test case.
		"""
		ts_src_path = os.path.join(self.work_dir, 'testcase_executer.cpp')
		new_ts = os.path.join(self.work_dir, 'testcase_executer.cpp.new')
		with open (ts_src_path) as test_suite:
			with open (new_ts, 'w') as new_test_suite:
				for line in test_suite:
					if "CURRENT_TC:" not in line:
						if crashed_tc_name in line:
							new_test_suite.write(line)
							new_test_suite.write("CURRENT_TC:\n")
							# change crashed_tc_name to some strange thing so it doesn't match again.
							crashed_tc_name = "<<<<<<<<<<"
						else:
							new_test_suite.write(line)
		os.remove(ts_src_path)
		os.rename(new_ts, ts_src_path)

	def execute(self):
		ts_bin_path = os.path.join(self.work_dir, 'o-optimize/test-program.exe')
		emulator = subprocess.Popen(['sparc-rtems4.12-run', ts_bin_path],
			stdout = subprocess.PIPE)
		output = emulator.communicate()[0]
		tc_crashed = False;
		# interpret resutls (TODO: replace with a separate func)
		""" sample emulator output:
		TC_abs_1 Started...
		TC task creation: RTEMS_SUCCESSFUL
		TC task start: RTEMS_SUCCESSFUL
		TC_abs_1: PASS

		TC_tan_1 Started...
		TC task creation: RTEMS_SUCCESSFUL
		TC task start: RTEMS_SUCCESSFUL
		Unexpected trap ( 4) at address 0x02001488
		fp disabled
		"""
		tc_begin = re.findall (r".* Started\.\.\.", output) # TODO: might be a hot spot!
		tc_fin = re.findall (r".*: PASS|RESTART", output)
		for tc in tc_begin:
			token = tc.split()
			tc_name = token[0]
			''' if the test case name is found in tc_fin, it was executed properly.
			otherwise it's a crash. '''
			found = [t for t in tc_fin if tc_name in t]
			if found:
				print "{0}".format(found[0]) # TODO: write PASS or RESTART in db.
			else: # if any test case found that has no finish status, it has crashed.
				tc_crashed = True
				break
		if tc_crashed == True:
			print "{0} CRASH".format(tc_name)
			self._goto_testcase_after(tc_name) # change the goto label in the test program template.
			# TODO: write crash report in db.
			return 1
		return 0

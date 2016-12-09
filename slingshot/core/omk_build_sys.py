import os
import sys
import subprocess

class OMK(object):

	def __init__(self, work_dir):
		self.work_dir = work_dir

	def _make(self, cmd, jobs):
		# store current dir to go back at the end.
		original_work_dir = os.getcwd()
		# go to working directory to invoke "make".
		os.chdir (self.work_dir)
		make_log = open(os.path.join(self.work_dir, 'makefile.log'), 'a')
		if cmd == 'all':
			make_proc = subprocess.Popen(["make", "-j", str(jobs)],
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
			out = make_proc.communicate()[0]
			for line in out:
				sys.stdout.write(line)
				make_log.write(line)
		if cmd == 'clean':
			make_proc = subprocess.Popen(["make", "clean", "-j", str(jobs)],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE)
			make_proc.communicate()
		make_log.close()
		# go back to the previous work dir.
		os.chdir(original_work_dir)
		return make_proc.returncode;

	def _get_obj_path(self, obj_name):
		arch = os.environ['RTEMS_MAKEFILE_PATH'].split('/')[-1]
		return os.path.join (self.work_dir, '_build', arch, 'user', obj_name + '.o')

	def _link_tc_and_setting_objs(self, tc_list):
		toolset = os.environ['RTEMS_MAKEFILE_PATH'].split('/')[-2]
		linker = toolset + '-ld'
		rootfs_path = os.path.join(self.work_dir, 'rootfs')
		for tc in tc_list:
			tc_final_obj_path = os.path.join(rootfs_path, tc.get_name() + '.o')
			all_settings = []
			for setting in tc.get_settings():
				all_settings.append (self._get_obj_path(setting.get_name()))
			link_proc = subprocess.Popen([linker,
				'-r',
				'-o',
				tc_final_obj_path,
				self._get_obj_path(tc.get_name())] +
				all_settings,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE)
			err = link_proc.communicate()[1]
			if link_proc.returncode != 0: # exit if make fails for any test case.
				print err
				return -1
		return 0

	def make_all(self, tc_list, jobs):
		'''
		the OMK procedure to put the test cases' object files in
		the final executable for dynamic linking, is as following:
		1. 'make all' source codes (test cases + test executor).
		2. [only for Slingshot]: combine the test case obj file with
		the corresponding setting file.
		3. put the obj files in 'rootfs' dir.
		4. 'make clean'
		5. 'make all' again. then objs in 'rootfs' will be put in the final exec.
		'''
		print "\n\nFirst make..."
		if self._make(cmd='all', jobs=jobs) != 0:
			return -1 # error
		print "\n\nLinking test case obj and setting obj..."
		if self._link_tc_and_setting_objs(tc_list) != 0:
			return -1
		# make clean and...
		self._make(cmd='clean', jobs=jobs)
		# ...make again to put the newly created objects (under 'rootfs') in the final binary
		print "\n\nFinal make..."
		if self._make(cmd='all', jobs=jobs) != 0:
			return -1 # error
		return 0 # success

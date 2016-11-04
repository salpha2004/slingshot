import logging
import os
import random
import shutil
import subprocess
import sys
from sets import Set
from util import get_path


class TcGenerator(object):

    def __init__(self, database, tc_factory, setting_factory,
            work_dir, batch_size=2):

        # batch_size specifies the number of testcases returned by generate
        self.batch_size = batch_size

        # connection to the database
        self.db = database

        # Number of testcases needed to completely test this function
        self.remaining_tcs = 0

        # Get logger
        self.logger = logging.getLogger(__name__)

        # Set working directory for file creation, compilation
        self.work_dir = work_dir

        # Factory for testcases
        self.tc_factory = tc_factory

        # Factory for settings
        self.s_factory = setting_factory

        # function record
        self.function = None
        self.testcases = None
        self.testcases_iter = None
        self.created_setting_ids = []
        self.all_settings = Set()
        self.compiled_settings = []

    # this modules generates dynamic parts of testcase_executer.
    # static parts are added in the end by "finalize_testcase_generation"
    # (defined in slingshot.py).



    def _gen_testcase_executer(self, tc_batch):
      # file path and name for the final generated testcase_executer.h
      h_file = os.path.join(self.work_dir, "testcase_executer.h")

      # generate testcase_executer.h.
      with open(h_file, "a") as f:
        for tc in tc_batch:
          f.write("#include \"{0}.h\"\n".format(tc.get_name()))
      


    def _gen_Makefile_testcase(self, tc_batch):
      # Makefile filename.
      makefileomk_file = os.path.join(self.work_dir, "Makefile.omk")
      
      with open(makefileomk_file, "a") as f:
        for tc in tc_batch:
          f.write("testsuite_SOURCES += {0}.c\n".format(tc.get_name()))



    def _gen_Makefile_settings(self):
      # Makefile filename.
      makefile_file = os.path.join(self.work_dir, "Makefile_settings")
      
      with open(makefile_file, "a") as f:
        for setting in self.all_settings:
          f.write("testsuite_SOURCES += {0}.c\n".format(setting.get_name()))
 
      

    def _reset(self):
        """ Resete all class members and delete generated files """

        self.function = None
        self.testcases_iter = None
        self.testcases = None
        self.remaining_tcs = 0
        self.created_setting_ids = []
        self.all_settings = Set()



    def load_function(self, function):
        """ Load function into testcase generator.

        Args:
            function: Function which is loaded as a named Function tuple.

        """

        self._reset()
        self.function = function
        self.testcases = self.db.get_testcases(self.function.signature)
        self.remaining_tcs = len(self.testcases)
        self.logger.info("Loaded function {}. {} testcases found.".format(
            self.function.name, self.remaining_tcs))
        self.testcases_iter = iter(self.testcases)



    def testcases_left(self):
        """ Check if there are remaining testcases for this function.

        Returns:
            True if there are remaining testcases, False otherwise.

        """
        return self.remaining_tcs > 0



    def _next_testcase_batch(self):
        """ Get the next batch of testcases.

        Args:
            testcase_iter: Iterator object over the testcase tuple.

        Returns:
            A list containing self.batch_size tuples. In which each tuple
            represents a testcase.

        """
        tc_batch = []
        while len(tc_batch) < self.batch_size:
            try:
                testcase = self.testcases_iter.next()
                tc_batch.append(testcase)
                self.remaining_tcs -= 1
            except StopIteration:
                break
        return tc_batch



    def _create_settings(self, setting_ids):
        """ Create setting objects for the given setting ids.

        Args:
            setting_ids: Tuple contining setting ids

        Returns:
            A list of setting objects.

        """
        setting_obj = []
        for setting_id in setting_ids:
            if setting_id in self.created_setting_ids:
                # Get object from created_setting_ids
                setting_obj.append(self._get_setting(setting_id))
            else:
                setting_obj.append(self.s_factory.create_setting(
                    setting_id, self.work_dir))

        return setting_obj



    def _get_setting(self, setting_id):
        for setting in self.all_settings:
            if setting.get_id() == setting_id:
                return setting



    def generate(self):
        """ Generate 'batch_size' testcases from the set of remaining
        testcases. """
        
        tc_batch = self._next_testcase_batch()
        # Generate all testcases in this batch
        testcases = []
        for testcase in tc_batch:
          testcase_id, setting_ids = testcase[0], testcase[1:]
          settings = self._create_settings(setting_ids)
          for s in settings:
              s.generate_files()
              self.created_setting_ids.append(s.get_id)
              self.all_settings.add(s)
          tc = self.tc_factory.create_testcase(self.function,
                  testcase_id, settings)
          tc.generate_files()
          testcases.append(tc)

        # for each test case, an entry should be appended to testcase_executer.h
        self._gen_testcase_executer(testcases)
        # for each test case, an entry should be appended to Makefile
        self._gen_Makefile_testcase(testcases)
        """ for each test case, corresponding settings entry should be
        appended to Makefile. duplicated entries would be removed
        in the end. """
        self._gen_Makefile_settings()

        # it'd be used by OMK to link test cases along with their settings in a single obj
        return testcases;



    def finalize_testcase_generation(self):
        # finalize header file generation
        h_file = os.path.join(self.work_dir, "testcase_executer.h")
        with open(h_file, "a") as f:
          f.write("\n")
          f.write("bool tc_finished = false;\n")
        
        # finalize Makefile generation
        makefileomk_file = os.path.join(self.work_dir, "Makefile.omk")
        """
        since settings are common among test cases, Makefile_settings contains
        duplicated entries for settings CPP files. we have to apply "sort"
        and "uniq", Linux commands, to remove duplicates.
        """
        makefile_settings_file = os.path.join(self.work_dir, "Makefile_settings")
        p1 = subprocess.Popen(["sort", makefile_settings_file], 
          stdout=subprocess.PIPE)
        p2 = subprocess.Popen("uniq", stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        output = p2.communicate()[0]
        with open(makefileomk_file, "a") as target_f:
          # add entries for settings CPP files:
          target_f.write(output)
          # add entry for testcase_executer.c:
          target_f.write("testsuite_SOURCES += testcase_executer.c\n")
          # concat Makefile.omk_tail to the Makefile.omk.
          with open(get_path('bin/Makefile.omk_tail')) as tail_f:
            target_f.write(tail_f.read())
        # remove Makefile_settings as it is temporary.
        os.remove(makefile_settings_file)
        
        """ copy values.h (which reside on /usr/include on Linux systems) to
        work_dir since it is included by test cases. """
        shutil.copy2(get_path("bin/values.h"), os.path.join(self.work_dir))
        shutil.copy2(get_path("bin/testcase_executer.c"), os.path.join(self.work_dir))
        shutil.copy2(get_path("bin/Makefile"), os.path.join(self.work_dir))
        shutil.copy2(get_path("bin/Makefile.rules"), os.path.join(self.work_dir))

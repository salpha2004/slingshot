#define CONFIGURE_INIT
#include <stdio.h>
#include <stdlib.h>
#include <rtems.h>
#include <sys/types.h>
#include <dlfcn.h>
#include <rtems/imfs.h>
#include <bsp.h>

#define CONFIGURE_APPLICATION_NEEDS_CONSOLE_DRIVER
#define CONFIGURE_APPLICATION_NEEDS_CLOCK_DRIVER
#define CONFIGURE_MAXIMUM_TASKS     4
#define CONFIGURE_MAXIMUM_SEMAPHORES  5
#define CONFIGURE_LIBIO_MAXIMUM_FILE_DESCRIPTORS 4
#define CONFIGURE_RTEMS_INIT_TASKS_TABLE
#include <rtems/confdefs.h>

#include "testcase_executer.h"

/* note: the default priority for Init task is 1 (the highest). */
#define TC_TASK_PRIORITY 2
#define TC_TIMEOUT_DIVISION_FACTOR 10
/* in microseconds. should be dividable by TC_TIMEOUT_DIVISION_FACTOR. */
#define TC_TIMEOUT 5000000

extern int _binary_rootfs_tarfile_start;
extern int _binary_rootfs_tarfile_size;
#define TARFILE_START _binary_rootfs_tarfile_start
#define TARFILE_SIZE _binary_rootfs_tarfile_size

typedef int (*tc_func_t)();

rtems_task runner (rtems_task_argument tc_name_arg)
{
  void* tc_handle;
  tc_func_t tc_call;
  int tc_call_ret;
  int status;
  char tc_obj_name [35];
  char* tc_name = (char*)tc_name_arg;

  status = rtems_tarfs_load("/", (uint8_t*)(&TARFILE_START), (long)&TARFILE_SIZE);
  printf ("tar decompress status: %d\n", status);

  strcpy (tc_obj_name, tc_name);
  strcat (tc_obj_name, ".o");
  tc_handle = dlopen (tc_obj_name, RTLD_NOW | RTLD_GLOBAL);
  if (!tc_handle)
  {
    printf ("dlopen failed: %s -- %s\n", dlerror(), tc_obj_name);
    exit(1);
  }

  tc_call = (tc_func_t)dlsym (tc_handle, tc_name);
  if (tc_call == NULL)
  {
    printf ("dlsym failed: symbol not found: %s\n", tc_name);
    exit(1);
  }

  tc_call_ret = tc_call();
  printf ("__errno: %d\n", tc_call_ret);

  dlclose (tc_handle);
  rtems_task_delete (RTEMS_SELF);
}

rtems_task Init (rtems_task_argument ignored)
{
  rtems_id runner_task_id;
  rtems_name runner_task_name = rtems_build_name( 'T', 'C', 'R', ' ');
  rtems_status_code status;
  char tc_name [30] = "TC_abs_";
  /* ********************************* TODO: get test case name and set tc_name accordingly ********************************* */
  /* ********************************* TODO: run test cases in a loop till the fin cmd ********************************* */
  status = rtems_task_create(runner_task_name, TC_TASK_PRIORITY,
                      RTEMS_MINIMUM_STACK_SIZE, RTEMS_DEFAULT_MODES,
                      RTEMS_DEFAULT_ATTRIBUTES | RTEMS_FLOATING_POINT,
                      &runner_task_id);
  printf ("Test case runner creation: %s\n",
          rtems_status_text (status));
  
  status = rtems_task_start (runner_task_id, runner, (rtems_task_argument)tc_name);
  printf ("Test case runner start: %s\n",
          rtems_status_text (status));

  for (int i=0; i<TC_TIMEOUT_DIVISION_FACTOR; i++)
  {
    status = rtems_task_wake_after(
      RTEMS_MICROSECONDS_TO_TICKS (TC_TIMEOUT/TC_TIMEOUT_DIVISION_FACTOR));
    if (tc_finished)
      break;
  }
  if (tc_finished)
    printf ("%s: PASS\n", tc_name);
  else
    printf ("%s: RESTART\n", tc_name);
  printf ("\n");

  /* signal end of the test program. */
  printf ("finito!\n");
  exit (0);
}

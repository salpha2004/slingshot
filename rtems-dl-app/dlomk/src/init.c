/* originally based on 'appdl' example by Pavel Pisa (git://rtime.felk.cvut.cz/rtems-devel.git)
 * modified by Saeed Ehteshamfar (https://devel.rtems.org/wiki/SOCIS/2016)
 */

#include <rtems.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>

#include <dlfcn.h>

#include <rtems/imfs.h>

#include <rtems/shellconfig.h>
#include <rtems/monitor.h>
#include <rtems/shell.h>

extern int _binary_rootfs_tarfile_start;
extern int _binary_rootfs_tarfile_size;
#define TARFILE_START _binary_rootfs_tarfile_start
#define TARFILE_SIZE _binary_rootfs_tarfile_size

typedef int (*call_t)();

rtems_task Init(
  rtems_task_argument ignored
)
{
  int res;
  void * handle;
  int    unresolved;
  char * message = "loaded";
  char   *call_file_name;
  char   *call_symbol = NULL;
  call_t call;
  int    call_ret;
  res = rtems_tarfs_load("/", (void*)(&TARFILE_START), (long)&TARFILE_SIZE);
  printf("rtems_tarfs_load returned %d\n", res);

  rtems_monitor_init(RTEMS_MONITOR_SUSPEND|RTEMS_MONITOR_GLOBAL);
//  rtems_shell_init("SHLL",RTEMS_MINIMUM_STACK_SIZE,
//              150, "/dev/console", true, true, NULL);

  handle = dlopen ("hello.o", RTLD_NOW | RTLD_GLOBAL);
  if (!handle)
  {
    printf("dlopen failed: %s\n", dlerror());
    exit(1);
  }
  if (dlinfo (handle, RTLD_DI_UNRESOLVED, &unresolved) < 0)
    message = "dlinfo error checking unresolved status";
  else if (unresolved)
    message = "has unresolved externals";

  call = dlsym (handle, "hello");
  if (call == NULL)
  {
    printf("dlsym failed: symbol 'hello' not found\n");
    return 1;
  }

  call_ret = call();
  printf ("ret val: %d\n", call_ret);
  printf( "*** END OF INIT ***\n" );
  exit(0);
}

/* configuration information */

#include <bsp.h>


#define CONFIGURE_LIBIO_MAXIMUM_FILE_DESCRIPTORS 32
#define CONFIGURE_MAXIMUM_TASKS 4
#define CONFIGURE_MINIMUM_TASK_STACK_SIZE (8U * 1024U)
#define CONFIGURE_EXTRA_TASK_STACKS (8 * 1024)
#define CONFIGURE_MAXIMUM_POSIX_KEYS             16
#define CONFIGURE_MAXIMUM_POSIX_KEY_VALUE_PAIRS  16

#define CONFIGURE_APPLICATION_NEEDS_NULL_DRIVER
#define CONFIGURE_APPLICATION_NEEDS_ZERO_DRIVER
#define CONFIGURE_USE_IMFS_AS_BASE_FILESYSTEM
#define CONFIGURE_FILESYSTEM_DOSFS
#define CONFIGURE_APPLICATION_NEEDS_CLOCK_DRIVER
#define CONFIGURE_APPLICATION_NEEDS_CONSOLE_DRIVER
#define CONFIGURE_APPLICATION_NEEDS_LIBBLOCK // for rtems shell.

#define CONFIGURE_INIT_TASK_PRIORITY    100
#define CONFIGURE_INIT_TASK_INITIAL_MODES (RTEMS_PREEMPT | \
                                           RTEMS_NO_TIMESLICE | \
                                           RTEMS_NO_ASR | \
                                           RTEMS_INTERRUPT_LEVEL(0))





#define CONFIGURE_RTEMS_INIT_TASKS_TABLE

#define CONFIGURE_INIT
#include <rtems/confdefs.h>

/* end of include file */

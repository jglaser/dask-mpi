import click
from mpi4py import MPI
from tornado.ioloop import IOLoop

from distributed.cli.utils import check_python_3

from dask_mpi.common import get_host_from_interface, start_scheduler, start_worker

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
loop = IOLoop()


@click.command()
@click.option('--scheduler-file', type=str, default='scheduler.json',
              help='Filename to JSON encoded scheduler information. ')
@click.option('--interface', type=str, default=None,
              help="Network interface like 'eth0' or 'ib0'")
@click.option('--nthreads', type=int, default=0,
              help="Number of threads per worker.")
@click.option('--memory-limit', default='auto',
              help="Number of bytes before spilling data to disk. "
                   "This can be an integer (nbytes) "
                   "float (fraction of total memory) "
                   "or 'auto'")
@click.option('--local-directory', default='', type=str,
              help="Directory to place worker files")
@click.option('--scheduler/--no-scheduler', default=True,
              help=("Whether or not to include a scheduler. "
                    "Use --no-scheduler to increase an existing dask cluster"))
@click.option('--nanny/--no-nanny', default=True,
              help="Start workers in nanny process for management")
@click.option('--bokeh-port', type=int, default=8787,
              help="Bokeh port for visual diagnostics")
@click.option('--bokeh-worker-port', type=int, default=8789,
              help="Worker's Bokeh port for visual diagnostics")
@click.option('--bokeh-prefix', type=str, default=None,
              help="Prefix for the bokeh app")
def main(scheduler_file, interface, nthreads, local_directory, memory_limit,
         scheduler, bokeh_port, bokeh_prefix, nanny, bokeh_worker_port):
    host = get_host_from_interface(interface)

    if rank == 0 and scheduler:
        start_scheduler(loop, host=host, scheduler_file=scheduler_file,
                        bokeh_port=bokeh_port, bokeh_prefix=bokeh_prefix)
    else:
        name = rank if scheduler else None
        start_worker(loop, host=host, name=name, scheduler_file=scheduler_file, nanny=nanny,
                     local_directory=local_directory, nthreads=nthreads, memory_limit=memory_limit,
                     bokeh_worker_port=bokeh_worker_port)


def go():
    check_python_3()
    main()


if __name__ == '__main__':
    go()

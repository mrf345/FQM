import os

from app.utils import find
from app.tasks.cache_tickets_tts import CacheTicketsAnnouncements
from app.tasks.delete_tickets import DeleteTickets


THREADS = {}
TASKS = [CacheTicketsAnnouncements, DeleteTickets]


def start_tasks(app=None, tasks=TASKS):
    ''' start all tasks in `TASKS`.

    Parameters
    ----------
        app: Flask app

    Returns
    -------
        List of running QThreads.
    '''
    if app:
        start_tasks.__dict__['APP'] = app
    else:
        app = start_tasks.__dict__['APP']

    if app.config.get('MIGRATION') or os.environ.get('DOCKER'):
        # FIXME: Tasks are disabled when `GUNICORN` is running. We should implement
        # a new tasks module with celery that works seemlessly alongside gunicorn.
        return THREADS

    for task in tasks:            
        if task.__name__ not in THREADS:
            new_thread = task(app)

            if new_thread.settings.enabled:
                THREADS[task.__name__] = new_thread
                THREADS[task.__name__].init()

                if not new_thread.quiet:
                    print(f'Starting task({task.__name__})...')

    return THREADS


def stop_tasks(tasks=[]):
    ''' stop all tasks in `tasks or TASKS`.

    Parameters
    ----------
        tasks: list
            list of task names to stop, if empty will stop all.
    '''
    threads = [i for i in THREADS.items() if i[0] in tasks]\
        if tasks else list(THREADS.items())

    for task, thread in threads:
        if not thread.quiet:
            print(f'Stopping task: {task} ...')

        thread.stop()
        THREADS.pop(task)


def get_task(task_name):
    ''' get a task if running.

    Parameters
    ----------
    task_name : str
        task name to find in list of running tasks.
    '''
    item = find(lambda i: i[0] == task_name, THREADS.items())

    return item and item[1]

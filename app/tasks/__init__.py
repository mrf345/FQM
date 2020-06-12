from app.tasks.tickets import CacheTicketsAnnouncements


TASKS = [CacheTicketsAnnouncements]
THREADS = {}


def start_tasks(app):
    ''' start all tasks in `TASKS`.

    Parameters
    ----------
        app: Flask app

    Returns
    -------
        List of running QThreads.
    '''
    for task in TASKS:
        if task.__name__ not in THREADS:
            THREADS[task.__name__] = task(app)
            THREADS[task.__name__].init()

    return THREADS


def stop_tasks(tasks=[]):
    ''' stop all tasks in `tasks or TASKS`.

    Parameters
    ----------
        tasks: list
            list of task names to stop, if empty will stop all.
    '''
    threads = []

    if tasks:
        threads += [i for i in THREADS.items() if i[0] in tasks]
    else:
        threads += THREADS.items()

    for task, thread in threads:
        if not thread.quiet:
            print(f'Stopping task: {task} ...')

        thread.stop()

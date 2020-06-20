import pickle
from time import time
from datetime import timedelta
from pathlib import Path
# import pathlib

from telegram.ext import Updater, Job
# Archive
# from threading import Event
# from time import time
# import pickle

"""
The following snippet pickles the jobs in the job queue periodically and on bot shutdown,
and unpickles and queues them again on startup. Since pickle doesn't support threading primitives,
therefore their values and states are extracted
(this information may change in the future, always check the Job documentation).

Note: Job is not yet safe for threads so eventually some special condition may occur.
In a previous example, the content of Job was modified which
resulted in some asynchronous processing errors; now the content of Job is
extracted without modifying it which is much more safe.
"""
# JOBS_PICKLE = 'job_tuples.pickle'
# PATH = Path.cwd()
FILE = Path.cwd() / 'job_tuples.pickle'
# FILE = 'job_tuples.pickle'
# FILE = PATH.parent / 'job_tuples.pickle'
print('FILE periodical save:\n ', FILE)
# JOBS_PICKLE = PATH

# pathlib.PurePosixPath
# WARNING: This information may change in future versions (changes are planned)
JOB_DATA = ('callback', 'interval', 'repeat', 'context', 'days', 'name', 'tzinfo')
JOB_STATE = ('_remove', '_enabled')


def load_jobs(jq):

    # w: open for writing, truncating the file first
    # b: binary mode
    # r: open for reading (default)
    with FILE.open(mode='rb') as fp:
        while True:
            try:
                # next_t, data, state = pickle.load(fp)
                next_t = pickle.load(fp)
                state = pickle.load(fp)
                data = pickle.load(fp)
            except EOFError:
                break  # loaded all jobs

            # New object with the same data
            job = Job(**{var: val for var, val in zip(JOB_DATA, data)})

            # Restore the state it had
            for var, val in zip(JOB_STATE, state):
                attribute = getattr(job, var)
                getattr(attribute, 'set' if val else 'clear')()

            job.job_queue = jq

            next_t -= time()  # convert from absolute to relative time

            jq._put(job, next_t)


def save_jobs(jq):

    print('JOB run_repeting as save pickle')
    
    with jq._queue.mutex:  # in case job_queue makes a change        
        if jq:
            job_tuples = jq._queue.queue
        else:
            job_tuples = []

        with FILE.open(mode='wb') as fp:
            print('First time run job save pickle')
        # with open(PATH, 'wb') as fp:
            for next_t, job in job_tuples:
                # This job is always created at the start
                if job.name == 'save_jobs_job':
                    continue

                # Threading primitives are not pickleable
                data = tuple(getattr(job, var) for var in JOB_DATA)
                state = tuple(getattr(job, var).is_set() for var in JOB_STATE)

                # Pickle the job
                pickle.dump((next_t, data, state), fp)


def save_jobs_job(context):
    save_jobs(context.job_queue)

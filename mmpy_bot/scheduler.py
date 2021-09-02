from datetime import datetime
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from typing import Optional

import schedule
from schedule import default_scheduler


class OneTimeJob(schedule.Job):
    # Override schedule.Job._schedule_next_run to avoid periodic job generation.
    def _schedule_next_run(self):
        pass

    def __repr__(self):
        txt = super().__repr__()
        # One time jobs always read "Every 0 None at ..."
        # due undefined self.interval (0) and self.unit (None)
        return txt.replace("Every 0 None", "Once")

    def set_next_run(self, next_time: datetime):
        if not isinstance(next_time, datetime):
            raise AssertionError("The next_time parameter should be a datetime object.")
        self.at_time = next_time
        self.next_run = next_time

    def run(self):
        super().run()
        return schedule.CancelJob()


def _default_scheduler_once(self, trigger_time: datetime):
    job = OneTimeJob(0, self)
    job.set_next_run(trigger_time)
    return job


def _run_job(self, job):
    """Overrides default_scheduler._run_job to support running the jobs in a separate
    process.

    Either way, this waits for the result in a dedicated thread to prevent blocking the
    event loop.
    """

    # Launch job in a dedicated process and send the result through a pipe.
    if "subprocess" in job.tags:

        def wrapped_run(pipe: Connection):
            result = job.run()
            pipe.send(result)

        pipe, child_pipe = Pipe()
        p = Process(target=wrapped_run, args=(child_pipe,))
        p.start()
        # This still blocks despite running in a subprocess
        result = pipe.recv()
    else:
        # Or simply run the job in this thread
        result = job.run()

    if isinstance(result, schedule.CancelJob) or result is schedule.CancelJob:
        self.cancel_job(job)


def _once(trigger_time: Optional[datetime] = None):
    """Adds support for scheduling one-time jobs to the default_scheduler."""
    if trigger_time is None:
        trigger_time = datetime.now()
    if not isinstance(trigger_time, datetime):
        raise AssertionError("The trigger_time parameter should be a datetime object.")
    return default_scheduler.once(self=default_scheduler, trigger_time=trigger_time)


# Monkey-Patching
default_scheduler.once = _default_scheduler_once
schedule.Scheduler._run_job = _run_job
schedule.once = _once

import schedule
from schedule import default_scheduler
from datetime import datetime


class OneTimeJob(schedule.Job):

    # override schedule.Job._schedule_next_run
    # to avoid periodic job genration
    def _schedule_next_run(self):
        pass

    def set_next_run(self, next_time):
        if not isinstance(next_time, datetime):
            raise AssertionError(
                "The next_time parameter should be a datetime object.")
        self.at_time = next_time
        self.next_run = next_time

    def run(self):
        try:  # py3+
            ret = super().run()
        except TypeError:  # py2.7
            ret = super(OneTimeJob, self).run()
        self.scheduler.cancel_job(self)
        return ret


def _default_scheduler__once(self, trigger_time):
    job = OneTimeJob(0, self)
    job.set_next_run(trigger_time)
    return job


def _once(trigger_time=None):
    if trigger_time is None:
        trigger_time = datetime.now()
    if not isinstance(trigger_time, datetime):
        raise AssertionError(
            "The trigger_time parameter should be a datetime object.")
    return default_scheduler.once(
            self=default_scheduler,
            trigger_time=trigger_time)


# Monkey-Patching
default_scheduler.once = _default_scheduler__once
schedule.once = _once

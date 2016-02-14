# -*- coding: utf-8 -*-

import logging

from six.moves import _thread, queue

logger = logging.getLogger(__name__)


class WorkerPool(object):
    def __init__(self, func, num_worker=10):
        self.num_worker = num_worker
        self.func = func
        self.queue = queue.Queue()
        self.busy_workers = queue.Queue()

    def start(self):
        for _ in range(self.num_worker):
            _thread.start_new_thread(self.do_work, tuple())

    def add_task(self, msg):
        self.queue.put(msg)

    def get_busy_workers(self):
        return self.busy_workers.qsize()

    def do_work(self):
        while True:
            msg = self.queue.get()
            self.busy_workers.put(1)
            self.func(msg)
            self.busy_workers.get()


def allow_only_direct_message():
    def plugin(func):
        def wrapper(message, *args, **kw):
            if not message.is_direct_message():
                return message.reply("`Only direct messages is allowed`")
            return func(message, *args, **kw)

        return wrapper

    return plugin

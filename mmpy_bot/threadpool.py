import asyncio
import logging
import threading
import time
from queue import Queue

from mmpy_bot.scheduler import default_scheduler
from mmpy_bot.webhook_server import WebHookServer

log = logging.getLogger("mmpy.threadpool")


class ThreadPool(object):
    def __init__(self, num_workers: int):
        """Threadpool class to easily specify a number of worker threads and assign work
        to any of them.

        Arguments:
        - num_workers: int, how many threads to run simultaneously.
        """
        self.num_workers = num_workers
        self.alive = False
        self._queue = Queue()
        self._busy_workers = Queue()
        self._threads = []

    def add_task(self, function, *args):
        self._queue.put((function, args))

    def get_busy_workers(self):
        return self._busy_workers.qsize()

    def start(self):
        self.alive = True
        # Spawn num_workers threads that will wait for work to be added to the queue
        for _ in range(self.num_workers):
            worker = threading.Thread(target=self.handle_work)
            self._threads.append(worker)
            worker.start()

    def stop(self):
        """Signals all threads that they should stop and waits for them to finish."""
        self.alive = False
        # Signal every thread that it's time to stop
        for _ in range(self.num_workers):
            self._queue.put((self._stop_thread, tuple()))
        # Wait for each of them to finish
        log.info("Stopping threadpool, waiting for threads...")
        for thread in self._threads:
            thread.join()
        log.info("Threadpool stopped.")

    def _stop_thread(self):
        """Used to stop individual threads."""
        return

    def handle_work(self):
        while self.alive:
            # Wait for a new task (blocking)
            function, arguments = self._queue.get()
            # Notify the pool that we started working
            self._busy_workers.put(1)
            try:
                function(*arguments)
            except Exception:
                log.exception("Unhandled exception in main loop")
            # Notify the pool that we finished working
            self._queue.task_done()
            self._busy_workers.get()

    def start_scheduler_thread(self, trigger_period: float):
        def run_pending():
            log.info("Scheduler thread started.")
            while self.alive:
                time.sleep(trigger_period)
                default_scheduler.run_pending()
            log.info("Scheduler thread stopped.")

        self.add_task(run_pending)

    def start_webhook_server_thread(self, webhook_server: WebHookServer):
        async def start_server():
            log.info("Webhook server thread started.")
            await webhook_server.start()
            while self.alive:
                # We just use this to keep the loop running in a non-blocking way
                await asyncio.sleep(0.001)
            await webhook_server.stop()
            log.info("Webhook server thread stopped.")

        self.add_task(asyncio.run, start_server())

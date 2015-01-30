#!/usr/bin/env python

import threading

timer_thread_name = "CodeIntel Timer"

def set_timeout(callback, delay, *args, **kwargs):
    timer = threading.Timer(delay / 1000, callback, args, kwargs)
    timer.name = timer_thread_name
    timer.start()


# -*- coding: UTF-8 -*-

from typing import *;

import subprocess;
import threading;



_controller_list = {};
_controller_list_l = threading.Lock();

class _Controller:

    ST_PRERUN = 0;
    ST_RUNNING = 1;
    ST_KILLING = 2;
    ST_DEAD = 3;

    def __init__(self, name : str, args : List[str], running : bool = False) -> None:
        self._name = name;
        self._args = args;
        self._state = _Controller.ST_PRRUN;
        self._state_l = threading.Lock();
        self._thread = threading.Thread(target = self._run, name = self._name, daemon = True);
        if running:
            self.start();

    def start(self):
        if self._state == _Controller.ST_PRERUN:
            with self._state_l:
                if self._state == _Controller.ST_PRERUN:
                    self._thread.start();
                    return;
        raise;

    def kill(self):
        if self._state != _Controller.ST_DEAD:
            with self._state_l:
                if self._state != _Controller.ST_DEAD:
                    self._state = _Controller.ST_KILLING;
                    return;
        raise;

    def _run(self):
        _proc = subprocess.Popen(
            args = self._args,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            shell = True
        );
        while self._state == _Controller.ST_RUNNING:
            pass;
        with self._state_l:
            self._state = _Controller.ST_DEAD;
    

def Controller(name : str, args : List[str], running : bool = False):
    if not name in _controller_list:
        with _controller_list_l:
            if not name in _controller_list:
                _controller_list[name] = _Controller(name, args, running);
                return _controller_list[name];
    raise ValueError("Existing Controller of name %s." % name);

def KillController(name : str):
    if name in _controller_list:
        with _controller_list_l:
            if name in _controller_list:
                _c = _controller_list.pop(name);
                _c.kill();
                return;
    raise ValueError("Non-existing Controller of name %s." % name)
    


# -*- coding: UTF-8 -*-

from typing import *;

import subprocess;
import threading;

from . import recorder as rec;



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
        self._proc = None;
        self._thread = threading.Thread(target = self._run, name = self._name, daemon = True);
        self._recorder = rec.get_recorder(name);
        if running:
            self.start();
    
    @property
    def recorder(self):
        return self._recorder;

    def start(self):
        if self._state is _Controller.ST_PRERUN:
            with self._state_l:
                if self._state is _Controller.ST_PRERUN:
                    self._proc = subprocess.Popen(
                        args = self._args,
                        stdin = subprocess.PIPE,
                        stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE,
                        shell = True
                    );
                    self._state = _Controller.ST_RUNNING;
                    self._thread.start();
                    return;

    def kill(self):
        if self._state != _Controller.ST_DEAD:
            with self._state_l:
                if self._state != _Controller.ST_DEAD:
                    self._state = _Controller.ST_KILLING;
                    return;
    
    def is_running(self):
        return self._state is _Controller.ST_RUNNING;
    
    def is_alive(self):
        return not self._state is _Controller.ST_DEAD;
    
    def is_dead(self):
        return self._state is _Controller.ST_DEAD;

    def get_state(self):
        return self._state;

    def _run(self):
        while self._state == _Controller.ST_RUNNING:
            try:
                _line = self._proc.stdout.readline();
                self._recorder.record(_line);
            except Exception as e:
                pass;
                ## TODO: Add exception handling.
        with self._state_l:
            self._state = _Controller.ST_DEAD;
    

def _add_controller_to_list(name : str, controller : _Controller):
    if not name in _controller_list:
        with _controller_list_l:
            if not name in _controller_list:
                _controller_list[name] = controller;
                return;
    raise ValueError("Existing Controller of name %s." % name);

def _pop_controller_from_list(name : str):
    if name in _controller_list:
        with _controller_list_l:
            if name in _controller_list:
                _c = _controller_list.pop(name);
                return _c;
    raise ValueError("Non-existing Controller of name %s." % name);

def _with_controller_in_list(name : str, action):
    if name in _controller_list:
        with _controller_list_l:
            if name in _controller_list:
                _c = _controller_list[name];
                action(_c);
                ## TODO: Check action.

def Controller(name : str, args : List[str], running : bool = False):
    _c = _Controller(name, args, running);
    _add_controller_to_list(name = name, controller = _c);
    return _c;

def KillController(name : str):
    _c = _pop_controller_from_list(name = name);
    _c.kill();
    return;
    

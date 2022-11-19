
# -*- coding: UTF-8 -*-

import time
from typing import *;

import threading;



_recorder_list = {};
_recorder_list_l = threading.Lock();

_history = [];
_history_l = threading.Lock();

_formatter = None;
_formatter_l = threading.Lock();



class _Record:

    def __init__(self, recorder : str, time : float, markers : Tuple = (), message : str = "") -> None:
        self._recorder = recorder;
        self._time = time;
        self._markers = markers;
        self._message = message;
    
    @property
    def recorder(self):
        return self._recorder;
    
    @property
    def time(self):
        return self._time;
    
    @property
    def markers(self):
        return self._markers;
    
    @property
    def message(self):
        return self._message;

class _Recorder:

    def __init__(self, name : str, markers : Tuple[str], recording : bool = True) -> None:
        self._name = name;
        self._markers = set(markers);
        self._markers_l = threading.Lock();
        self._markers_tuple = tuple(sorted(markers));
        self._recording = recording;
        self._recording_l = threading.Lock();
    
    def mark(self, marker : str):
        if not marker in self._markers:
            with self._markers_l:
                if not marker in self._markers:
                    self._markers.add(marker);
                    self._markers_tuple = tuple(sorted(self._markers));
    
    def demark(self, marker : str):
        if marker in self._markers:
            with self._markers_l:
                if marker in self._markers:
                    self._markers.remove(marker);
                    self._markers_tuple = tuple(sorted(self._markers));

    def record(self, message : str):
        _rec = _Record(
            self._name,
            time = time.time(),
            markers = self._markers_tuple,
            message = message
        );
        with _history_l:
            _history.append(_rec)



def get_recorder(name : str):
    with _recorder_list_l:
        if name in _recorder_list:
            _r = _recorder_list[name];
        else:
            _r = _Recorder(name = name, markers = ());
            _recorder_list[name] = _r;
    return _r;

def format(record : _Record):
    if _formatter:
        with _formatter_l:
            if _formatter:
                return _formatter(record);
    return "";

def set_formatter(formatter):
    with _formatter_l:
        _formatter = formatter;

def dump_history(file : str):
    with open(file = file, mode = "w") as fp:
        fp.writelines((format(_rec) for _rec in _history));
        ## TODO: Should this be locked? I think visiting _history is thread safe for python ensures it.

def get_history():
    return _history.copy();

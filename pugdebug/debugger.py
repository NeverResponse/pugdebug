# -*- coding: utf-8 -*-

"""
    pugdebug - a standalone PHP debugger
    =========================
    copyright: (c) 2015 Robert Basic
    license: GNU GPL v3, see LICENSE for more details
"""

__author__="robertbasic"

import socket

from PyQt5.QtCore import QObject, pyqtSignal

from pugdebug.server import PugdebugServer
from pugdebug.message_parser import PugdebugMessageParser

class PugdebugDebugger(QObject):

    server = None
    parser = None

    last_message = ''

    current_file = ''
    current_line = 0

    debugging_started_signal = pyqtSignal()
    step_command_signal = pyqtSignal()
    got_all_variables_signal = pyqtSignal()

    def __init__(self):
        """Init the debugger object

        Create a PugdebugServer object used to communicate with xdebug client
        through TCP.

        Create a PugdebugMessageParser object used to parse the xml responses
        from xdebug.

        Connect signals to slots.
        """
        super(PugdebugDebugger, self).__init__()

        self.server = PugdebugServer()
        self.parser = PugdebugMessageParser()

        self.server.server_connected_signal.connect(self.handle_server_connected)
        self.server.server_stepped_signal.connect(self.handle_server_stepped)
        self.server.server_got_variables_signal.connect(self.handle_server_got_variables)

    def cleanup(self):
        """Cleanup debugger when it's done
        """
        if self.server.is_connected():
            self.server.disconnect()

        self.last_message = ''
        self.current_file = ''
        self.current_line = 0

    def handle_server_connected(self):
        self.debugging_started_signal.emit()

    def handle_server_stepped(self):
        self.get_variables()

    def handle_server_got_variables(self):
        self.got_all_variables_signal.emit()

    def start_debug(self):
        """Start a debugging session

        If the server is not connected, connect it.
        """
        self.server.connect()

    def stop_debug(self):
        self.server.stop()

    def run_debug(self):
        self.server.step_run()

    def step_over(self):
        self.server.step_over()

    def step_into(self):
        self.server.step_into()

    def step_out(self):
        self.server.step_out()

    def get_variables(self):
        self.server.get_variables()

    def get_current_file(self):
        if 'filename' in self.last_message:
            self.current_file = self.last_message['filename'].replace('file://', '')

        return self.current_file

    def get_current_line(self):
        if 'lineno' in self.last_message:
            self.current_line = int(self.last_message['lineno'])

        return self.current_line

    def is_breaking(self):
        return self.is_status('break')

    def is_stopping(self):
        return self.is_status('stopping')

    def is_stopped(self):
        return self.is_status('stopped')

    def is_status(self, status):
        if 'status' in self.last_message and self.last_message['status'] == status:
            return True
        return False

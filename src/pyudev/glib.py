# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.

# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

"""
    pyudev.pygtk
    ============

    Provide :class:`~pyudev.glib.GUDevMonitorObserver` to integrate a
    :class:`~pyudev.Monitor` into a :class:`glib.MainLoop`.

    To use this module, :mod:`glib` and :mod:`gobject` from PyGObject_ must be
    available.  PyGtk is not required.

    .. _PyGObject: http://www.pygtk.org/

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
    .. versionadded:: 0.7
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

# thanks to absolute imports, this really imports the glib binding and not this
# module again
import glib
import gobject


class GUDevMonitorObserver(gobject.GObject):
    """
    Observe a :class:`~pyudev.Monitor` and emit Glib signals upon device
    events:

    >>> context = pyudev.Context()
    >>> monitor = pyudev.Monitor.from_netlink(context)
    >>> monitor.filter_by(subsystem='input')
    >>> observer = pyudev.pygtk.GUDevMonitorObserver(monitor)
    >>> def device_connected(observer, device):
    ...     print('{0!r} added'.format(device))
    >>> observer.connect('device-added', device_connected)
    >>> monitor.start()

    This class is a child of :class:`gobject.GObject`.
    """

    _action_signal_map = {
        'add': 'device-added', 'remove': 'device-removed',
        'change': 'device-changed', 'move': 'device-moved'}

    __gsignals__ = {
        # glib apparently expects byte-strings as signal names
        b'device-event': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        b'device-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          (gobject.TYPE_PYOBJECT,)),
        b'device-removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                            (gobject.TYPE_PYOBJECT,)),
        b'device-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                            (gobject.TYPE_PYOBJECT,)),
        b'device-moved': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          (gobject.TYPE_PYOBJECT,)),
        }

    def __init__(self, monitor):
        gobject.GObject.__init__(self)
        self.monitor = monitor
        self.event_source = glib.io_add_watch(monitor, glib.IO_IN,
                                              self._process_udev_event)

    def _process_udev_event(self, source, condition):
        if condition == glib.IO_IN:
            event = self.monitor.receive_device()
            if event:
                action, device = event
                self.emit('device-event', action, device)
                self.emit(self._action_signal_map[action], device)
        return True


gobject.type_register(GUDevMonitorObserver)

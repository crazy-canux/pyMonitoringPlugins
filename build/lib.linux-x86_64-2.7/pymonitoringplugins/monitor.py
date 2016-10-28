#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic functions for nagios and tools based on nagios.

Copyright (C) 2016 Canux CHENG.
All rights reserved.
Name: monitor.py
Author: Canux CHENG canuxcheng@gmail.com
Version: V1.0.0.0
Time: Thu 28 Jul 2016 03:23:45 PM CST

Description:
    Test on nagios, naemon, icinga, shinken, centreon, opsview and sensu except check_mk.
    [1.0.0.0] 20160728 init for basic function.
"""
import logging
import argparse


class Monitor(object):

    """Basic class for monitor.

    Nagios and tools based on nagios have the same status.
    All tools have the same output except check_mk.

        Services Status:
        0 green  OK
        1 yellow Warning
        2 red    Critical
        3 orange Unknown
        * grey   Pending

        Nagios Output(just support 4kb data):
        shortoutput - $SERVICEOUTPUT$
        -> The first line of text output from the last service check.

        perfdata - $SERVICEPERFDATA$
        -> Contain any performance data returned by the last service check.
        With format: | 'label'=value[UOM];[warn];[crit];[min];[max].

        longoutput - $LONGSERVICEOUTPUT$
        -> The full text output aside from the first line from the last service check.

        example:
        OK - shortoutput. |
        Longoutput line1
        Longoutput line2 |
        'perfdata'=value[UOM];[warn];[crit];[min];[max]
    """

    def __init__(self):
        # Init the log.
        logging.basicConfig(format='[%(levelname)s] (%(module)s) %(message)s')
        self.logger = logging.getLogger("monitor")
        self.logger.setLevel(logging.INFO)

        # Init output data.
        self.nagios_output = ""
        self.shortoutput = ""
        self.perfdata = []
        self.longoutput = []

        # Init the argument
        self.__define_options()
        self.define_sub_options()
        self.__parse_options()

        # Init the logger
        if self.args.debug:
            self.logger.setLevel(logging.DEBUG)
        self.logger.debug("===== BEGIN DEBUG =====")
        self.logger.debug("Init Monitor")

        # End the debug.
        if self.__class__.__name__ == "Monitor":
            self.logger.debug("===== END DEBUG =====")

    def __define_options(self):
        self.parser = argparse.ArgumentParser(description="Plugin for Monitor.")
        self.parser.add_argument('-D', '--debug',
                                 action='store_true',
                                 required=False,
                                 help='Show debug informations.',
                                 dest='debug')

    def define_sub_options(self):
        """Define options for monitoring plugins.

        Rewrite your method and define your suparsers.
        Use subparsers.add_parser to create sub options for one function.
        """
        self.plugin_parser = self.parser.add_argument_group("Plugin Options",
                                                            "Options for all plugins.")
        self.plugin_parser.add_argument("-H", "--host",
                                        required=True,
                                        help="Host IP address or DNS",
                                        dest="host")
        self.plugin_parser.add_argument("-u", "--user",
                                        required=False,
                                        help="User name",
                                        dest="user")
        self.plugin_parser.add_argument("-p", "--password",
                                        required=False,
                                        help="User password",
                                        dest="password")

    def __parse_options(self):
        try:
            self.args = self.parser.parse_args()
        except Exception as e:
            self.unknown("Parser arguments error: {}".format(e))

    def output(self, substitute=None, long_output_limit=None):
        """Just for nagios output and tools based on nagios except check_mk.

        Default longoutput show everything.
        But you can use long_output_limit to limit the longoutput lines.
        """
        if not substitute:
            substitute = {}

        self.nagios_output += "{0}".format(self.shortoutput)
        if self.longoutput:
            self.nagios_output = self.nagios_output.rstrip("\n")
            self.nagios_output += " | \n{0}".format(
                "\n".join(self.longoutput[:long_output_limit]))
            if long_output_limit:
                self.nagios_output += "\n(...showing only first {0} lines, " \
                    "{1} elements remaining...)".format(
                        long_output_limit,
                        len(self.longoutput[long_output_limit:]))
        if self.perfdata:
            self.nagios_output = self.nagios_output.rstrip("\n")
            self.nagios_output += " | \n{0}".format(" ".join(self.perfdata))
        return self.nagios_output.format(**substitute)

    def ok(self, msg):
        raise MonitorOk(msg)

    def warning(self, msg):
        raise MonitorWarning(msg)

    def critical(self, msg):
        raise MonitorCritical(msg)

    def unknown(self, msg):
        raise MonitorUnknown(msg)


class MonitorOk(Exception):

    def __init__(self, msg):
        print("OK - %s" % msg)
        raise SystemExit(0)


class MonitorWarning(Exception):

    def __init__(self, msg):
        print("WARNING - %s" % msg)
        raise SystemExit(1)


class MonitorCritical(Exception):

    def __init__(self, msg):
        print("CRITICAL - %s" % msg)
        raise SystemExit(2)


class MonitorUnknown(Exception):

    def __init__(self, msg):
        print("UNKNOWN - %s" % msg)
        raise SystemExit(3)
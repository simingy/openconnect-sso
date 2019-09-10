import argparse
import enum
import logging
import os

import openconnect_sso
from openconnect_sso import app, config


def create_argparser():
    parser = argparse.ArgumentParser(
        prog="openconnect-sso", description=openconnect_sso.__description__
    )

    server_settings = parser.add_argument_group("Server connection")
    server_settings.add_argument(
        "-p",
        "--profile",
        dest="profile_path",
        help="Use a profile from this file or directory",
    )

    server_settings.add_argument(
        "-P",
        "--profile-selector",
        dest="use_profile_selector",
        help="Always display profile selector",
        action="store_true",
        default=False,
    )

    server_settings.add_argument("-s", "--server")
    server_settings.add_argument("-g", "--usergroup", default="")

    parser.add_argument(
        "--login-only", "--authenticate",
        help="Complete authentication but do not acquire a session token or initiate a connection",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "-l",
        "--log-level",
        help="",
        type=LogLevel.parse,
        choices=LogLevel.choices(),
        default=LogLevel.INFO,
    )

    parser.add_argument(
        "openconnect_args",
        help="Arguments passed to openconnect",
        nargs=argparse.REMAINDER,
    )

    credentials_group = parser.add_argument_group("Credentials for automatic login")
    credentials_group.add_argument(
        "-u", "--user", help="Authenticate as the given user", default=None
    )
    return parser


class LogLevel(enum.IntEnum):
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG

    def __str__(self):
        return self.name

    @classmethod
    def parse(cls, name):
        return cls.__members__[name.upper()]

    @classmethod
    def choices(cls):
        return cls.__members__.values()


def main():
    parser = create_argparser()
    args = parser.parse_args()

    if (args.profile_path or args.use_profile_selector) and (args.server or args.usergroup):
        parser.error("--profile/--profile-selector and --server/--usergroup are mutually exclusive")

    if not args.profile_path and not args.server and not config.load().default_profile:
        if os.path.exists("/opt/cisco/anyconnect/profiles"):
            args.profile_path = "/opt/cisco/anyconnect/profiles"
        else:
            parser.error("No Anyconnect profile can be found. One of --profile or --server arguments required.")

    return app.run(args)
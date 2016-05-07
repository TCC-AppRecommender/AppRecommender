import commands
import os
import re

from src.data_classification import get_time_from_package
from src.config import Config
from src.user import LocalSystem

USER_DATA_DIR = Config().user_data_dir


def create_pkg_data(manual_pkgs=None):
    if not manual_pkgs:
        user = LocalSystem()
        user.no_auto_pkg_profile()
        manual_pkgs = user.pkg_profile

    pkgs_time = get_packages_time(manual_pkgs)
    save_package_time(pkgs_time)

    return pkgs_time


def get_package_data(file_path=USER_DATA_DIR + 'pkg_data.txt'):

    if os.path.isfile(file_path):
        pkgs_time = {}

        with open(file_path, 'r') as pkg_data:
            for pkg_line in pkg_data:
                name, modify, access = pkg_line.split(' ')
                pkgs_time[name] = [modify, access]

        return pkgs_time

    else:
        return create_pkg_data()


def get_best_time(pkg):
    valid_regex = re.compile(r'/usr/bin/|/usr/sbin|/usr/game/|/usr/lib/.+/')
    pkg_files = commands.getoutput('dpkg -L {}'.format(pkg))

    bestatime, bestmtime = 0, 0
    for pkg_file in pkg_files.splitlines():
        if valid_regex.search(pkg_file):
            access, modify = get_time_from_package(pkg_file, pkg_bin=False)

            if access >= bestatime:
                bestatime = access
                bestmtime = modify

    return (bestmtime, bestatime)


def get_packages_time(pkgs):
    pkgs_time = {}

    for pkg in pkgs:

        modify, access = get_best_time(pkg)

        if modify and access:
            print 'ADD: {}'.format(pkg)
            pkgs_time[pkg] = []
            pkgs_time[pkg].append(modify)
            pkgs_time[pkg].append(access)
        else:
            print 'NOT: {} {} {}'.format(pkg, modify, access)

    return pkgs_time


def print_package_time(pkgs_time):
    for key, value in pkgs_time.iteritems():
        print "{0} : Modify {1}, Access {2}".format(key, value[0], value[1])


def save_package_time(pkgs_time, file_path=USER_DATA_DIR + 'pkg_data.txt'):
    with open(file_path, 'w') as pkg_data:

        pkg_str = "{pkg} {modify} {access}\n"
        for pkg, times in pkgs_time.iteritems():

            pkg_line = pkg_str.format(pkg=pkg, modify=times[0],
                                      access=times[1])
            pkg_data.write(pkg_line)

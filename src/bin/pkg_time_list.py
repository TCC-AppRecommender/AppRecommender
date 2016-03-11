#!/usr/bin/python

import commands
import re

import sys
sys.path.insert(0, '../')

from data_classification import get_time_from_package, get_alternative_pkg
from config import Config

USER_DATA_DIR = Config().user_data_dir


def get_packages_time(pkgs):

    pkgs_time = {}

    for pkg in pkgs:

        modify, access = get_time_from_package(pkg)

        if not modify or not access:
            pkg_tmp = get_alternative_pkg(pkg)
            modify, access = get_time_from_package(pkg_tmp)

        if modify and access:
            pkgs_time[pkg] = []
            pkgs_time[pkg].append(modify)
            pkgs_time[pkg].append(access)

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


def get_packages_from_apt_mark():

    dpkg_output = commands.getoutput('apt-mark showmanual')
    pkgs = []

    for pkg in dpkg_output.splitlines():

        if not re.match(r'^lib', pkg):
            pkgs.append(pkg)

    return pkgs


def main():

    manual_pkgs = get_packages_from_apt_mark()
    print "Size of manual installed packages apt-mark:", len(manual_pkgs)

    pkgs_time = get_packages_time(manual_pkgs)
    print_package_time(pkgs_time)

    print "\nSize of dictionary:", len(pkgs_time)
    save_package_time(pkgs_time)


if __name__ == "__main__":
    main()

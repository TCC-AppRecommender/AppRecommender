#!/usr/bin/env python

import commands
import calendar
import logging
import math
import operator
import time

pkgs_times = {}
pkgs_time_weight = {}
best_weight_terms = {}
user_tfidf_weights = {}


def pkg_name_with_error(pkg):
    return len(pkg.split()) > 1


def get_time_from_package(pkg, pkg_bin=True):
    if pkg_name_with_error(pkg):
        pkgs_times[pkg] = [None, None]

    if pkg in pkgs_times:
        modify, access = pkgs_times[pkg]
    else:
        modify = get_time('Y', pkg, pkg_bin)
        access = get_time('X', pkg, pkg_bin)
        pkgs_times[pkg] = [modify, access]

    return pkgs_times[pkg]


def get_alternative_pkg(pkg):
    dpkg_command = "dpkg -L {0}| grep /usr/bin/"
    dpkg_command += " || dpkg -L {0}| grep /usr/sbin/"
    pkg_bin = commands.getoutput(dpkg_command.format(pkg))

    possible_pkgs = {}
    for pkg_path in pkg_bin.splitlines():
        possible_pkgs[pkg_path] = get_time('X', pkg_path)

    if bool(possible_pkgs):
        return sorted(possible_pkgs.items(), key=operator.itemgetter(1))[0][0]

    return None


def get_time(option, pkg, pkg_bin=True):
    stat_base = "stat -c '%{option}'"
    stat_base += " `which {package}`" if pkg_bin else " {package}"
    stat_error = 'stat:'
    stat_time = stat_base.format(option=option, package=pkg)

    pkg_time = commands.getoutput(stat_time)

    if stat_error not in pkg_time:
        return pkg_time

    return None


def linear_percent_function(modify, access, time_now):
    modify, access = int(modify), int(access)

    time_access = access - modify
    time_actual = time_now - modify

    percent = float(time_access) / float(time_actual)

    return percent


def get_pkg_time_weight(pkg):
    modify, access = get_time_from_package(pkg)

    if not modify and not access:
        modify, access = get_time_from_package(get_alternative_pkg(pkg))

    if not modify and not access:
        return 0

    time_now = calendar.timegm(time.gmtime())

    return linear_percent_function(modify, access, time_now)


def calculate_time_curve(pkg_time_weight):

    if not pkg_time_weight:
        return 0

    const_a = 10
    lambda_value = 1

    return const_a * (1 / math.exp((1 - pkg_time_weight) * lambda_value))


def time_weight(term, term_list):
    weight = []
    weight_len = 5
    weight_delta = 0.2

    for pkg in term_list:
        if pkg in pkgs_time_weight:
            weight.append(pkgs_time_weight[pkg])
        else:
            pkg_time_weight = get_pkg_time_weight(pkg)
            pkgs_time_weight[pkg] = pkg_time_weight
            weight.append(calculate_time_curve(pkg_time_weight))

    weight = list(reversed(sorted(weight)))
    if len(weight) < weight_len:
        for i in range(len(weight), weight_len):
            weight.append(weight[-1] - weight_delta)

    time_weight = float(sum(weight[0:weight_len])) / float(weight_len)

    best_weight_terms[term] = time_weight

    return time_weight


def print_best_weight_terms(terms_package):
    index = 0
    total = 0
    logging.info("BEST TERMS")

    for term in sorted(best_weight_terms, key=best_weight_terms.get,
                       reverse=True):
        if index < 10:
            logging.info("\n")
            logging.info(term, best_weight_terms[term])
            logging.info('-')

            for pkg in terms_package[term]:
                logging.info("[{0}: {1} {2}]\n".format(pkg,
                             get_pkg_time_weight(pkg),
                             get_alternative_pkg(pkg)))

                total += 1
                if total > 5:
                    break

        total = 0
        index += 1

#!/usr/bin/env python
"""
    Clustering - A python script to perform clustering of popcon data.
"""
__author__ = "Tassia Camoes Araujo <tassia@gmail.com>"
__copyright__ = "Copyright (C) 2011 Tassia Camoes Araujo"
__license__ = """
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
sys.path.insert(0, '../')
import logging
import datetime

from apprecommender.config import Config
from apprecommender.data import PopconXapianIndex
from apprecommender.error import Error

if __name__ == '__main__':
    try:
        cfg = Config()
        begin_time = datetime.datetime.now()
        logging.info("Clustering computation started at %s" % begin_time)

        pxi = PopconXapianIndex(cfg)

        end_time = datetime.datetime.now()
        logging.info("Clustering computation completed at %s" % end_time)
        delta = end_time - begin_time
        logging.info("Time elapsed: %d seconds." % delta.seconds)
        logging.info("Medoids: %d\tDispersion:%f" %
                     (cfg.k_medoids, pxi.cluster_dispersion))

    except Error:
        logging.critical("Aborting proccess. Use '--debug' for more details.")

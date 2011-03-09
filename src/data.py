#!/usr/bin/python

#  AppRecommender - A GNU/Linux application recommender
#
#  Copyright (C) 2010  Tassia Camoes <tassia@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import re
import xapian
import axi
from debian import debtags
import logging

class Item:
    """  """

class Package(Item):
    """  """
    def __init__(self,package_name):
        """  """
        self.package_name  = package_name

    def load_package_info(self):
        """  """
        print "debian pkg",self.id

def normalize_tags(string):
    """
    Normalize tag string so that it can be indexed and retrieved.
    """
    return string.replace(':','_').replace('-','\'')

# FIXME Data repositories should be singleton

class DebtagsDB(debtags.DB):
    def __init__(self,path):
        self.path = path

    def load(self):
        tag_filter = re.compile(r"^special::.+$|^.+::TODO$")
        try:
            self.read(open(self.path, "r"), lambda x: not tag_filter.match(x))
            return 1
        except IOError:
            logging.error("IOError: could not open debtags file \'%s\'" %
                          self.path)
            return 0

    def get_relevant_tags(self,pkgs_list,qtd_of_tags):
        """
        Return most relevant tags considering a list of packages.
        """
        relevant_db = self.choose_packages(pkgs_list)
        relevance_index = debtags.relevance_index_function(self,relevant_db)
        sorted_relevant_tags = sorted(relevant_db.iter_tags(),
                                      lambda a, b: cmp(relevance_index(a),
                                      relevance_index(b)))
        return normalize_tags(' '.join(sorted_relevant_tags[-qtd_of_tags:]))

class DebtagsIndex(xapian.WritableDatabase):
    def __init__(self,path):
        self.path = path

    def load(self,debtags_db,reindex):
        """
        Load an existing debtags index.
        """
        self.debtags_db = debtags_db
        if not reindex:
            try:
                logging.info("Opening existing debtags xapian index at \'%s\'"
                              % self.path)
                xapian.Database.__init__(self,self.path)
            except xapian.DatabaseError:
                logging.error("Could not open debtags xapian index")
                reindex =1
        if reindex:
            self.reindex(debtags_db)

    def reindex(self,debtags_db):
        """
        Create a xapian index for debtags info based on file 'debtags_db' and
        place it at 'index_path'.
        """
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        logging.info("Creating new debtags xapian index at \'%s\'" % self.path)
        xapian.WritableDatabase.__init__(self,self.path,
                                         xapian.DB_CREATE_OR_OVERWRITE)
        for pkg,tags in debtags_db.iter_packages_tags():
            doc = xapian.Document()
            doc.set_data(pkg)
            for tag in tags:
                doc.add_term(normalize_tags(tag))
            doc_id = self.add_document(doc)
            logging.debug("Indexing doc %d",doc_id)

#!/usr/bin/env python
# encoding: utf-8
"""
test_refine.py

Created by Paul Makepeace on 2011-04-22.
Copyright (c) 2011 Real Programmers. All rights reserved.
"""

import sys
import os
import unittest
from google.refine import REFINE_HOST, REFINE_PORT
from google.refine import NumericFacet, TextFacet, Engine
from google.refine import RefineServer, Refine, RefineProject
from google.refine import to_camel, from_camel

PATH_TO_TEST_DATA = os.path.join('google', 'test', 'data')


class CamelTest(unittest.TestCase):
    def test_to_camel(self):
        pairs = (
            ('this', 'this'),
            ('this_attr', 'thisAttr'),
            ('From', 'from'),
        )
        for attr, camel_attr in pairs:
            self.assertEqual(to_camel(attr), camel_attr)

    def test_from_camel(self):
        pairs = (
            ('this', 'this'),
            ('This', 'this'),
            ('thisAttr', 'this_attr'),
            ('ThisAttr', 'this_attr'),
            ('From', 'from'),
        )
        for camel_attr, attr in pairs:
            self.assertEqual(from_camel(camel_attr), attr)


class RefineTestCase(unittest.TestCase):
    project_file = None
    project = None
    # {1}, {2}
    def setUp(self):
        self.server = RefineServer()
        self.refine = Refine(self.server)
        if self.project_file:
            self.project = self.refine.new_project(
                os.path.join(PATH_TO_TEST_DATA, self.project_file))

    def tearDown(self):
        if self.project:
            self.project.delete()
            self.project = None


class RefineServerTest(RefineTestCase):
    def test_init(self):
        self.assertEqual(self.server.server, 'http://%s:%s' % (REFINE_HOST, REFINE_PORT))
        server = RefineServer('http://refine.example/')
        self.assertEqual(server.server, 'http://refine.example')

    def test_list_projects(self):
        projects = self.refine.list_projects()
        self.assertTrue(isinstance(projects, dict))

    def test_get_version(self):
        version_info = self.refine.get_version()
        for item in ('revision', 'version', 'full_version', 'full_name'):
            self.assertTrue(item in version_info)


class RefineTest(RefineTestCase):
    project_file = 'duplicates.csv'

    def test_new_project(self):
        self.assertTrue(isinstance(self.project, RefineProject))

    def test_get_models(self):
        self.assertEqual(self.project.key_column, 'email')
        self.assertTrue('email' in self.project.columns)
        self.assertEqual(self.project.column_index['name'], 1)

    def test_delete_project(self):
        self.assertTrue(self.project.delete())


class TutorialTestFacets(RefineTestCase):
    project_file = 'louisiana-elected-officials.csv'

    def test_get_rows(self):
        # {3}
        response = self.project.get_rows(limit=10)
        self.assertEqual(len(response.rows), 10)
        self.assertEqual(response.limit, 10)
        self.assertEqual(response.total, 6958)
        for row in response.rows:
            self.assertFalse(row.flagged)
            self.assertFalse(row.starred)

    def test_basic_facet(self):
        # {4}
        party_code_facet = TextFacet(column='Party Code')
        response = self.project.compute_facets(party_code_facet)
        pc = response.facets[0]
        self.assertEqual(pc.name, 'Party Code')
        self.assertEqual(pc.choices['D'].count, 3700)
        self.assertEqual(pc.choices['N'].count, 15)
        self.assertEqual(pc.blank_choice.count, 1446)
        # {5}, {6}
        engine = Engine(party_code_facet)
        ethnicity_facet = TextFacet(column='Ethnicity')
        engine.add_facet(ethnicity_facet)
        self.project.engine = engine
        response = self.project.compute_facets()
        e = response.facets[1]
        self.assertEqual(e.choices['B'].count, 1255)
        self.assertEqual(e.choices['W'].count, 4469)
        # {7}
        ethnicity_facet.include('B')
        response = self.project.get_rows()
        self.assertEqual(response.filtered, 1255)
        indexes = [r.index for r in response.rows]
        self.assertEqual(indexes, [1, 2, 3, 4, 6, 12, 18, 26, 28, 32])
        # {8}
        response = self.project.compute_facets()
        pc = response.facets[0]
        self.assertEqual(pc.name, 'Party Code')
        self.assertEqual(pc.choices['D'].count, 1179)
        self.assertEqual(pc.choices['R'].count, 11)
        self.assertEqual(pc.blank_choice.count, 46)
        # {9}
        party_code_facet.include('R')
        response = self.project.compute_facets()
        e = response.facets[1]
        self.assertEqual(e.choices['B'].count, 11)
        # {10}
        party_code_facet.reset()
        ethnicity_facet.reset()
        response = self.project.get_rows()
        self.assertEqual(response.filtered, 6958)
        # {11}
        office_title_facet = TextFacet('Office Title')
        self.project.engine.add_facet(office_title_facet)
        response = self.project.compute_facets()
        self.assertEqual(len(response.facets[2].choices), 76)
        # {12} - XXX not sure how to interpret bins & baseBins yet
        office_level_facet = NumericFacet('Office Level')
        self.project.engine.add_facet(office_level_facet)
        # {13}
        office_level_facet.From = 300   # from reserved word
        office_level_facet.to = 320
        response = self.project.get_rows()
        self.assertEqual(response.filtered, 1907)
        response = self.project.compute_facets()
        ot = response.facets[2]   # Office Title
        self.assertEqual(len(ot.choices), 21)
        self.assertEqual(ot.choices['Chief of Police'].count, 2)
        self.assertEqual(ot.choices['Chief of Police          '].count, 211)
        # {14}
        self.project.engine.remove_all()
        response = self.project.get_rows()
        self.assertEqual(response.filtered, 6958)


if __name__ == '__main__':
    unittest.main()
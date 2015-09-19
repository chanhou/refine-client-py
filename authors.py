#!/usr/bin/env python
"""
Script to provide a command line interface to a Refine server.

Examples,

refine --list    # show list of Refine projects, ID: name
refine --export 1234... > project.tsv
refine --export --output=project.xls 1234...
refine --apply trim.json 1234...
"""

# Copyright (c) 2011 Paul Makepeace, Real Programmers. All rights reserved.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


import optparse
import os
import sys
import time

import gzip


sys.path.append('./google/refine')

print '****************'

import refine as refine


PARSER = optparse.OptionParser(
    usage='usage: %prog [--help | OPTIONS] [project ID/URL]')
PARSER.add_option('-H', '--host', dest='host',
                  help='OpenRefine hostname')
PARSER.add_option('-P', '--port', dest='port',
                  help='OpenRefine port')
PARSER.add_option('-o', '--output', dest='output',
                  help='Output filename')
# Options that are more like commands
PARSER.add_option('-l', '--list', dest='list', action='store_true',
                  help='List projects')
PARSER.add_option('-E', '--export', dest='export', action='store_true',
                  help='Export project')
PARSER.add_option('-f', '--apply', dest='apply',
                  help='Apply a JSON commands file to a project')


def list_projects():
    """Query the Refine server and list projects by ID: name."""
    projects = refine.Refine(refine.RefineServer()).list_projects().items()

    def date_to_epoch(json_dt):
        """Convert a JSON date time into seconds-since-epoch."""
        return time.mktime(time.strptime(json_dt, '%Y-%m-%dT%H:%M:%SZ'))
    projects.sort(key=lambda v: date_to_epoch(v[1]['modified']), reverse=True)
    for project_id, project_info in projects:
        print('{0:>14}: {1}'.format(project_id, project_info['name']))


def export_project(project, options):
    """Dump a project to stdout or options.output file."""
    export_format = 'tsv'
    if options.output:
        ext = os.path.splitext(options.output)[1][1:]     # 'xls'
        if ext:
            export_format = ext.lower()
        output = open(options.output, 'wb')
    else:
        output = sys.stdout
    output.writelines(project.export(export_format=export_format))
    output.close()



class oooutput:
    def __init__(self, path):
        self.output = path


def cluster_edit(project, column):
    for cluster in project.compute_clusters(column):
        i = 0
        arr = []
        for match in cluster:
            i += 1
            # print match
            if i == 1:
                check = match['value']
                # print check
                continue
            arr.append(match['value'])
        #print arr
        project.edit(column, arr, check)
        break

def create_project(file_des, filename):
    return refine.Refine(refine.RefineServer()).new_project(\
        project_file=file_des, \
        project_name=filename, separator='\t',\
        header_lines=0,store_blank_rows=False,\
        guess_cell_value_types=False,process_quotes=False,\
        store_blank_cells_as_nulls=False)

def dump_csv(cluster, des):
    with open('des','wb') as f:
        for ind,i in enumerate(cluster):
            for q in i:
                f.write(q.values()[1].encode('UTF-8')+'\t')
                f.write('\n')
                #if ind==3:
                #    break


#noinspection PyPep8Naming
def main():
    """Main."""
    options, args = PARSER.parse_args()

    if options.host:
        refine.REFINE_HOST = options.host
    if options.port:
        refine.REFINE_PORT = options.port

    if not options.list and len(args) != 1:
        PARSER.print_usage()
    if options.list:
        list_projects()
    if args:
        project = refine.RefineProject(args[0])
        if options.apply:
            response = project.apply_operations(options.apply)
            if response != 'ok':
                print >>sys.stderr, 'Failed to apply %s: %s' % (options.apply,
                                                                response)
        if options.export:
            export_project(project, options)

        return project

if __name__ == '__main__':

    # return project so that it's available interactively, python -i refine.py
    refine_project = main()

    #bbb = create_project('/tmp2/MicrosoftAcademicGraph_refine/Authors_1_column.txt', "author_new")

    # read project by id
    bbb = refine.RefineProject(refine.RefineServer(), 2281573611164)

    #ddd = bbb.compute_clusters('Column 1')
    # dump_csv(ddd, '/tmp2/MicrosoftAcademicGraph_clean/Affiliations.tsv')

    # rename column
    # bbb.rename_column('Column 1', 'Affiliation_ID')
    # bbb.rename_column('Column 2', 'Affiliation_name')

    
    # doing cluster and edit by refine
    # see the function above if only want the cluster result
    #cluster_edit(bbb, 'Column 2')
    
    # export project to a tsv file
    # export_project(bbb,oooutput('/tmp2/MicrosoftAcademicGraph_clean/Affiliations.tsv'))


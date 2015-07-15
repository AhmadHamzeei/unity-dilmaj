#! /usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (C) 2015 Ahmad Hamzeei <ahmadhamzeei@gmail.com>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Unity, Gio
import sqlite3
import urllib
import subprocess

GROUP_NAME = 'com.canonical.Unity.Scope.Info.Dilmaj'
UNIQUE_PATH = '/com/canonical/unity/scope/info/dilmaj'
SEARCH_HINT = 'Translate'
NO_RESULTS_HINT = 'Sorry, there are no results that match your search.'
PROVIDER_CREDITS = ''
SVG_DIR = '/usr/share/icons/unity-icon-theme/places/svg/'
PROVIDER_ICON = SVG_DIR+'service-yelp.svg'
DEFAULT_RESULT_ICON = SVG_DIR+'result-info.svg'
DEFAULT_RESULT_MIMETYPE = 'text/html'
DEFAULT_RESULT_TYPE = Unity.ResultType.PERSONAL

c1 = {'id'      :'results',
      'name'    :'Result',
      'icon'    :SVG_DIR+'group-installed.svg',
      'renderer':Unity.CategoryRenderer.VERTICAL_TILE}
CATEGORIES = [c1]
FILTERS = []
EXTRA_METADATA = []

def search(search, filters):
    '''
    Dilmaj: Search for words in database
    '''
    results = []
    if len(search) < 1:
        return results
    
    db = sqlite3.connect('/usr/share/unity-scopes/dilmaj/generic.db')
    cur = db.cursor()
    
    cur.execute("SELECT key, value FROM words WHERE key LIKE :word LIMIT 12", {"word" : search.lower() + '%'})
    rows = cur.fetchall()
    
    for row in rows:
        results.append({'uri':row[0], 'title':row[1], 'icon':'dilmaj'})
    
    db.close()
    
    if len(results) < 1:
        results.append({'uri':search.lower(), 'title':'در واژه نامه موجود نبود!', 'icon':'dilmaj'})
    
    return results

# Classes below this point establish communication
# with Unity, you probably shouldn't modify them.


class MySearch (Unity.ScopeSearchBase):
    def __init__(self, search_context):
        super (MySearch, self).__init__()
        self.set_search_context (search_context)

    def do_run (self):
        '''
        Adds results to the model
        '''
        try:
            result_set = self.search_context.result_set
            for i in search(self.search_context.search_query,
                            self.search_context.filter_state):
                if not 'uri' in i or not i['uri'] or i['uri'] == '':
                    continue
                if not 'icon' in i or not i['icon'] or i['icon'] == '':
                    i['icon'] = DEFAULT_RESULT_ICON
                if not 'mimetype' in i or not i['mimetype'] or i['mimetype'] == '':
                    i['mimetype'] = DEFAULT_RESULT_MIMETYPE
                if not 'result_type' in i or not i['result_type'] or i['result_type'] == '':
                    i['result_type'] = DEFAULT_RESULT_TYPE
                if not 'category' in i or not i['category'] or i['category'] == '':
                    i['category'] = 0
                if not 'title' in i or not i['title']:
                    i['title'] = ''
                if not 'comment' in i or not i['comment']:
                    i['comment'] = ''
                if not 'dnd_uri' in i or not i['dnd_uri'] or i['dnd_uri'] == '':
                    i['dnd_uri'] = i['uri']
                result_set.add_result(**i)
        except Exception as error:
            print (error)

class Preview (Unity.ResultPreviewer):

    def do_run(self):
        '''
        Dilmaj: Preview result when user clicks a word
        '''
        image = Gio.ThemedIcon.new('dilmaj')
        preview = Unity.GenericPreview.new(self.result.uri, '', image)
        preview.props.description_markup = self.result.title
        open_action = Unity.PreviewAction.new("open", "ترجمه گوگل", None)
        preview.add_action(open_action)
        return preview


class Scope (Unity.AbstractScope):
    def __init__(self):
        Unity.AbstractScope.__init__(self)

    def do_get_search_hint (self):
        return SEARCH_HINT

    def do_get_schema (self):
        '''
        Adds specific metadata fields
        '''
        schema = Unity.Schema.new ()
        if EXTRA_METADATA:
            for m in EXTRA_METADATA:
                schema.add_field(m['id'], m['type'], m['field'])
        #FIXME should be REQUIRED for credits
        schema.add_field('provider_credits', 's', Unity.SchemaFieldType.OPTIONAL)
        return schema

    def do_get_categories (self):
        '''
        Adds categories
        '''
        cs = Unity.CategorySet.new ()
        if CATEGORIES:
            for c in CATEGORIES:
                cat = Unity.Category.new (c['id'], c['name'],
                                          Gio.ThemedIcon.new(c['icon']),
                                          c['renderer'])
                cs.add (cat)
        return cs

    def do_get_filters (self):
        '''
        Adds filters
        '''
        fs = Unity.FilterSet.new ()
#        if FILTERS:
#            
        return fs

    def do_get_group_name (self):
        return GROUP_NAME

    def do_get_unique_name (self):
        return UNIQUE_PATH

    def do_create_search_for_query (self, search_context):
        se = MySearch (search_context)
        return se

    def do_create_previewer(self, result, metadata):
        rp = Preview()
        rp.set_scope_result(result)
        rp.set_search_metadata(metadata)
        return rp

    def do_activate(self, result, metadata, id):
        '''
        Dilmaj: Open google translate in web browser when user clicks google translate button
        '''
        parameters = ["x-www-browser", "http://translate.google.com/#en/fa/" + urllib.parse.quote_plus(result.uri)]
        subprocess.Popen(parameters)
        return Unity.ActivationResponse(handled=Unity.HandledType.HIDE_DASH, goto_uri=None)

def load_scope():
    return Scope()


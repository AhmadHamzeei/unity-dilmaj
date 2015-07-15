#!/usr/bin/python3

import sqlite3
import xml.etree.ElementTree as etree

DICT_XML = 'generic.xdb'
tree = etree.parse(DICT_XML)
root = tree.getroot()

DICT_DB  = 'generic.db'
db = sqlite3.connect(DICT_DB)
cur = db.cursor()

try: cur.execute('DROP TABLE words;')
except: pass

cur.execute('CREATE TABLE words(id INTEGER PRIMARY KEY, key TEXT, value TEXT);')

for word in root.findall('word'):
	key = word.find('in').text
	value = word.find('out').text
	cur.execute('INSERT INTO words(key, value) VALUES (?,?)', (key, value))

db.commit()
db.close()


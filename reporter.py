#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import re
import sys
import zipfile

from codecs import getreader
from glob import iglob
from os.path import isfile

import jsonschema

def die(msg):
	sys.stderr.write('{0}\n'.format(msg))
	sys.exit(-1)

def header(title):
	print('{0:{1}^80}'.format(' %s ' % title, '#'))

def load_raw_unicode_escaped_latin1_encoded_json(file):
	reader = getreader('raw_unicode_escape')(file)
	return json.loads(file.read().encode('latin1').decode('utf8', errors='replace'))

def main(args):
	if len(args) == 0 or not isfile(args[0]):
		die('Usage: %s <dump.zip>' % sys.argv[0])

	with zipfile.ZipFile(args[0], 'r') as dump:

		schemas = frozenset(iglob('*/*.json'))
		files = frozenset(filter(lambda f: f.endswith('.json'), dump.namelist()))

		print('Filename: {0}\n'.format(args[0]))

		#
		# Files not covered by a schema
		#
		header('Files not covered by a schema')
		missings = frozenset(filter(lambda f: \
			not f.startswith('messages/') and not f.startswith('photos_and_videos/album/'),
			files - schemas))
		print('%s\n' % '\n'.join(missings) if len(missings) > 0 else '' )

		#
		# Check schemas and files against theirs schemas
		#
		header('Schema Conformance')
		for file in schemas.intersection(files):
			with dump.open(file, 'r') as i, open(file, 'r') as s:
				schema = json.load(s)
				instance = load_raw_unicode_escaped_latin1_encoded_json(i)

			try:
				jsonschema.validate(instance, schema, cls=jsonschema.Draft4Validator)
			except jsonschema.SchemaError as error:
				print('Invalid schema {0}: {1}'.format(file, error.message))
			except jsonschema.ValidationError as error:
				print('Invalid instance {0}: {1}'.format(file, error.message))
		print('')

		#
		# Check messages against message schema
		#
		header('Messages Schema Conformance')
		for file in filter(lambda f: re.match(r'messages/.+/message\.json', f), files):
			with dump.open(file, 'r') as i, open('messages/message.json', 'r') as s:
				schema = json.load(s)
				instance = load_raw_unicode_escaped_latin1_encoded_json(i)

			try:
				jsonschema.validate(instance, schema, cls=jsonschema.Draft4Validator)
			except jsonschema.SchemaError as error:
				print('Invalid schema {0}: {1}'.format(file, error.message))
			except jsonschema.ValidationError as error:
				print('Invalid instance {0}: {1}'.format(file, error.message))
		print('')

		#
		# Check photos and videos against album schema
		#
		header('Photos and Videos Schema Conformance')
		for file in filter(lambda f: f.startswith('photos_and_videos/album/'), files):
			with dump.open(file, 'r') as i, open('photos_and_videos/album/album.json', 'r') as s:
				schema = json.load(s)
				instance = load_raw_unicode_escaped_latin1_encoded_json(i)

			try:
				jsonschema.validate(instance, schema, cls=jsonschema.Draft4Validator)
			except jsonschema.SchemaError as error:
				print('Invalid schema {0}: {1}'.format(file, error.message))
			except jsonschema.ValidationError as error:
				print('Invalid instance {0}: {1}'.format(file, error.message))

if __name__ == '__main__':
	main(sys.argv[1:])

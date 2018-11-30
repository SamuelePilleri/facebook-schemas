#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import os
import re
import sys
import zipfile

from codecs import getreader

import jsonschema

from jsonref import JsonLoader, JsonRef

BASE_URI = 'http://localhost:8080/'

def die(msg):
	sys.stderr.write('{0}\n'.format(msg))
	sys.exit(-1)

def header(title):
	print('{0:#^80}'.format(' %s ' % title))

def read(filename):
	with open(filename, 'r') as file:
		return file.read()

def load_facebook_json(file):
	reader = getreader('raw_unicode_escape')(file)
	return json.loads(reader.read().encode('latin1').decode('utf8'), strict=False)

def validate(filename, instance, schema):
	loader = JsonLoader(store=cache)
	schema = JsonRef.replace_refs(schema, jsonschema=True, loader=loader)

	# Thank you https://github.com/pudo/jsonmapping/blob/4cf0a2/tests/util.py#L25
	resolver = jsonschema.RefResolver(BASE_URI, BASE_URI, store=cache)

	try:
		jsonschema.validate(instance, schema, cls=jsonschema.Draft4Validator, resolver=resolver)
	except jsonschema.SchemaError as error:
		print('Invalid schema {0}: {1}'.format(filename, error.message))
	except jsonschema.ValidationError as error:
		print('Invalid instance {0}: {1}'.format(filename, error.message))
	except Exception as error:
		print('Exception in {0}: {1}'.format(filename, str(error)))

def main(args):
	if len(args) == 0 or not zipfile.is_zipfile(args[0]):
		die('Usage: %s <dump.zip>' % sys.argv[0])

	with zipfile.ZipFile(args[0], 'r') as dump:

		schemas = frozenset([
			os.path.join(dirpath, file)[2:].replace(os.path.sep, '/')
			for dirpath, _, files in os.walk('.')
			for file in files if file.endswith('.json')
		])
		files = frozenset([ file for file in dump.namelist() if file.endswith('.json') ])

		#
		# Populate shared cache for offline schema resolution
		#
		global cache
		cache = { BASE_URI + file: json.loads(read(file)) for file in schemas }

		print('Filename: {0}\n'.format(args[0]))

		#
		# Files not covered by a schema
		#
		header('Files not covered by a schema')
		missings = frozenset([
			file for file in files - schemas
			if not re.match(r'messages/.+/message\.json', file)
			and not file.startswith('photos_and_videos/album/')
		])
		print('%s\n' % '\n'.join(missings) if len(missings) > 0 else '' )

		#
		# Check schemas and files against theirs schemas
		#
		header('Schema Conformance')
		for file in schemas.intersection(files):
			with dump.open(file, 'r') as instance:
				validate(file, load_facebook_json(instance), cache[BASE_URI + file])
		print('')

		#
		# Check messages against message schema
		#
		header('Messages Schema Conformance')
		for file in filter(lambda file: re.match(r'messages/.+/message\.json', file), files):
			with dump.open(file, 'r') as instance:
				validate(file, load_facebook_json(instance),
					cache[BASE_URI + 'messages/message.json'])
		print('')

		#
		# Check photos and videos against album schema
		#
		header('Photos and Videos Schema Conformance')
		for file in filter(lambda file: file.startswith('photos_and_videos/album/'), files):
			with dump.open(file, 'r') as instance:
				validate(file, load_facebook_json(instance),
					cache[BASE_URI + 'photos_and_videos/album/album.json'])

if __name__ == '__main__':
	main(sys.argv[1:])

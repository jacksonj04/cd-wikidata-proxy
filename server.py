from os import environ
import io

from flask import Flask, url_for
from flask import request
from flask import make_response

import csv
import re

import requests
import requests_cache

import urllib.parse

import codecs
from contextlib import closing


def load_map(map_name):

    output = {}

    with open('maps/{}.csv'.format(map_name), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            output[row['dc_id']] = row['wikidata_id']

    return output


PARTY_MAP = load_map('parties')
AREA_MAP = load_map('areas')

requests_cache.install_cache(expire_after=600)

APP = Flask(__name__)


@APP.route('/<election_id>', defaults={'view': 'html'})
@APP.route('/<election_id>/<view>')
def election(election_id, view):

    url = 'https://candidates.democracyclub.org.uk/media/candidates-{id}.csv'.format(id=election_id)

    APP.logger.info('Getting CSV at {url}'.format(
        url=url
    ))

    with closing(requests.get(url, stream=True)) as r:

        reader = csv.DictReader(codecs.iterdecode(r.iter_lines(), 'utf-8'))

        output = io.StringIO()

        fieldnames = [
            'name',
            'dc_id',
            'wikidata_id',
            'party_id',
            'area_id',
            'gender',
            'twitter_username',
            'twfy_id'
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        unmapped_parties = {}
        unmapped_areas = {}
        unmapped_people = {}

        for row in reader:

            person = {
                'name': row['name'],
                'dc_id': row['id'],
                'wikidata_id': row['wikidata_id'],
                'gender': row['gender'].lower(),
                'twitter_username': row['twitter_username']
            }

            if row['party_id'] in PARTY_MAP:
                person['party_id'] = PARTY_MAP[row['party_id']]
            else:
                person['party_id'] = 'UNMAPPED PARTY {}'.format(row['party_id'])
                if row['party_id'] in unmapped_parties:
                    unmapped_parties[row['party_id']]['count'] = unmapped_parties[row['party_id']]['count'] + 1
                else:
                    unmapped_parties[row['party_id']] = {
                        'count': 1,
                        'name': row['party_name']
                    }


            if row['post_id'] in AREA_MAP:
                person['area_id'] = AREA_MAP[row['post_id']]
            else:
                person['area_id'] = 'UNMAPPED POST TO AREA {}'.format(row['post_id'])
                if row['post_id'] in unmapped_areas:
                    unmapped_areas[row['post_id']]['count'] = unmapped_areas[row['post_id']]['count'] + 1
                else:
                    unmapped_areas[row['post_id']] = {
                        'count': 1,
                        'name': row['post_label']
                    }

            if row['parlparse_id']:
                person['twfy_id'] = re.match(r'.*/([0-9]+)', row['parlparse_id']).group(1)

            if (not request.args.get('party')) or (row['party_id'] == request.args.get('party')):

                writer.writerow(person)

        if view == 'csv':

            response = make_response(output.getvalue())
            response.headers["Content-type"] = "text/csv;charset=UTF-8"

            return response

        else:

            output = '<h1>Democracy Club to Wikidata Candidate Data Proxy</h1>'
            output += '<h2>{id}</h2>'.format(id=election_id)
            output += '<p>Source: <code>{url}</code></p>'.format(url=url)
            output += '<hr>'

            if view == 'unmapped-parties':

                output += '<h3>Unmapped Parties Report</h3>'

                output += '<table>'
                output += '<tr><td></td><th>ID</th><th>Name</th><th>Total Instances</th><th>Search</th>''</tr>'

                i = 1
                total = 0

                for (id, data) in sorted(unmapped_parties.items(), key=lambda v: v[1]['count'], reverse=True):
                    output += '<tr>'
                    output += '<td>{}</td><td>{}</td><td>{}</td><td>{}</td>'.format(i, id, data['name'], data['count'])
                    output += '<td><a href="https://www.wikidata.org/w/index.php?search={}" target="_blank">Wikidata</a></td>'.format(urllib.parse.quote(data['name']))
                    output += '</tr>'
                    i += 1
                    total += data['count']

                output += '<tr><td></td><td></td><td></td><td>{}</td></tr>'.format(total)
                output += '</table>'

            elif view == 'unmapped-areas':

                output += '<h3>Unmapped Areas Report</h3>'

                output += '<table>'
                output += '<tr><td></td><th>ID</th><th>Name</th><th>Total Instances</th></tr>'

                i = 1
                total = 0

                for (id, data) in sorted(unmapped_areas.items(), key=lambda v: v[1]['count'], reverse=True):
                    output += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(i, id, data['name'], data['count'])
                    i += 1
                    total += data['count']

                output += '<tr><td></td><td></td><td></td><td>{}</td></tr>'.format(total)
                output += '</table>'

            else:

                output += '<p>HTML view will go here for debugging.</p>'

            output += '<hr>'
            output += '<p><a href="{data_url}">data</a> &middot; <a href="{um_parties_url}">unmapped parties report</a> &middot; <a href="{um_areas_url}">unmapped areas report</a></p>'.format(
                data_url=url_for('election', election_id=election_id),
                um_parties_url=url_for('election', election_id=election_id, view='unmapped-parties'),
                um_areas_url=url_for('election', election_id=election_id, view='unmapped-areas')
            )

            return output


APP.run(
    host='0.0.0.0',
    port=environ.get('PORT')
)

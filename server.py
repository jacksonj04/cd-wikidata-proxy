from os import environ
import io

from flask import Flask
from flask import request
from flask import make_response

import csv
import re

import requests
import requests_cache

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

app = Flask(__name__)


@app.route("/")
def cleanup_csv():

    url = 'https://candidates.democracyclub.org.uk/media/candidates-{id}.csv'.format(id=request.args.get('id'))

    app.logger.info('Getting CSV at {url}'.format(
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

            if row['parlparse_id']:
                person['twfy_id'] = re.match(r'.*/([0-9]+)', row['parlparse_id']).group(1)

            if (not request.args.get('party')) or (row['party_id'] == request.args.get('party')):

                writer.writerow(person)

        if request.args.get('unmapped'):

            if request.args.get('unmapped') == 'parties':

                output = '<h1>Unmapped Parties</h1>'
                output += '<table>'
                output += '<tr><td></td><th>ID</th><th>Name</th><th>Number</th></tr>'

                i = 1
                total = 0

                for (id, data) in sorted(unmapped_parties.items(), key=lambda v: v[1]['count'], reverse=True):
                    output += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(i, id, data['name'], data['count'])
                    i += 1
                    total += data['count']

                output += '<tr><td></td><td></td><td></td><td>{}</td></tr>'.format(total)
                output += '</table>'

                return output

            else:

                return('<p>For unmapped data report, set <code>unmapped</code> to <code>parties</code>.</p>')

        else:

            response = make_response(output.getvalue())
            response.headers["Content-type"] = "text/csv;charset=UTF-8"

            return response


app.run(
    host='0.0.0.0',
    port=environ.get('PORT')
)

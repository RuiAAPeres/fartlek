from typing import Optional
from flask import Flask, request, Response
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import insert
from werkzeug.utils import import_string

from gobiko.apns import APNsClient

import os
import requests

app = Flask(__name__)
configuration = import_string(os.environ['APP_SETTINGS'])()
app.config.from_object(configuration)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

client = APNsClient(
    team_id=os.environ['TEAM_ID'],
    bundle_id=os.environ['BUNDLE_ID'],
    auth_key_id=os.environ['APNS_KEY_ID'],
    auth_key=os.environ['APNS_TOKEN'],
    use_sandbox=configuration.SANDOX
)

from models import *

def check_challenge(key: str) -> Optional[Response]:
    default = Response('Get up on out of here with my Eyeholes!', 401)
    try:
        verification = request.json[key]
        if verification == os.environ['VERIFY_TOKEN']:
            return None
        else:
            return default
    except:
        return default


@app.route('/webhook', methods=['GET'])
def challenge() -> Response:

    challengeOutcome = check_challenge('hub.verify_token')
    if challengeOutcome is not None:
        return challengeOutcome

    challenge = request.values.get('hub.challenge')
    resp = jsonify({'hub.challenge': challenge})

    resp.headers['Content-Type'] = 'application/json'
    resp.status_code = 200
    return resp


@app.route('/webhook', methods=['POST'])
def update() -> Response:

    try:
        print(request.json)
        
        ownerId = request.json["owner_id"]
        athlete = AthleteNotifications.query.filter_by(id=ownerId).first()

        if athlete is None:
            # Strava's API expects a 200
            return Response('User not found', 200)

        client.send_message(
            athlete.token,
            "Dash Notification",
            content_available=True,
            extra=request.json,
            sound='default',
            priority=5,
            topic=os.environ['BUNDLE_ID']
        )
        
        print('Sent...')
        return Response('Success sending Push', 200)

    except Exception as error:
        # Strava's API expects a 200
        return Response('Bad request: {0}'.format(error), 200)


@app.route('/registerUser', methods=['POST'])
def registerUser() -> Response:

    challengeOutcome = check_challenge("verify_token")
    if challengeOutcome is not None:
        return challengeOutcome

    try:
        athleteId = request.json["athlete_id"]
        token = request.json["token"]
        value = AthleteNotifications(id=athleteId, token=token)

        db.session.merge(value)
        db.session.commit()
        return Response("Added", 201)

    except SQLAlchemyError as error:
        return Response('DB exception: {0}'.format(error), 500)

    except Exception as error:
        return Response('Exception: {0}'.format(error), 400)


if __name__ == '__main__':
    # registerCallback()
    app.run()

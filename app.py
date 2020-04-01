import env
import buses
import geocoding
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse


app = Flask(__name__)
app.config.update(
    SECRET_KEY = env.APP_SECRET_KEY,
)
PAT = buses.PATApiHandler(env.PORT_AUTHORITY_API_KEY)
GH = geocoding.GeocodingHandler(env.LOCATION_IQ_API_KEY)


def parse_message(msg):
    # temporary - assume <location>\n<route>\n<direction>
    msg = msg[::-1]
    di, rt, loc = msg.split('\n',maxsplit=2)
    di, rt, loc = di[::-1], rt[::-1], loc[::-1]
    return loc, rt, di


@app.route('/sms', methods=['GET','POST'])
def sms_reply():
    message = request.form['Body']
    location, route, direction = parse_message(message)

    coords = GH.getCoordinates(location)
    etaString = PAT.getETA(coords[0], coords[1], route, direction)

    resp = MessagingResponse()
    resp.message(etaString)
    return str(resp)


if __name__ == "__main__":
    app.run()

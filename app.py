import env
from buses import *
from geocoding import *
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse


app = Flask(__name__)
app.config.update(
    SECRET_KEY = env.APP_SECRET_KEY,
)
PAT = PATApiHandler(env.PORT_AUTHORITY_API_KEY)
GH = GeocodingHandler(env.LOCATION_IQ_API_KEY)


def parse_message(msg):
    # temporary - assume <location>\n<route>\n<direction>
    msg = msg.strip()[::-1]
    di, rt, loc = msg.split('\n',maxsplit=2)
    di, rt, loc = di.strip()[::-1], rt.strip()[::-1], loc.strip()[::-1]
    return loc, rt, di


@app.route('/sms', methods=['POST'])
def sms_reply():
    message = request.form['Body']
    location, route, direction = parse_message(message)

    try:
        coords = GH.getCoordinates(location)
        responseString = PAT.getETA(coords[0], coords[1], route, direction)
    except RouteNotFoundError as ex:
        responseString = str(ex)
    except PredictionsNotFoundError as ex:
        responseString = str(ex)
    except Exception:
        responseString = "Whoops- something went wrong! Try again?"

    resp = MessagingResponse()
    resp.message(responseString)
    return str(resp)


if __name__ == "__main__":
    app.run()

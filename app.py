import env
from flask import Flask, request
from twilio.twiml.messaging_response import Message, MessagingResponse
from twilio.rest import Client

app = Flask(__name__)
app.config.update(
    SECRET_KEY = env.APP_SECRET_KEY,
)
sms = Client(env.TWILIO_API_SID, env.TWILIO_API_TOKEN)

@app.route('/sms', methods=['POST'])
def sms_reply():
    number = request.form['From']
    body = request.form['Body']

    resp = twiml.MessagingResponse()
    resp.message("Hello {}!".format(number))
    return str(resp)

if __name__ == "__main__":
    app.run()

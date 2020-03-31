import env
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
app.config.update(
    SECRET_KEY = env.APP_SECRET_KEY,
)

@app.route('/sms', methods=['GET','POST'])
def sms_reply():
    resp = MessagingResponse()
    resp.message("Hello world!")
    return str(resp)

if __name__ == "__main__":
    app.run()

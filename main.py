"""
Main code for attendance Slackbot. This code is run when a POST request to the server is made.
(Serverless functions built on GCP's serverless framework.)
"""
import time, hashlib, hmac, urllib, json, random
import slack_secrets
import gsheets_handler
import requests

CHALLENGE = False

""" ENTRY POINT """
def parse_request(event):
    # authenticate with Slack
    if CHALLENGE:
        r = event.get_data().decode("utf-8")
        r = json.loads(r)
        return f"HTTP 200 OK\nContent-type: application/x-www-form-urlencoded\nchallenge={r['challenge']}"

    # check if the app is being rate limited
    if event.get_json()['type'] == 'app_rate_limited':
        print("App rate limited")
        return "HTTP 200 OK"

    # verify that the request came from Slack
    if not verifySlackRequest(event):
        return {
            'statusCode': 401,
            'body': 'Unauthorized'
        }
    
    # route the request to the appropriate handler
    data = event.get_json()
    user_id = data['event']['user']
    return router(data, user_id)

# route the request to the appropriate gsheets handler
def router(data, user_id):
    text = data['event']['text']
    channel_id = data['event']['channel']
    if 'register' in text.lower():
        info = gsheets_handler.register_user_handler(user_id, text)
        msg = create_message(info['header'], info['body'], error=True if "Error" in info['header'] else False)
        send_message(msg, channel_id, user_id)
        return {
            'statusCode': 200,
            'body': 'OK'
        }
    elif 'newevent' in text.lower():
        info = gsheets_handler.create_event_handler(user_id, text)
        msg = create_message(info['header'], info['body'], error=True if "Error" in info['header'] else False)
        send_message(msg, channel_id, user_id)
        return {
            'statusCode': 200,
            'body': 'OK'
        }
    elif 'checkin' in text.lower():
        info = gsheets_handler.checkin_handler(user_id, text)
        msg = create_message(info['header'], info['body'], error=True if "Error" in info['header'] else False)
        send_message(msg, channel_id, user_id)
        return {
            'statusCode': 200,
            'body': 'OK'
        }
    elif 'updateme' in text.lower():
        info = gsheets_handler.update_user_handler(user_id)
        msg = create_message(info['header'], info['body'], error=True if "Error" in info['header'] else False)
        send_message(msg, channel_id, user_id)
        return {
            'statusCode': 200,
            'body': 'OK'
        }
    elif 'eventstatus' in text.lower():
        info = gsheets_handler.event_status_handler(user_id, text)
        msg = create_message(info['header'], info['body'], error=True if "Error" in info['header'] else False)
        send_message(msg, channel_id, user_id)
        return {
            'statusCode': 200,
            'body': 'OK'
        }
    else:
        send_message(help, channel_id, user_id)
        return {
            'statusCode': 200,
            'body': 'OK'
        }


""" HELPER FUNCTIONS """

# verify that a request came from Slack by checking the signature
def verifySlackRequest(event):
    headers = event.headers
    request_body = event.get_data().decode("utf-8")
    timestamp = headers.get('X-Slack-Request-Timestamp', None)
    if timestamp is None or abs(time.time() - int(timestamp)) > 60 * 5:
        return False
    sig_basestring = 'v0:' + timestamp + ':' + str(request_body)
    my_signature = 'v0=' + hmac.new(
            slack_secrets.slack_signing_secret,
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
    slack_signature = headers['X-Slack-Signature']
    return hmac.compare_digest(my_signature, slack_signature)

# send an ephemeral message to a Slack channel (only visible to the user)
def send_message(msg, cid, uid):
    data = {
        "Content-Type": "application/json",
        "token": slack_secrets.slack_bot_token,
        "channel": cid,
        "user": uid,
        "text": msg
    }
    r = requests.post("https://slack.com/api/chat.postEphemeral", data=data)
    print(r.text)
    return r

# craft a basic message to send to Slack
def create_message(header="", body="", error=False):
    slack_emojis = ["partying_face", "white_check_mark", "tada", "rocket", "money_mouth_face", "champagne", "confetti_ball", "guitar", "bulb", "ok", "checkered_flag", "smile"]
    message = ""
    if header != "":
        message += f"*{header}*"
        decorator = "bangbang" if error else random.choice(slack_emojis)
        message += f" :{decorator}:\n\n"
    message += body
    return message

# help message
help = "Welcome to the KTP Slackbot! :tada:\nHere are some commands you can use:\n\n*register*: register a user\n*newevent*: add an event and get a unique code\n*checkin*: check in to an event\n*updateme*: see the number of events you've been to\n*eventstatus*: see the number of people checked into an event\n*help*: display this message"
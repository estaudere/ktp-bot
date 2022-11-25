# ktp-bot

KTP Bot is a custom Slack app that functions as an attendance bot for Kappa Theta Pi's Slack workspace, using the Slack Events API and the Google Sheets API. It was influenced by TPEO's own [attendance slack bot](https://github.com/tpeo/attendance-slack-bot).

## Prepping the code

Ensure you have two other files, **google_secrets.py**:

```python
service_account_creds='./xxxx-xxxxxxxx.json'
sheet_id="xxxxxxxxx"
```

and **slack_secrets.py**

```python
slack_signing_secret = b'xxxxxx'
slack_client_id = 'xxxxxxx.xxxxxxxx'
slack_client_secret = 'xxxxxxx'
slack_bot_token = 'xoxb-xxxxx-xxxxxxxxxx'
```

These files are user secrets for Google and Slack, respectively.

## Running locally

Ensure you have [Functions Framework](https://github.com/GoogleCloudPlatform/functions-framework-python) installed, as this code is meant to be run as a serverless function. You can use `pip install requirements.txt` to install the rest of the requirements. Then run `functions-framework --target=parse_requests` to start the server on localhost:8080. [Ngrok](ngrok.io) is suggested to expose localhost to the internet if you'd like another server to make requests to the function (such as the Slack Events API).
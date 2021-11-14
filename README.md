# Klaviyo integration with Slack

This Django app can be used for two purposes:

* notification in slack channel after adding a new list in Klaviyo.
* subscribing an email address to a named list.

## Description

* This is a project for scheduling a slack notification. Whenever a list is added in Klaviyo, a notification is sent to a channel in slack every 30 seconds with the basic list details like name, created and updated date.

* You can use the app to send the user details from a slack slash command and it would subscribe the email to a list mentioned in the slash command and send the welcome email (Note: If you have double opt-in enabled (default behavior), users will not be added to list until they opt-in)

### Help

The format for the slash command should be as below:

```
/subscribe sub=[LIST NAME],[EMAIL ADDRESS]
```
### Dependencies

Install following packages:

```
pip install schedule
pip install klaviyo
pip install python-dotenv
pip install requests
```

### Environment variables required in .env:

You can have your .env anywhere in the project but we recommend having it in the root directory

* PRIVATE_TOKEN=Klaviyo private api key
* PUBLIC_TOKEN=Klaviyo public api key
* SECRET_KEY=your django app key (can be found in setting.py)
* NGROK_URL=Your server url
* SLACK_BOT_TOKEN=slack bot token (one gets generated in slack when you create and app in slack)
* SLACK_BASE_URL=slack api base url
* SLACK_CHANNL_ID=channel ID where you would want your notifications to be triggered

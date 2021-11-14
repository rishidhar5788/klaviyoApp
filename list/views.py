import logging
import os
import requests
import json
import socket
import klaviyo
import datetime
import schedule
from dotenv import load_dotenv, find_dotenv
from django.http import HttpResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

load_dotenv(override=True)
load_dotenv(find_dotenv())

kv_client = klaviyo.Klaviyo(public_token=os.getenv('PUBLIC_TOKEN'), private_token=os.getenv('PRIVATE_TOKEN'))
now = datetime.utcnow()
kv_lists=kv_client.Lists.get_lists()

# Turn on the logging
logging.basicConfig(level=logging.DEBUG)

# Create your views here.
def index(request):
	return HttpResponse("Welocome to my website")

# Slash command to subscribe an email address to the list
@csrf_exempt
def kv_slash(request):
	if 'sub=' in request.POST['text']:
		sub_data=request.POST['text'].split("=")[1]
		sub_info=sub_data.split(",")
		sub_list=sub_info[0]
		if len(sub_info) <= 1:
			return HttpResponse("""\n*Check one or more of these suggested problem solutions:*\n
				:white_check_mark: Either of list name or email are missing\n
				:memo: *HELP* :Format for the slash command is */subscribe sub=[LIST NAME],[EMAIL ADDRESS]*\n
				:white_check_mark: List not present""")
		else:
			sub_email=sub_info[1]

		profiles=[{"email": sub_email}]
		try:
			for kv_list in kv_lists.data:
				if sub_list == kv_list["list_name"]:
					list_id=kv_list["list_id"]
			kv_client.Lists.add_subscribers_to_list(list_id, profiles)
			return HttpResponse(":tada::tada::tada: Successfully Subscribed the email to: *" + sub_list+ "*")
		except Exception as e:
			raise e
	else:
		return HttpResponse(":memo: *HELP* :Format for the slash command is */subscribe sub=[LIST NAME],[EMAIL ADDRESS]*")		
	return HttpResponse(""":x: *Oh no*:exclamation:\n 
				Looks like we have run into an issue! Don't worry :wink:, we have got you covered :grin: 
				\n*Check one or more of these suggested problem solutions:*\n
				:white_check_mark: No information provided for the subscriber\n
				:memo: *HELP* :Format for the slash command is */subscribe sub=[LIST NAME],[EMAIL ADDRESS]*\n
				:white_check_mark: Email address is required\n
				:white_check_mark: Not correct list name provided""")

# Notify in slack when a new list is added to Klaviyo
def demo():
	sorted_kv_list=[]
	for kv_list in kv_lists.data:
		list_id=kv_list["list_id"]
		kv_list_detail=kv_client.Lists.get_list_by_id(list_id)
		sorted_kv_list.append(kv_list_detail.data)

	sorted_kv_list.sort(key=lambda x: x['created'])
	newest_list = sorted_kv_list[-1]

	# block builder for slack
	block_for_slack = get_block_for_slack(newest_list["list_name"],newest_list["folder_name"], 
		newest_list["created"], newest_list["updated"])

	# POST the block data from Klaviyo back to slack
	# Response sent out to slack for showing the data in slack
	slack_channel_call(block_for_slack)

def slack_channel_call(block_for_slack):
	slk_url = os.getenv('SLACK_BASE_URL') + "chat.postMessage"
	slk_payload = "{\"channel\": \"" + os.getenv('SLACK_CHANNL_ID') + "\",\"blocks\":[" + block_for_slack + "]}"
	slk_headers = {
			'Content-Type': 'application/json',
			'Authorization': 'Bearer ' + os.getenv('SLACK_BOT_TOKEN')
		}
	response = requests.request("POST", slk_url, headers=slk_headers, data=slk_payload.encode('utf-8'))
	return response.text

# prepare the json for the block to be sent as a response to slack
def get_block_for_slack(list_name, folder_name,created, updated):
	block = """
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Welcome to the Klaviyo Demo:*\n *Please see the List details below.*\n *details of the list that was added recently*"
			}
		},
	  {
	    "type": "divider"
	  },
	  {
	    "type": "section",
	    "text": {
	      "type": "mrkdwn",
	      "text": "*Newly added List Name*\n:fire:\n""" +list_name+ """ "
	    }
	   },
	  {
	    "type": "section",
	    "text": {
	      "type": "mrkdwn",
	      "text": "*Folder Name*\n:file_folder:\n""" +folder_name+ """ "
	    }
	   },
	  {
	    "type": "section",
	    "text": {
	      "type": "mrkdwn",
	      "text": "\n:factory_worker:\n*Created Date:*\n""" +created+ """ "
	    }
	   },
	  {
	    "type": "section",
	    "text": {
	      "type": "mrkdwn",
	      "text": "*Updated Date:*\n""" +updated+ """ "
	    }
	   }
	"""

	return block

# run the scheduler every 60 seconds to send a notification to the channel for newly added list
schedule.every(60).seconds.do(demo)
while True: 
	schedule.run_pending()
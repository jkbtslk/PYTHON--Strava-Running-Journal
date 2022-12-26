#!/bin/bash
"""
contact - jakub.tesluk@gmail.com
Strava - https://www.strava.com/athletes/23952867
version 1.0 - 26/12/2022
________________________
Script uses Strava API to gather your running activities and sends them to Google Sheet running journal (template can
be found -> .
IMPORTANT - rest days should have the DATE cell empty!

Script consists of two files. Script anc pace_calculator.py. Calculator is necessary to calculate the running pace.

Provide script with an integer - how many last activities (non-running activities included) would you like to analyse
and paste to the Google Sheet. Then script separates non-running activities from running activities and pastes your
running data to Google sheet. The last step is to update the rest days. Script updates all rows with DATE cell empty.

TODO list:
1. Instead of "How many last activities would you like to update", user should be able to choose the starting date.
2. Smart 'rest day' detection.
"""


import gspread, requests, urllib3, time
from oauth2client.service_account import ServiceAccountCredentials
from pace_calulator import calculator
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
number = input("How many last activities would you like to update? ")
scopes = [
	'https://www.googleapis.com/auth/spreadsheets',
	'https://www.googleapis.com/auth/drive'
]

# Enter a path to your Service Account Credentials. If you need help with setting up Google API, please see:
# https://www.youtube.com/watch?v=hyUw-koO2DA
creds = ServiceAccountCredentials.from_json_keyfile_name("XXXXXXXXXXX", scopes = scopes)
file = gspread.authorize(creds)
workbook = file.open_by_key('1ZFauWlLQT8MDHRomemYrFv9g_ErhYaLy-DGffwGqqzk')
sheet = workbook.worksheet('2022')

# Enter your Strava API information below:
auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"
payload = {
	'client_id': "XXXX",
	'client_secret': 'XXXXXXXXXXX',
	'refresh_token': 'XXXXXXXXXXX',
	'grant_type': "refresh_token",
	'f': 'json'
}

# Connecting to Strava and gathering a list of all (as specified at the first step) your last activities.
print("Connecting to Strava...")
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']
print("Access Token = {}.\n"
	  "Access granted.\n".format(access_token))
header_all = {'Authorization': 'Bearer ' + access_token}
param_all = {'per_page': number, 'page': 1}
print(f"Validating last {number} activities on Strava... ")
all_activities = []
my_dataset = requests.get(activites_url, headers=header_all, params=param_all).json()

# Separating running activities from non-running ones and adding them to a list 'all_activities'.
for item in reversed(my_dataset):
	if item["sport_type"] == "Run":
		all_activities.append(item)
print(f"Found {len(all_activities)} running activities!")

# Connecting to Strava again and gathering all running activities data one by one.
# NOTE: It's necessary do it once more as a list of all activities doesn't contain Description field. To get it, script
# has to get one by one activity.
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']
header = {'Authorization': 'Bearer ' + access_token}
activities = []
for activity in all_activities:
	get_activity_url = "https://www.strava.com/api/v3/activities/{}".format(activity['id'])
	my_activity = requests.get(get_activity_url, headers=header).json()
# Adding activities to a list 'activities'.
	activities.append(my_activity)

# Creating a list 'all_dates' which consists of all dates from column Dates in the Google sheet. This list will be used
# to compare values with Strava activities dates. If the date is present in the list = it's a running day, if it's
# absent = it's a rest day.
all_dates = sheet.col_values(1)

# Iterating through all activities
for activity in activities:
	# If the activity date is in the 'all_dates' list, get activity data and send them to Google sheet.
	# Every Google sheet update is followed by 1 second wait time, so the Google query limit (60 activities/minute)
	# won't be breached. If you want to update small amount of activities, you can remove time.sleep(1).
	if activity["start_date_local"][:10] in all_dates:
		activity_date = activity["start_date_local"][:10]
		date = sheet.find(activity_date)
		print(activity['name'], 'at', activity_date, 'found! \nUpdating...')
		sheet.update_cell(date.row, date.col+1, activity['name'])
		time.sleep(1)
		sheet.update_cell(date.row, date.col+2, activity['distance'])
		time.sleep(1)
		sheet.update_cell(date.row, date.col+3, time.strftime("%H:%M:%S", time.gmtime(activity['moving_time'])))
		time.sleep(1)
		sheet.update_cell(date.row, date.col+4, calculator(activity['distance'],activity['moving_time']))
		time.sleep(1)
		sheet.update_cell(date.row, date.col + 6, activity['total_elevation_gain'])
		time.sleep(1)
		sheet.update_cell(date.row, date.col + 7, activity['description'])
		time.sleep(5)
		# This condition is necessary so the script won't break if you didn't measure your HR.
		if activity['has_heartrate'] == True or False:
			sheet.update_cell(date.row, date.col + 5,
							  f"{int(activity['average_heartrate'])} ({int(activity['max_heartrate'])})")
		print(activity['name'], 'updated!\n')

# Now it's time to take care of rest days.
print("\nUpdating rest days...\n")
# Interating through all dates, to get indexes. Indexes will be used to determine row number. If there is no date, it
# means that was a rest day. Index of empty list value = row number.
for index, val in enumerate(all_dates, start=1):
		if val == "":
			sheet.merge_cells(f"B{index}:H{index}", merge_type='MERGE_ALL')
			time.sleep(1)
			sheet.update_cell(index, 2, 'WOLNE')
			time.sleep(1)
			sheet.format(f"B{index}:H{index}",{
				"backgroundColor": {
					"red": 0.65,
					"green": 0.65,
					"blue": 0.65
				},
				"horizontalAlignment": "CENTER",
			})
print("---- UPDATE COMPLETED ----")
print(f'{len(activities)} training days updated!')
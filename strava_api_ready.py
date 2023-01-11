#!/bin/bash

import gspread, requests, urllib3, time
from oauth2client.service_account import ServiceAccountCredentials
from pace_calulator import calculator
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
number = input("How many last activities would you like to update? ")
scopes = [
	'https://www.googleapis.com/auth/spreadsheets',
	'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name("/Users/kuba/PycharmProjects/Strava/credentials.json", scopes = scopes)
file = gspread.authorize(creds)
workbook = file.open_by_key('1nmTc3UuDu8XcLBxmbtCA9pZVLME5IkK3oBMUGN_W3JA')
sheet = workbook.worksheet('2022')

auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"
payload = {
	'client_id': "97763",
	'client_secret': '72c44d8e7ef626651508e19ef45928501bb2afcf',
	'refresh_token': '95e3f5e27b29ea01b4525747434a453d2fed2c05',
	'grant_type': "refresh_token",
	'f': 'json'
}
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
for item in reversed(my_dataset):
	if item["sport_type"] == "Run":
		all_activities.append(item)
print(f"Found {len(all_activities)} running activities!")

res = requests.post(auth_url, data=payload, verify=False) # auth_url & payload referenced in code already above
access_token = res.json()['access_token']
header = {'Authorization': 'Bearer ' + access_token}
activities = []
for activity in all_activities:
	get_activity_url = "https://www.strava.com/api/v3/activities/{}".format(activity['id'])
	my_activity = requests.get(get_activity_url, headers=header).json()
	activities.append(my_activity)

all_dates = sheet.col_values(1)

for activity in activities:
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
		if activity['has_heartrate'] == True or False:
			sheet.update_cell(date.row, date.col + 5,
							  f"{int(activity['average_heartrate'])} ({int(activity['max_heartrate'])})")
		print(activity['name'], 'updated!\n')

print("\nUpdating rest days...\n")
for index, val in enumerate(all_dates, start=1):
		if val == "":
			sheet.merge_cells(f"B{index}:H{index}", merge_type='MERGE_ALL')
			time.sleep(1)
			sheet.update_cell(index, 2, 'WOLNE')
			time.sleep(1)
			sheet.format(f"B{index}:I{index}",{
				"backgroundColor": {
					"red": 0.65,
					"green": 0.65,
					"blue": 0.65
				},
				"horizontalAlignment": "CENTER",
			})
print("---- UPDATE COMPLETED ----")
print(f'{len(activities)} training days updated!')

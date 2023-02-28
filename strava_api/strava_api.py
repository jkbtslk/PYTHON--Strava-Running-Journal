#!/bin/bash
"""
contact - jakub.tesluk@gmail.com
Strava - https://www.strava.com/athletes/23952867
version history 
version 1.0 - 26/12/2022
version 1.1 - 26/02/2023 - rest day detection added
version 1.2 - 27/02/2023 - rest day counter added
________________________
Script uses Strava API to gather your running activities and sends them to Google Sheet running journal (template can
be found here -> https://docs.google.com/spreadsheets/d/1j7l_FCBkn2b91tRHDA_iI0bXczwVnMg0p0RmMQwrH4I/copy.

Script consists of two files. Script anc pace_calculator.py. Calculator is necessary to calculate the running pace.

Provide script with an integer - how many last activities (non-running activities included) would you like to analyse
and paste to the Google Sheet. Then script separates non-running activities from running activities and pastes your
running data to Google sheet. The last step is to update the rest days. Script updates all rows with DATE cell empty.

TODO list:
1. Instead of "How many last activities would you like to update", user should be able to choose the starting date.
"""


#!/bin/bash
import gspread, requests, urllib3, time, os
from oauth2client.service_account import ServiceAccountCredentials
from pace_calulator import calculator
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
number = input("How many last activities would you like to update? ")
scopes = [
	'https://www.googleapis.com/auth/spreadsheets',
	'https://www.googleapis.com/auth/drive'
]
path = os.getcwd()
credentials_path = os.path.join(path, "credentials.json")

creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scopes = scopes)
file = gspread.authorize(creds)
workbook = file.open_by_key('xxxxxWorkBookKeyxxxxx')
sheet = workbook.worksheet('2023')

auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"
payload = {
	'client_id': "97763",
	'client_secret': 'XXXXXXXXXXXXXXXXXXX',
	'refresh_token': 'XXXXXXXXXXXXXXXXXXX',
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
		activity_name = activity['name']
		print(activity_name, 'at', activity_date, 'found! \nUpdating...')
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
		time.sleep(3)
		if activity_name.startswith('Rozbieganie na bieżni'):
			sheet.update_cell(date.row, date.col + 8, "rozbieganie (%)")
		elif activity_name.startswith('Rozbieganie'):
			sheet.update_cell(date.row, date.col + 8, "rozbieganie")
		elif activity_name.startswith('Siła biegowa - podbiegi'):
			sheet.update_cell(date.row, date.col + 8, "siła (podbiegi)")
		elif activity_name.startswith('Siła biegowa - skip'):
			sheet.update_cell(date.row, date.col + 8, "siła (skip)")
		elif activity_name.startswith('Siła biegowa - VK'):
			sheet.update_cell(date.row, date.col + 8, "siła (VK)")
		elif activity_name.startswith('Długie wybieganie'):
			sheet.update_cell(date.row, date.col + 8, "długie wybieganie")
		elif activity_name.startswith('Wycieczka biegowa'):
			sheet.update_cell(date.row, date.col + 8, "wycieczka biegowa")
		elif activity_name.startswith('Rozbieganie na bieżni'):
			sheet.update_cell(date.row, date.col + 8, "rozbieganie (%)")
		elif activity_name.startswith('Zabawa biegowa'):
			sheet.update_cell(date.row, date.col + 8, activity_name[16:])
		elif activity_name.startswith('Drugi zakres na bieżni'):
			sheet.update_cell(date.row, date.col + 8, "drugi zakres (%)")
		elif activity_name.startswith('Drugi zakres -'):
			sheet.update_cell(date.row, date.col + 8, "drugi zakres")
		elif "x400 m" in activity_name:
			sheet.update_cell(date.row, date.col + 8, "400 m")
		elif "x800 m" in activity_name:
			sheet.update_cell(date.row, date.col + 8, "800 m")
		elif "x1 km" in activity_name:
			sheet.update_cell(date.row, date.col + 8, "1 km")
		elif "x200 m" in activity_name:
			sheet.update_cell(date.row, date.col + 8, "1 km")
		if activity['has_heartrate'] == True or False:
			sheet.update_cell(date.row, date.col + 5,
							  f"{int(activity['average_heartrate'])} ({int(activity['max_heartrate'])})")
		print(activity['name'], 'updated!\n')

all_activities_done = sheet.col_values(2)
rest_days = 0
print("\nUpdating rest days...\n")
for index, val in enumerate(all_activities_done, start=1):
		if val == "":
			rest_days += 1
			sheet.merge_cells(f"B{index}:I{index}", merge_type='MERGE_ALL')
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
print(f'{len(activities)} training day(s) updated!')
print(rest_days, 'rest day(s) updated!')

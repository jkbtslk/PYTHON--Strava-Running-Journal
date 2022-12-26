# StravaRunningJournal

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

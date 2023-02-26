# StravaRunningLog

contact - jakub.tesluk@gmail.com
Strava - https://www.strava.com/athletes/23952867
version 1.0 - 26/12/2022
version 1.1 - 26/02/2023 - rest day detection added
________________________
Script uses Strava API to gather your running activities and sends them to Google Sheet running journal (template can
be found here -> https://docs.google.com/spreadsheets/d/1j7l_FCBkn2b91tRHDA_iI0bXczwVnMg0p0RmMQwrH4I/copy.

Script consists of two files. Script anc pace_calculator.py. Calculator is necessary to calculate the running pace.

Provide script with an integer - how many last activities (non-running activities included) would you like to analyse
and paste to the Google Sheet. Then script separates non-running activities from running activities and pastes your
running data to Google sheet. The last step is to update the rest days.

TODO list:
1. Instead of "How many last activities would you like to update", user should be able to choose the starting date.

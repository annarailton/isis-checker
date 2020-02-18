"""Scrapes various EA and OURC websites for Isis river info and
pretty prints to terminal."""

import datetime
import json
import requests


class bcolors:
    RED = '\033[91m'
    AMBER = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BLACK = '\033[7m'
    GREY = '\033[90m'


C2T = {  # colour to terminal code
    'red': bcolors.RED,
    'green': bcolors.GREEN,
    'orange': bcolors.AMBER,
    'amber': bcolors.AMBER,
    'blue': bcolors.BLUE,
    'black': bcolors.BLACK,
    'grey': bcolors.GREY,
}

POSSIBLE_FLAG_COLOURS = ['green', 'blue', 'orange', 'red', 'black', 'grey']


def get_farmoor_data():
    """Scrape the Farmoor gauge data

    TODO get info from API
    https://environment.data.gov.uk/flood-monitoring/id/stations/1100TH/readings?latest

    Returns:
        str: flow rate (with unit)
        str: colour (red, amber or green)
        datetime.datetime: observation date
    """

    response = requests.get(
        f'https://environment.data.gov.uk/flood-monitoring/id/stations/1100TH/readings?latest'
    )
    content = json.loads(response.content.decode('utf-8'))
    flow_rate = float(content['items'][1]['value'])
    datetime_str = content['items'][1]['dateTime']
    observation_datetime = datetime.datetime.strptime(datetime_str,
                                                      '%Y-%m-%dT%H:%M:%SZ')

    if flow_rate >= 55:
        colour = 'red'
    elif 45 <= flow_rate < 55:
        colour = 'amber'
    else:
        colour = 'green'

    return f'{flow_rate:.3f}m^3/s', colour, observation_datetime


def get_flag_data(reach):
    """Fetch the OURCs flag data from API.

    Args:
        reach (str): Either `isis` or `godstow`

    Returns:
        str: flag colour
        datetime.datetime: observation date
    """
    assert reach in ['isis', 'godstow']

    response = requests.get(f'https://ourcs.co.uk/api/flags/status/{reach}')
    content = json.loads(response.content.decode('utf-8'))

    colour = content['status_text'].lower()
    observation_datetime = datetime.datetime.strptime(
        content['set_date'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(microsecond=0)

    return colour, observation_datetime


if __name__ == '__main__':
    farmoor_flow_rate, farmoor_colour, farmoor_time = get_farmoor_data()

    isis_flag, isis_flag_time = get_flag_data('isis')
    godstow_flag, godstow_flag_time = get_flag_data('godstow')

    print(
        f'Farmoor: {C2T[farmoor_colour]}{bcolors.BOLD}{farmoor_flow_rate}{bcolors.ENDC} at {farmoor_time}'
    )

    print(
        f'Isis flag: {C2T[isis_flag]}{bcolors.BOLD}{isis_flag}{bcolors.ENDC} at {isis_flag_time}'
    )
    print(
        f'Godstow flag: {C2T[godstow_flag]}{bcolors.BOLD}{godstow_flag}{bcolors.ENDC} at {godstow_flag_time}'
    )

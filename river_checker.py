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


def get_farmoor_flow_rate():
    """Get Farmoor flow rate data from EA API.

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


def get_isis_flow_rate():
    """Calculate Isis flow rate using Osney and Iffley river level data from  EA API.

  Returns:
      str: flow rate (with unit)
      str: colour (red, amber or green)
      datetime.datetime: observation (calculation) date
  """
    def _get_reading(response):
        """Get data from EA API"""
        content = json.loads(response.content.decode('utf-8'))
        level = content['items']['latestReading']['value']
        observation_datetime = datetime.datetime.strptime(
            content['items']['latestReading']['dateTime'],
            '%Y-%m-%dT%H:%M:%SZ').replace(microsecond=0)

        return level, observation_datetime

    osney_id = '1303TH'
    iffley_id = '1501TH'
    upstream = 'stage'
    downstream = 'downstage'

    osney_downstream_level, osney_downstream_observation_datetime = _get_reading(
        requests.get(
            f'https://environment.data.gov.uk/flood-monitoring/id/measures/{osney_id}-level-{downstream}-i-15_min-mASD'
        ))

    iffley_upstream_level, iffley_downstream_observation_datetime = _get_reading(
        requests.get(
            f'https://environment.data.gov.uk/flood-monitoring/id/measures/{iffley_id}-level-{upstream}-i-15_min-mASD'
        ))

    # Pessimistically chose earliest time
    observation_datetime = min(osney_downstream_observation_datetime,
                               iffley_downstream_observation_datetime)

    # Using Anu Dudhia formula
    flow_rate = 100 * (osney_downstream_level - iffley_upstream_level - 2.07)

    # Using Anu Dudhia levels take from graph on http://eodg.atm.ox.ac.uk/user/dudhia/rowing/river.html
    if flow_rate >= 73:
        colour = 'red'
    elif 53 <= flow_rate < 73:
        colour = 'amber'
    elif 33 <= flow_rate < 53:
        colour = 'blue'
    else:
        colour = 'green'

    return f'{flow_rate:.3f}m^3/s', colour, observation_datetime


if __name__ == '__main__':

    farmoor_flow_rate, farmoor_colour, farmoor_time = get_farmoor_flow_rate()
    isis_flow_rate, isis_colour, isis_time = get_isis_flow_rate()

    isis_flag, isis_flag_time = get_flag_data('isis')
    godstow_flag, godstow_flag_time = get_flag_data('godstow')

    print(
        f'Farmoor: {C2T[farmoor_colour]}{bcolors.BOLD}{farmoor_flow_rate}{bcolors.ENDC} at {farmoor_time}'
    )
    print(
        f'Isis: {C2T[isis_colour]}{bcolors.BOLD}{isis_flow_rate}{bcolors.ENDC} at {isis_time}'
    )
    print(
        f'Isis flag: {C2T[isis_flag]}{bcolors.BOLD}{isis_flag}{bcolors.ENDC} at {isis_flag_time}'
    )
    print(
        f'Godstow flag: {C2T[godstow_flag]}{bcolors.BOLD}{godstow_flag}{bcolors.ENDC} at {godstow_flag_time}'
    )

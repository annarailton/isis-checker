"""Scrapes various EA and OURC websites for Isis river info and
pretty prints to terminal."""

import datetime
import json
import requests

from bs4 import BeautifulSoup


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

    return f'{flow_rate:.0f}m^3/s', colour, observation_datetime


def get_ea_boards():
    """
    Scrapes EA board info from http://riverconditions.environment-agency.gov.uk

    I _think_ the board for a particular lock `X` is given by the board colour for
    the stretch X to Y.

    TODO
    - Check date time format for days (might use single digit)
    - Check if 24h date format
    - Check advice string when no stream warnings
    - Double check which lock the stretches refer to (needs Iffley to go Yellow and Osney on Red)
    """

    request = requests.get('http://riverconditions.environment-agency.gov.uk')
    soup = BeautifulSoup(request.text, 'html.parser')
    advice = soup.find_all(class_='advices')

    above_iffley = advice[0]
    godstow_advice = above_iffley.find_all('td')[-3].find_all(
        'span')[-1].contents[0].lower()
    osney_advice = above_iffley.find_all('td')[-1].find_all(
        'span')[-1].contents[0].lower()

    below_iffley = advice[1]
    iffley_advice = below_iffley.find_all('td')[1].find_all(
        'span')[-1].contents[0].lower()
    sandford_advice = below_iffley.find_all('td')[3].find_all(
        'span')[-1].contents[0].lower()

    advice_to_colour = {
        'caution strong stream': 'red',
        'caution stream increasing': 'yellow',
        'caution stream decreasing': 'yellow',
        'no stream warnings': 'grey',
    }

    last_update = soup.find(class_='last-update').contents[0].replace(
        'Page Last Updated:', '').strip()
    last_update_datetime = datetime.datetime.strptime(last_update,
                                                      '%d %B %Y %H:%M')

    return {
        'last_update_datetime': last_update_datetime,
        'godstow_advice': godstow_advice,
        'godstow_colour': advice_to_colour[godstow_advice],
        'osney_advice': osney_advice,
        'osney_colour': advice_to_colour[osney_advice],
        'iffley_advice': iffley_advice,
        'iffley_colour': advice_to_colour[iffley_advice],
        'sandford_advice': sandford_advice,
        'sandford_colour': advice_to_colour[sandford_advice],
    }


if __name__ == '__main__':

    farmoor_flow_rate, farmoor_colour, farmoor_time = get_farmoor_flow_rate()
    isis_flow_rate, isis_colour, isis_time = get_isis_flow_rate()

    isis_flag, isis_flag_time = get_flag_data('isis')
    godstow_flag, godstow_flag_time = get_flag_data('godstow')

    board_info = get_ea_boards()

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
    print(f'Godstow board: {C2T[board_info["godstow_colour"]]}{bcolors.BOLD}{board_info["godstow_advice"]}{bcolors.ENDC} at {board_info["last_update_datetime"]}')
    print(f'Osney board: {C2T[board_info["osney_colour"]]}{bcolors.BOLD}{board_info["osney_advice"]}{bcolors.ENDC} at {board_info["last_update_datetime"]}')
    print(f'Iffley board: {C2T[board_info["iffley_colour"]]}{bcolors.BOLD}{board_info["iffley_advice"]}{bcolors.ENDC} at {board_info["last_update_datetime"]}')
    print(f'Sandford board: {C2T[board_info["sandford_colour"]]}{bcolors.BOLD}{board_info["sandford_advice"]}{bcolors.ENDC} at {board_info["last_update_datetime"]}')

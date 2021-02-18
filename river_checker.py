"""Scrapes various EA and OURC websites for Isis river info and
pretty prints to terminal."""

import datetime
import json
import requests

from rich.console import Console
from rich.table import Table

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
    'yellow': bcolors.AMBER,
    'blue': bcolors.BLUE,
    'black': bcolors.BLACK,
    'grey': bcolors.GREY,
}

# POSSIBLE_FLAG_COLOURS = ['green', 'blue', 'orange', 'red', 'black', 'grey']
# POSSIBLE_BOARD_COLOURS = ['grey', 'yellow', 'red']


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
    observation_datetime = datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')

    if flow_rate >= 55:
        colour = 'red'
    elif 45 <= flow_rate < 55:
        colour = 'yellow'
    else:
        colour = 'green'

    return ("Farmour", f'[{colour}]{flow_rate:.3f}[/{colour}]', f'{observation_datetime}')


def get_isis_flow_rate():
    """Calculate Isis flow rate using Osney and Iffley river level data from  EA API.

   Returns:
     tuple of flow rate, colour (red, amber or green) and observation (calculation) date
  """
    def _get_reading(response):
        """Get data from EA API"""
        content = json.loads(response.content.decode('utf-8'))
        level = content['items']['latestReading']['value']
        observation_datetime = datetime.datetime.strptime(
            content['items']['latestReading']['dateTime'], '%Y-%m-%dT%H:%M:%SZ'
        ).replace(microsecond=0)

        return level, observation_datetime

    osney_id = '1303TH'
    iffley_id = '1501TH'
    upstream = 'stage'
    downstream = 'downstage'

    osney_downstream_level, osney_downstream_observation_datetime = _get_reading(
        requests.get(
            f'https://environment.data.gov.uk/flood-monitoring/id/measures/{osney_id}-level-{downstream}-i-15_min-mASD'
        )
    )

    iffley_upstream_level, iffley_downstream_observation_datetime = _get_reading(
        requests.get(
            f'https://environment.data.gov.uk/flood-monitoring/id/measures/{iffley_id}-level-{upstream}-i-15_min-mASD'
        )
    )

    # Pessimistically chose earliest time
    observation_datetime = min(
        osney_downstream_observation_datetime, iffley_downstream_observation_datetime
    )

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

    return ("Isis", f'[{colour}]{flow_rate:.3f}[/{colour}]', f'{observation_datetime}')


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

    flag_colour = content['status_text'].lower()

    if flag_colour == 'grey':
        terminal_string = f'[bright_black]{flag_colour}[/bright_black]'
    elif flag_colour == 'black':
        terminal_string = f'[blink][reverse]{flag_colour}[/reverse][/blink]'
    else:
        terminal_string = f'[{flag_colour}]{flag_colour}[/{flag_colour}]'

    observation_datetime = datetime.datetime.strptime(content['set_date'],
                                                      '%Y-%m-%dT%H:%M:%S.%fZ').replace(
                                                          microsecond=0
                                                      )

    return (reach.capitalize(), terminal_string, f'{observation_datetime}')


def get_ea_boards():
    """
    Scrapes EA board info from http://riverconditions.environment-agency.gov.uk

    I _think_ the board for a particular lock `X` is given by the board colour for
    the stretch X to Y.

    TODO
    - Would be better to display like they do on the EA website e.g. "Godstow to Osney lock"
    """

    request = requests.get('http://riverconditions.environment-agency.gov.uk')
    soup = BeautifulSoup(request.text, 'html.parser')
    advice = soup.find_all(class_='advices')

    above_iffley = advice[0]
    godstow_advice = above_iffley.find_all('td')[-3].find_all('span')[-1].contents[0].lower()
    osney_advice = above_iffley.find_all('td')[-1].find_all('span')[-1].contents[0].lower()

    below_iffley = advice[1]
    iffley_advice = below_iffley.find_all('td')[1].find_all('span')[-1].contents[0].lower()
    sandford_advice = below_iffley.find_all('td')[3].find_all('span')[-1].contents[0].lower()

    advice_to_emoji = {
        'caution strong stream': ':red_square:',
        'caution stream increasing': ':yellow_square::arrow_double_up:',
        'caution stream decreasing': ':yellow_square::arrow_double_down:',
        'no stream warnings': ':green_square:',
    }

    last_update = soup.find(class_='last-update').contents[0].replace('Page Last Updated:',
                                                                      '').strip()
    last_update_datetime = datetime.datetime.strptime(last_update, '%d %B %Y %H:%M')

    return [
        ('Godstow', advice_to_emoji[godstow_advice], godstow_advice, f'{last_update_datetime}'),
        ('Osney', advice_to_emoji[osney_advice], osney_advice, f'{last_update_datetime}'),
        ('Iffley', advice_to_emoji[iffley_advice], iffley_advice, f'{last_update_datetime}'),
        ('Sandford', advice_to_emoji[sandford_advice], sandford_advice, f'{last_update_datetime}'),
    ]


if __name__ == '__main__':

    console = Console()

    flow_rate_table = Table(show_header=True, header_style="bold")
    flow_rate_table.add_column("Location")
    flow_rate_table.add_column("Flow rate (m^3/s)")
    flow_rate_table.add_column("Date last updated")
    flow_rate_table.add_row(*get_farmoor_flow_rate())
    flow_rate_table.add_row(*get_isis_flow_rate())

    flag_table = Table(show_header=True, header_style="bold")
    flag_table.add_column("Location")
    flag_table.add_column("Flag :white_flag:")
    flag_table.add_column("Date last updated")
    flag_table.add_row(*get_flag_data('isis'))
    flag_table.add_row(*get_flag_data('godstow'))

    board_table = Table(show_header=True, header_style="bold")
    board_table.add_column("Lock")
    board_table.add_column("Board")
    board_table.add_column("Advice")
    board_table.add_column("Date last updated")
    for row in get_ea_boards():
        board_table.add_row(*row)

    console.print(flow_rate_table)
    console.print(flag_table)
    console.print(board_table)

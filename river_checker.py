"""Scrapes various EA and OURC websites for Isis river info and
pretty prints to terminal."""

from bs4 import BeautifulSoup


class bcolors:
    RED = '\033[91m'
    AMBER = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


POSSIBLE_FLAG_COLOURS = ["green", "blue", "orange", "red", "black", "grey"]


def get_farmour_data():
    """Scrape the Farmour gauge data"""
    with open('farmour.html', 'r') as farmour:
        soup = BeautifulSoup(farmour, 'html.parser')

    farmour_flow_rate = float(
        soup.find(class_='pointlabelValue').contents[0][0:-4])
    farmour_observation_time = soup.find(
        class_='pointlabelTime').contents[0][1:]

    return farmour_flow_rate, farmour_observation_time


def get_flag_data():
    """Scrape the OURCs flag data

    TODO could get flag colour direct from API?
    TODO get date last updated
    """

    with open('ourc_flags.html', 'r') as ourc:
        soup = BeautifulSoup(ourc, 'html.parser')

    isis_background = soup.find(id='isis')['style'].split(' ')
    isis_colour = isis_background[isis_background.index('background:') +
                                  1][:-1]
    godstow_background = soup.find(id='godstow')['style'].split(' ')
    godstow_colour = godstow_background[godstow_background.index('background:')
                                        + 1][:-1]

    return isis_colour, godstow_colour


if __name__ == '__main__':
    farmour_flow_rate, farmour_observation_time = get_farmour_data()

    isis_flag, godstow_flag = get_flag_data()

    if farmour_flow_rate >= 55:
        colour = bcolors.RED
    elif 45 <= farmour_flow_rate < 55:
        colour = bcolors.AMBER
    else:
        colour = bcolors.GREEN
    print(
        f'Farmour: {colour}{bcolors.BOLD}{farmour_flow_rate:.3f}m^3/s{bcolors.ENDC} at {farmour_observation_time}'
    )

    if isis_flag == 'red':
      isis_colour = bcolors.RED
    if godstow_flag == 'red':
      godstow_colour = bcolors.RED

    print(f'Isis flag: {isis_colour}{bcolors.BOLD}{isis_flag}{bcolors.ENDC}')
    print(f'Godstow flag: {godstow_colour}{bcolors.BOLD}{godstow_flag}{bcolors.ENDC}')



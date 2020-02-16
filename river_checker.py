"""Scrapes various EA and OURC websites for Isis river info and
pretty prints to terminal."""

from bs4 import BeautifulSoup
with open('farmour.html') as farmour:
    soup = BeautifulSoup(farmour, 'html.parser')

# print(soup.find(id="linegraph").prettify())

farmour_flow_rate = soup.find(class_='pointlabelValue').contents[0]
farmour_observation_time = soup.find(class_='pointlabelTime').contents[0]

print(farmour_flow_rate[0:-4])
print(farmour_observation_time[1:])

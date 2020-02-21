# isis-checker

Aggregates river info and prints (with nice colours) to the terminal.

Completely unnecessary.

## Information sources

- [EA flood monitoring API](https://environment.data.gov.uk/flood-monitoring/doc/reference)
- [Farmour flow rate](http://www.gaugemap.co.uk/#!Map/Summary/1001/1037)
- [OURCs flag](https://ourcs.co.uk/information/flags/)
    - [API for Isis](https://ourcs.co.uk/api/flags/status/isis/)
    - [API for Godstow](https://ourcs.co.uk/api/flags/status/godstow/)
- [Osney data](https://flood-warning-information.service.gov.uk/station/7057?direction=d)
- [Iffley data](https://flood-warning-information.service.gov.uk/station/7072?direction=u)
- [Thames EA boards](http://riverconditions.environment-agency.gov.uk/)

## EA flood monitoring API

This turns out to be amazing. Full docs [here](https://environment.data.gov.uk/flood-monitoring/doc/reference).

|    Lock/Gauge    |   ID   | RLOI (river level on the internet) ID |                                  Info link                                  |
| ---------------- | ------ | ------------------------------------- | --------------------------------------------------------------------------- |
| Farmoor          | 1100TH |                                  7047 | [Link](https://environment.data.gov.uk/flood-monitoring/id/stations/1100TH) |
| Sutton Courtenay | 1800TH |                                  7084 | [Link](https://environment.data.gov.uk/flood-monitoring/id/stations/1800TH)                                                                            |
| Osney            | 1303TH |                                  7057 | [Link](http://environment.data.gov.uk/flood-monitoring/id/stations/1303TH)  |
| Iffley           | 1501TH |                                  7072 | [Link](http://environment.data.gov.uk/flood-monitoring/id/stations/1501TH)  |
| Sandford         | 1502TH |                                  7405 | [Link](http://environment.data.gov.uk/flood-monitoring/id/stations/1502TH)  |

All the instantaneous info is available on the overview pages linked above but it is possible to get more fine g.rained info (or just return pages with only the information you want on them).

For example, there is `stageScale` and `downstageScale` (*i.e.* up and down stream), so *e.g.* for Osney we have

- [Upstream level](https://environment.data.gov.uk/flood-monitoring/id/stations/1303TH/stageScale)
- [Downstream level](https://environment.data.gov.uk/flood-monitoring/id/stations/1303TH/downstageScale)

To *e.g.* get the flow rate from Farmoor we can look [here](https://environment.data.gov.uk/flood-monitoring/id/stations/1100TH/readings?latest).

## Estimating flow rate

Following the [calculations of Anu Dudhia](http://eodg.atm.ox.ac.uk/user/dudhia/rowing/river.html)

Flow rate F [m3/s] is estimated from `F = 100 ( OD - IU - 2.07 )` where OD and IU are the Osney Downstream and Iffley Upstream measurements (in metres).

The number 2.07 is chosen to give approx zero flow for the OD-IU measurements during dry summer conditions (this ought to match the nominal altitude difference 2.15m between the two locks, but this gives 'negative' flow). The factor 100 is chosen to convert to a flow rate which approximately matches the geometric average of the nearest Thames flow meters which are about 10 miles upstream (Farmoor) and 10 miles dowstream (Sutton Courtenay).

Unfortunately Sutton Courtenay appears to have broken in November. We can probably work out something sensible from the [EA archive](https://environment.data.gov.uk/flood-monitoring/archive) if needs be.
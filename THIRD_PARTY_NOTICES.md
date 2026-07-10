# Third-Party Notices

## pyswisseph 2.10.3.2

This project packages `pyswisseph==2.10.3.2` for exact natal-chart and Human
Design calculations. Its source distribution declares the GNU Affero General
Public License, version 3 or later (AGPL-3.0-or-later). Distribution and hosted
deployment of this project must comply with that license.

The Docker runtime uses a multi-stage build: compilation occurs in the
`ephemeris-builder` stage and only the finished extension wheel is copied into
the production image.

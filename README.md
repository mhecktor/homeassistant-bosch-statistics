# Bosch Statistics

A custom integration that connects to home appliances by bosh using the home connect services.
In order to setup this integration you need get the following information:

- base url for authentication (e.g. `https://api.home-connect.com/`)
- client id
- refresh token

## Capture the required information
In order to get the required information, we used [mitmproxy](https://www.mitmproxy.org/) to intercept the requests from the mobile phone application.
The request payload to `https://api.home-connect.com/security/oauth/token` contains the access token and refresh token, whereas the params contain the client id.
With these information we can authenticate and setup the integration.

## Sensors
This integration contains two sensors:
- Energy (kWh)
- Water Consumption (L)

The sensors are fetched on a 5 minute basis and are showing the current month.

## Limitations
Right now, this is only working for eu and is using the endpoint:
`https://eu.services.home-connect.com/appliance-usage-statistics-webapp/private/api/appliances/<home_appliance_id>/statistics`


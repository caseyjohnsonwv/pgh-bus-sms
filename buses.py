import requests, json, re
from datetime import datetime


class PATApiHandlerError(Exception): pass
class RouteNotFoundError(PATApiHandlerError): pass
class PredictionsNotFoundError(PATApiHandlerError): pass


class PATApiHandler:
    def __init__(self, apiKey):
        self.baseQuery = "http://realtime.portauthority.org/bustime/api/v3/"
        self.queryOptions = "?key={}&tmres=s&localestring=en_US&format=json&rtpidatafeed=Port%20Authority%20Bus".format(apiKey)
        self.predictionsQuery = self.baseQuery + "getpredictions" + self.queryOptions
        self.stopsQuery = self.baseQuery + "getstops" + self.queryOptions

    def queryApi(self, queryString):
        response = requests.get(queryString)
        return json.loads(response.text)['bustime-response']

    def getETA(self, lat, lon, route, direction):
        """
        Finds the next bus arrival for a given route/direction at the closest stop to the user's location.

        lat: float --> user latitude
        lon: float --> user longitude
        route: string --> requested route
        direction: string --> requested direction (INBOUND, OUTBOUND)
        """

        # get all stops on route in selected direction
        queryString = self.stopsQuery + "&rt={}&dir={}".format(route,direction)
        try:
            stopJson = self.queryApi(queryString)['stops']
        except KeyError:
            raise RouteNotFoundError("Route '{}' couldn't be found!".format(route))

        # convert to dictionary- {stop_id:[lat,lon]} - O(n)
        stopTable = {j['stpid']:[j['lat'],j['lon']] for j in stopJson}

        # find closest stop on route to lat/lon - O(n)
        closest = list(stopTable.keys())[0]
        minDist = float("inf")
        for stpid,point in stopTable.items():
            dist = ((lat-point[0])**2)+((lon-point[1])**2)
            # ^ no need for sqrt of distance - order of sorted values wouldn't change
            if dist < minDist:
                minDist = dist
                closest = stpid

        # get all predictions for stop
        queryString = self.predictionsQuery + "&stpid={}".format(closest)
        try:
            predJson = self.queryApi(queryString)['prd']
        except KeyError:
            raise PredictionsNotFoundError("Predictions for stop '{}' couldn't be found!".format(closest))

        # get first prediction time and stop name for correct route and direction
        eta = None
        stpnm = None
        for pred in predJson:
            if pred['rt'].upper().strip() == route.upper().strip() and pred['rtdir'].upper() == direction.upper():
                eta = pred['prdtm']
                stpnm = pred['stpnm']
                break
        if not (eta and stpnm):
            raise PredictionsNotFoundError("Predictions for route '{} {}' couldn't be found!".format(direction, route))

        # convert to human-readable format for sms response
        eta = datetime.strftime(datetime.strptime(eta, "%Y%m%d %H:%M:%S"), "%I:%M")
        msg = "{} {}: Arriving {} at {}.".format(direction, route, eta, stpnm)
        return msg

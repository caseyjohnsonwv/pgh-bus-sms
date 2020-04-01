import requests, json, re
from datetime import datetime


class PATApiHandlerError(Exception): pass
class RouteNotFoundError(PATApiHandlerError): pass
class PredictionsNotFoundError(PATApiHandlerError): pass


class PATApiHandler:
    def __init__(self, apiKey):
        self.baseQuery = "http://realtime.portauthority.org/bustime/api/v3/"
        self.queryOptions = "?key={}&tmres=s&localestring=en_US&format=json&rtpidatafeed=Port%20Authority%20Bus".format(apiKey)
        self.vehicleQuery = self.baseQuery + "getvehicles" + self.queryOptions
        self.predictionsQuery = self.baseQuery + "getpredictions" + self.queryOptions
        self.stopsQuery = self.baseQuery + "getstops" + self.queryOptions

    def queryApi(self, queryString):
        response = requests.get(queryString)
        return json.loads(response.text)['bustime-response']

    """
    def getVehiclesOnRoute(self, route):
        queryString = self.vehicleQuery + "&rt={}".format(route)
        resp = self.queryApi(queryString)
        if 'vehicle' not in resp:
            raise RouteNotFoundError("Route '{}' returned no results!".format(route))
        return resp

    def getPredictionsForVehicles(self, vehicleIds):
        # vehicleIds is a list of vid values - convert to comma-delimited list
        idString=""
        for vid in vehicleIds:
            idString += vid + ","
        idString = idString[:-1]
        # query api and whatnot
        queryString = self.predictionsQuery + "&vid={}".format(idString)
        resp = self.queryApi(queryString)
        if 'prd' not in resp:
            raise PredictionsNotFoundError("No predictions for vehicles '{}'!".format(idString))
        return resp
    """

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
            dist = (lat**2-point[0]**2)+(lon**2-point[1]**2)
            # ^ no need for sqrt of distance - order of sorted values wouldn't change
            if dist < minDist:
                minDist = dist
                closest = stpid

        # get all predictions for stop
        queryString = self.predictionsQuery + "&stpid={}".format(stpid)
        try:
            predJson = self.queryApi(queryString)['prd']
        except KeyError:
            raise PredictionsNotFoundError("Predictions for route '{}' couldn't be found!".format(stpid))

        # get first prediction time and stop name for correct route and direction
        eta = None
        stpnm = None
        for pred in predJson:
            if pred['rt'] == route and pred['rtdir'] == direction:
                eta = pred['prdtm']
                stpnm = pred['stpnm']
                break
        if not (eta and stpnm):
            raise PredictionsNotFoundError("Prediction for route '{} {}' couldn't be found!".format(direction, route))

        # convert to human-readable format for sms response
        eta = datetime.strftime(datetime.strptime(eta, "%Y%m%d %H:%M:%S"), "%I:%M")
        msg = "{} {}: Arriving {} at {}.".format(direction, route, eta, stpnm)
        return msg



"""TESTERS"""

# instantiate API handler
import env
PAT = PATApiHandler(env.PORT_AUTHORITY_API_KEY)

# test message generation
nextBusMsg = PAT.getETA(40.441796934296,-80.002513999999,"28X","OUTBOUND")
print(nextBusMsg)

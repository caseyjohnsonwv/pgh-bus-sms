from geocoder import locationiq


class GeocodingHandler:
    def __init__(self, apiKey):
        self.apiKey = apiKey

    def getCoordinates(self, location):
        response = locationiq(location, key=self.apiKey)
        # return the norhteast corner of the geocoder's bounding box
        return response.json['bbox']['northeast']

import env
g = GeocodingHandler(env.LOCATION_IQ_API_KEY)
coords = g.getCoordinates("PPG Paints Arena, Pittsburgh")
print(coords)

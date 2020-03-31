import env

class PortAuthorityApiHandler:
    def __init__(self):
        self.apiKey = env.PORT_AUTHORITY_API_KEY
        self.apiEndpoint = "http://realtime.portauthority.com/api/v3/getvehicles"
        

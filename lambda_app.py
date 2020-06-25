import urllib.request
import os
import json

# Class to define a home device that to be controlled by Alexa. eg. Lamp
class AlexaHomeApp:
    def __init__(self, applianceId, name, id):
        self.endpointId = applianceId
        self.manufacturerName = "weigao"
        self.friendlyName = name
        self.displayCategories = ["SWITCH"]
        self.capabilities = [
            {
                "type": "AlexaInterface",
                "interface": "Alexa",
                "version": "3"
            },
            {
                "interface": "Alexa.PowerController",
                "version": "3",
                "type": "AlexaInterface",
                "properties": {
                    "supported": [{ "name": "powerState" }],
                    "retrievable": "true"
                }
            }
        ]

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

def lambda_handler(event, context):
    print(event)
    eventname = event["directive"]["header"]["namespace"]
    if eventname == "Alexa.Discovery":
        return handleDiscovery(event["directive"]["header"])
    elif eventname == "Alexa.PowerController":
        return handleControl(event)


base_url = os.environ["BASE_URL"]
tv = AlexaHomeApp("tv", "TV", "tv")
lift = AlexaHomeApp("lift", "Lift", "lift")

# This function return all the devices in a JSON body.
# see document in https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#discovery-messages
def handleDiscovery(header):
    header["name"] = "Discover.Response"

    payload = {"endpoints":
        [
            tv.__dict__,
            lift.__dict__,
        ]
    }

    response = {"event":{
        "header": header,
        "payload": payload
    }}

    print(response)
    return response

# This is the function to handle the event request. The event will be generated when you talk to Alexa Echo with a valid request.
# See https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#onoff-messages
def handleControl(event):
    name = "TurnOnConfirmation"

    event_name = event["header"]["name"]
    applianceId = event["payload"]["appliance"]["applianceId"]

    if event_name == "TurnOnRequest":
        name = "TurnOnConfirmation"
    elif event_name == "TurnOffRequest":
        name = "TurnOffConfirmation"

    if applianceId == "tv":
        power = "on" if event_name == "TurnOnRequest" else "off"
        send_tv_request(power)
    elif applianceId == "lift":
        direction = "up" if event_name == "TurnOnRequest" else "down"
        send_lift_request(direction)

    header = {
        "namespace": "Alexa.ConnectedHome.Control",
        "name": name,
        "payloadVersion": "2",
    }
    return {
        "header": header,
        "payload": {}
    }

def send_tv_request(power):
    url = "{}/tv_power/{}".format(base_url, power)
    urllib.request.urlopen(url)

def send_lift_request(direction):
    url = "{}/move_lift/{}".format(base_url, direction)
    urllib.request.urlopen(url)

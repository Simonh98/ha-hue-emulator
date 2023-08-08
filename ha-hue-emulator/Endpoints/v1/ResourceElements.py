from flask_restful import Resource
from flask import request
from dependency_injector.wiring import Provide, inject
from Bridge.Bridge import Bridge
from Container import Container
from datetime import datetime
from Config import Config
import helpers as helper
from Bridge.User import User
import logging, os, copy, pytz
try:
    from time import tzset
except ImportError:
    tzset = None

log = logging.getLogger(__name__)

# API v1
# ref: https://developers.meethue.com/develop/hue-api/7-configuration-api/

class ResourceElements(Resource):
    
    @inject
    def __init__(
        self,
        bridge_service: Bridge = Provide[Container.bridge_service],
        config_service: Config = Provide[Container.config_service]
    ) -> None:
        self.bridge_service = bridge_service
        self.config_service = config_service

    @property
    def unauthconfig(self):
        return {
            "name": self.bridge_service.name,
            "datastoreversion": self.bridge_service.staticconfig["datastoreversion"],
            "swversion": self.bridge_service.swversion,
            "apiversion": self.bridge_service.apiversion,
            "mac": self.config_service.mac,
            "bridgeid": self.bridge_service.bridgeid,
            "factorynew": False,
            "replacesbridgeid": None,
            "modelid": self.bridge_service.staticconfig["modelid"],
            "starterkitid": ""
        }
        
    @property
    def config(self):
        config = copy.deepcopy(self.bridge_service.staticconfig)
        config.update({
            "Hue Essentials key": self.bridge_service.hue_essentials_key, 
            "Remote API enabled": self.bridge_service.remote_api_enabled, 
            "apiversion": self.bridge_service.apiversion, 
            "bridgeid": self.bridge_service.bridgeid,
            "ipaddress": self.config_service.host,
            "netmask": self.config_service.netmask, 
            "gateway": self.config_service.gateway,
            "mac": self.config_service.mac, 
            "name": self.bridge_service.name, 
            "swversion": self.bridge_service.swversion, 
            "timezone": "none",
            "UTC": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            "localtime": datetime.now(pytz.timezone('Europe/Berlin')).strftime("%Y-%m-%dT%H:%M:%S")
        })
        config["whitelist"] = {}
        for key, user in self.bridge_service.users.items():
            user: User
            config["whitelist"][key] = {
                "create date": user.created,
                "last use date": user.lastused,
                "name": user.name
            }
        # log.info(helper.prettydict(config))
        return config
        
    @property
    def lights(self):
        data = self.bridge_service.getv1lights()
        print(helper.prettydict(data))
        return data
    
    @property
    def groups(self):
        return {}
        
    @property
    def scenes(self):
        return {}
        
    @property
    def rules(self):
        return {}
        
    @property
    def resourcelinks(self):
        return {}
        
    @property
    def schedules(self):
        return {}
        
    @property
    def sensors(self):
        return {}
        
    @property
    def capabilities(self):
        return self.bridge_service.capabilites
    
    # Returns list of all configuration elements in the bridge
    def get(self, username, resource):
        if not self.bridge_service.validate_user(username):
            return self.unauthconfig if resource == 'config' else helper.ErrorMessages.UserNotAuthorized
        try:
            # config, lights, groups, scenes, rules, resourcelinks, schedules, sensors, capabilities
            data = getattr(self, resource)
            # log.info(data)
            return data
        except AttributeError:
            # TODO return correct error message
            return "", 403
    
    
    def post(self, username, resource):
        log.info(f"POST -> {request.path} -> {request.get_json(force=True)}")
        if not self.bridge_service.validate_user(username):
            return [{
                "error": {
                    "type": 1,
                    "address": f"/{resource}/",
                    "description": "unauthorized user"
                }
            }]
            
        # log.info(resource)
        
        
        # authorisation = authorize(username, resource)
        # if "success" not in authorisation:
        #     return authorisation

        # if resource in ["lights", "sensors"] and request.get_data(as_text=True) == "":
        #     print("scan for light")
        #     # if was a request to scan for lights of sensors
        #     Thread(target=scanForLights).start()
        #     return [{"success": {"/" + resource: "Searching for new devices"}}]
        # postDict = request.get_json(force=True)
        # logging.debug(postDict)
        # if resource == "lights":  # add light manually from the web interface
        #     Thread(target=manualAddLight, args=[
        #            postDict["ip"], postDict["protocol"], postDict["config"]]).start()
        #     return [{"success": {"/" + resource: "Searching for new devices"}}]
        # v2Resource = None
        # # find the first unused id for new object
        # new_object_id = nextFreeId(bridgeConfig, resource)
        # postDict["id_v1"] = new_object_id
        # postDict["owner"] = bridgeConfig["apiUsers"][username]
        # if resource == "groups":
        #     if "type" in postDict:
        #         if postDict["type"] == "Zone":
        #             v2Resource = "zone"
        #             bridgeConfig[resource][new_object_id] = HueObjects.Group(postDict)
        #         elif postDict["type"] == "Room":
        #             v2Resource = "room"
        #             bridgeConfig[resource][new_object_id] = HueObjects.Group(postDict)
        #         elif postDict["type"] == "Entertainment":
        #             v2Resource = "entertainment_configuration"
        #             bridgeConfig[resource][new_object_id] = HueObjects.EntertainmentConfiguration(postDict)

        #     if "lights" in postDict:
        #         for light in postDict["lights"]:
        #             bridgeConfig[resource][new_object_id].add_light(
        #                 bridgeConfig["lights"][light])
        #     if "locations" in postDict:
        #         for light, location in postDict["locations"].items():
        #             bridgeConfig[resource][new_object_id].locations[bridgeConfig["lights"]
        #                                                             [light]] = [{"x": location[0], "y": location[1], "z": location[2]}]
        #     # trigger stream messages
        #     GroupZeroMessage()
        # elif resource == "scenes":
        #     v2Resource = "scene"
        #     if "group" in postDict:
        #         postDict["group"] = weakref.ref(
        #             bridgeConfig["groups"][postDict["group"]])
        #     elif "lights" in postDict:
        #         objLights = []
        #         for light in postDict["lights"]:
        #             objLights.append(weakref.ref(
        #                 bridgeConfig["lights"][light]))
        #         postDict["lights"] = objLights
        #     bridgeConfig[resource][new_object_id] = HueObjects.Scene(postDict)
        #     scene = bridgeConfig[resource][new_object_id]
        #     if "lightstates" in postDict:
        #         for light, state in postDict["lightstates"].items():
        #             scene.lightstates[bridgeConfig["lights"][light]] = state
        #     else:
        #         if "group" in postDict:
        #             for light in postDict["group"]().lights:
        #                 scene.lightstates[light()] = {
        #                     "on": light().state["on"]}
        #         elif "lights" in postDict:
        #             for light in postDict["lights"]:
        #                 scene.lightstates[light()] = {
        #                     "on": light().state["on"]}
        #         # add remaining state details in one shot.
        #         sceneStates = list(scene.lightstates.items())
        #         for light, state in sceneStates:
        #             if "bri" in light.state:
        #                 state["bri"] = light.state["bri"]
        #             if "colormode" in light.state:
        #                 if light.state["colormode"] == "ct":
        #                     state["ct"] = light.state["ct"]
        #                 elif light.state["colormode"] == "xy":
        #                     state["xy"] = light.state["xy"]
        #                 elif light.state["colormode"] == "hs":
        #                     state["hue"] = light.state["hue"]
        #                     state["sat"] = light.state["sat"]

        # elif resource == "rules":
        #     bridgeConfig[resource][new_object_id] = HueObjects.Rule(postDict)
        # elif resource == "resourcelinks":
        #     bridgeConfig[resource][new_object_id] = HueObjects.ResourceLink(
        #         postDict)
        # elif resource == "sensors":
        #     v2Resource = "device"
        #     bridgeConfig[resource][new_object_id] = HueObjects.Sensor(postDict)
        # elif resource == "schedules":
        #     bridgeConfig[resource][new_object_id] = HueObjects.Schedule(
        #         postDict)
        # newObject = bridgeConfig[resource][new_object_id]
        # if v2Resource != "none":
        #     streamMessage = {"creationtime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        #                      "data": [],
        #                      "id_v1": "/" + resource + "/" + new_object_id,
        #                      "id": str(uuid.uuid4()),
        #                      "type": "add"
        #                      }
        #     if resource == "groups":
        #         if v2Resource == "room":
        #             streamMessage["data"].append(newObject.getV2Room())
        #         elif v2Resource == "zone":
        #             streamMessage["data"].append(newObject.getV2Zone())
        #         elif  v2Resource == "entertainment_configuration":
        #             streamMessage["data"].append(newObject.getV2Api())
        #         else:
        #             streamMessage["data"].append(newObject.getV2GroupedLight())
        #     elif hasattr(newObject, 'getV2Api'):
        #         streamMessage["data"].append(newObject.getV2Api())
        #     bridgeConfig["temp"]["eventstream"].append(streamMessage)
        #     logging.debug(streamMessage)
        # logging.info(json.dumps([{"success": {"id": new_object_id}}],
        #                         sort_keys=True, indent=4, separators=(',', ': ')))
        # configManager.bridgeConfig.save_config(backup=False, resource=resource)
        # return [{"success": {"id": new_object_id}}]

    # Allows the user to set some configuration values
    def put(self, username, resource):
        log.info(f"PUT -> {request.path} -> {request.get_json(force=True)}")
        # log.info(request.get_json(force=True))
        # return "", 403
        if not self.bridge_service.validate_user(username):
            return [{
                "error": {
                    "type": 1,
                    "address": f"/{resource}/",
                    "description": "unauthorized user"
                }
            }]
        
        data: dict = request.get_json(force=True)
        log.info(f"UPDATE CONFIG: {data}")
        # apply timezone OS variable
        if resource == "config" and "timezone" in data:
            os.environ['TZ'] = data["timezone"]
            if tzset is not None:
                tzset()

        for key, value in data.items():
            if isinstance(value, dict):
                self.bridge_service.staticconfig[key].update(value)
            else:
                self.bridge_service.staticconfig[key] = value

        # build response list
        responseList = []
        response_location = "/" + resource + "/"
        for key, value in data.items():
            responseList.append({"success": {response_location + key: value}})
        log.debug(responseList)
        return responseList
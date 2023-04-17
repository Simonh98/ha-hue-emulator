from flask_restful import Resource
from flask import request
from dependency_injector.wiring import Provide, inject
from Bridge.Bridge import Bridge
from Container import Container
import logging
from dataclasses import asdict

log = logging.getLogger(__name__)

class ClipV2Resource(Resource):
    
    @inject
    def __init__(self, bridge_service: Bridge = Provide[Container.bridge_service]) -> None:
        self.bridge_service = bridge_service
        
        self.get_actions = {
            'scene' : [],
            'light' : [asdict(light) for _, light in self.bridge_service.lights.items()],
            'room' : [], # [s.v2_room() for s in self.bridge_service.groups]
            'zone' : [], # [s.v2_zone() for s in self.bridge_service.groups]
            'grouped_light' : [], # [s.v2_api() for s in self.bridge_service.grouped_lights]
            'zigbee_connectivity' : [], # [s.zigbee() for s in self.bridge_service.lights]
            'entertainment' : [], # [s.v2_entertainment() for s in self.bridge_service.lights]
            'entertainment_configuration' : [], # [s.v2_entertainment_conf() for s in self.bridge_service.groups]
            'device' : [asdict(device) for _, device in self.bridge_service.devices.items()],
            'bridge' : [self.bridge_service.bridge],
            'bridge_home' : [],
            'homekit' : [],
            'behavior_instance' : [],
            'geolocation' : [],
            'geofence_client' : [],
            'behavior_script' : [],
            'motion' : [],
            'device_power' : [],
            'button' : []
        }
    
    def get(self, resource):
        if not self.bridge_service.validate_user(request.headers["hue-application-key"]):
            return "", 403
        try:
            return {'data': self.get_actions[resource], 'erros': []}
        except KeyError:
            return {'erros': [{"description": "Not Found"}]}

    def post(self, resource):
        if not self.bridge_service.validate_user(request.headers["hue-application-key"]):
            return "", 403
        postDict = request.get_json(force=True)
        logging.debug(postDict)
        newObject = None
        if resource == "scene":
            new_object_id = nextFreeId(bridgeConfig, "scenes")
            objCreation = {
                "id_v1": new_object_id,
                "name": postDict["metadata"]["name"],
                "image": postDict["metadata"]["image"]["rid"] if "image" in postDict["metadata"] else None,
                "owner": bridgeConfig["apiUsers"][request.headers["hue-application-key"]],
            }
            if "group" in postDict:
                objCreation["group"] = weakref.ref(
                    getObject(postDict["group"]["rtype"], postDict["group"]["rid"]))
                objCreation["type"] = "GroupScene"
                del postDict["group"]
            elif "lights" in postDict:
                objCreation["type"] = "LightScene"
                objLights = []
                for light in postDict["lights"]:
                    objLights.append(getObject(light["rtype"], light["rid"]))
                objCreation["lights"] = objLights
            objCreation.update(postDict)
            newObject = HueObjects.Scene(objCreation)
            bridgeConfig["scenes"][new_object_id] = newObject
            if "actions" in postDict:
                for action in postDict["actions"]:
                    if "target" in action:
                        if action["target"]["rtype"] == "light":
                            lightObj = getObject(
                                "light",  action["target"]["rid"])
                            sceneState = {}
                            scene = action["action"]
                            if "on" in scene:
                                sceneState["on"] = scene["on"]["on"]
                            if "dimming" in scene:
                                sceneState["bri"] = int(
                                    scene["dimming"]["brightness"] * 2.54)
                            if "color" in scene:
                                if "xy" in scene["color"]:
                                    sceneState["xy"] = [
                                        scene["color"]["xy"]["x"], scene["color"]["xy"]["y"]]
                            if "color_temperature" in scene:
                                if "mirek" in scene["color_temperature"]:
                                    sceneState["ct"] = scene["color_temperature"]["mirek"]
                            if "gradient" in scene:
                                sceneState["gradient"] = scene["gradient"]
                            newObject.lightstates[lightObj] = sceneState
        elif resource == "behavior_instance":
            newObject = HueObjects.BehaviorInstance(postDict)
            bridgeConfig["behavior_instance"][newObject.id_v2] = newObject
        elif resource == "entertainment_configuration":
            new_object_id = nextFreeId(bridgeConfig, "groups")
            objCreation = {
                "id_v1": new_object_id,
                "name": postDict["metadata"]["name"]
            }
            objCreation.update(postDict)
            newObject = HueObjects.EntertainmentConfiguration(objCreation)
            if "locations" in postDict:
                if "service_locations" in postDict["locations"]:
                    for element in postDict["locations"]["service_locations"]:
                        obj = getObject(
                            element["service"]["rtype"], element["service"]["rid"])
                        newObject.add_light(obj)
                        newObject.locations[obj] = element["positions"]
            bridgeConfig["groups"][new_object_id] = newObject
        elif resource in ["room", "zone"]:
            new_object_id = nextFreeId(bridgeConfig, "groups")
            objCreation = {
                "id_v1": new_object_id,
                "name": postDict["metadata"]["name"]
            }
            objCreation["type"] = "Room" if resource == "room" else "Zone"
            if "archetype" in postDict["metadata"]:
                objCreation["icon_class"] = postDict["metadata"]["archetype"].replace("_", " ")
            objCreation.update(postDict)
            newObject = HueObjects.Group(objCreation)
            if "children" in postDict:
                for children in postDict["children"]:
                    obj = getObject(
                        children["rtype"], children["rid"])
                    newObject.add_light(obj)

            bridgeConfig["groups"][new_object_id] = newObject

        # return message
        returnMessage = {"data": [{
            "rid": newObject.id_v2,
            "rtype": resource}
        ], "errors": []}

        logging.debug(json.dumps(returnMessage, sort_keys=True, indent=4))
        return returnMessage
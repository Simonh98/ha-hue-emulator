from flask_restful import Resource
from flask import request
from dependency_injector.wiring import Provide, inject
from Bridge.Bridge import Bridge
from Container import Container
import logging

log = logging.getLogger(__name__)

class ClipV2ResourceId(Resource):
    
    @inject
    def __init__(self, bridge_service: Bridge = Provide[Container.bridge_service]) -> None:
        self.bridge_service = bridge_service
    
    # def get(self, resource, resourceid)
        
    #     if not self.bridge_service.validate_user(request.headers["hue-application-key"]):
    #         return "", 403
        
    #     object = getObject(resource, resourceid)
    #     if not object:
    #         return {"errors": [], "data": []}

    #     if resource in ["scene", "light"]:
    #         return {"errors": [], "data": [object.getV2Api()]}
    #     elif resource == "room":
    #         return {"errors": [], "data": [object.getV2Room()]}
    #     elif resource == "grouped_light":
    #         return {"errors": [], "data": [object.getV2GroupedLight()]}
    #     elif resource == "device":
    #         return {"errors": [], "data": [object.getDevice()]}
    #     elif resource == "zigbee_connectivity":
    #         return {"errors": [], "data": [object.getZigBee()]}
    #     elif resource == "entertainment":
    #         return {"errors": [], "data": [object.getV2Entertainment()]}
    #     elif resource == "entertainment_configuration":
    #         return {"errors": [], "data": [object.getV2Api()]}
    #     elif resource == "bridge":
    #         return {"errors": [], "data": [v2Bridge()]}
    #     elif resource == "device_power":
    #         return {"errors": [], "data": [object.getDevicePower()]}

    # def put(self, resource, resourceid):
    #     logging.debug(request.headers)
    #     authorisation = authorizeV2(request.headers)
    #     if "user" not in authorisation:
    #         return "", 403
    #     putDict = request.get_json(force=True)
    #     logging.debug(putDict)
    #     object = getObject(resource, resourceid)
    #     if resource == "light":
    #         object.setV2State(putDict)
    #     elif resource == "entertainment_configuration":
    #         if "action" in putDict:
    #             if putDict["action"] == "start":
    #                 logging.info("start hue entertainment")
    #                 Thread(target=entertainmentService, args=[
    #                        object, authorisation["user"]]).start()
    #                 for light in object.lights:
    #                     light().update_attr({"state": {"mode": "streaming"}})
    #                 object.update_attr({"stream": {"active": True, "owner": authorisation["user"].username, "proxymode": "auto", "proxynode": "/bridge"}})
    #                 sleep(1)
    #             elif putDict["action"] == "stop":
    #                 logging.info("stop entertainment")
    #                 for light in object.lights:
    #                     light().update_attr({"state": {"mode": "homeautomation"}}) 
    #                 Popen(["killall", "openssl"])
    #                 object.update_attr({"stream": {"active": False}})
    #     elif resource == "scene":
    #         if "recall" in putDict:
    #             object.activate(putDict)
    #         if "speed" in putDict:
    #             object.speed = putDict["speed"]
    #         if "palette" in putDict:
    #             object.palette = putDict["palette"]
    #         if "metadata" in putDict:
    #             object.name = putDict["metadata"]["name"]
    #     elif resource == "grouped_light":
    #         object.setV2Action(putDict)
    #     elif resource == "geolocation":
    #         bridgeConfig["sensors"]["1"].protocol_cfg = {
    #             "lat": putDict["latitude"], "long": putDict["longitude"]}
    #         bridgeConfig["sensors"]["1"].config["configured"] = True
    #     elif resource == "behavior_instance":
    #         object.update_attr(putDict)
    #     elif resource in ["room", "zone"]:
    #         v1Api = {}
    #         if "metadata" in putDict:
    #             if "name" in putDict["metadata"]:
    #                 v1Api["name"] = putDict["metadata"]["name"]
    #             if "archetype" in putDict["metadata"]:
    #                 v1Api["icon_class"] = putDict["metadata"]["archetype"].replace("_", " ")
    #         if "children" in putDict:
    #             for children in putDict["children"]:
    #                 obj = getObject(
    #                     children["rtype"], children["rid"])
    #                 object.add_light(obj)
    #         object.update_attr(v1Api)
    #     response = {"data": [{
    #         "rid": resourceid,
    #         "rtype": resource
    #     }]}

    #     return response

    # def delete(self, resource, resourceid):
    #     # logging.debug(request.headers)
    #     authorisation = authorizeV2(request.headers)
    #     if "user" not in authorisation:
    #         return "", 403
    #     object = getObject(resource, resourceid)

    #     if hasattr(object, 'getObjectPath'):
    #         del bridgeConfig[object.getObjectPath()["resource"]
    #                          ][object.getObjectPath()["id"]]
    #     else:
    #         del bridgeConfig[resource][resourceid]

    #     response = {"data": [{
    #         "rid": resourceid,
    #         "rtype": resource
    #     }]}
    #     return response

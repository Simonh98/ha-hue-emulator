from flask_restful import Resource
from flask import request
from dependency_injector.wiring import Provide, inject
from Bridge.Bridge import Bridge
from Container import Container
import logging, dataclasses

log = logging.getLogger(__name__)

class ClipV2(Resource):
    
    @inject
    def __init__(self, bridge_service: Bridge = Provide[Container.bridge_service]) -> None:
        self.bridge_service = bridge_service
    
    def get(self):
        
        if not self.bridge_service.validate_user(request.headers["hue-application-key"]):
            log.error("User not authorized")
            return "", 403
        
        log.info(request)
        
        data = []
        
        # /bridge
        data.append(self.bridge_service.bridge)
        
        # /devices
        for _, device in self.bridge_service.devices.items():
            data.append(dataclasses.asdict(device))
        data.append(self.bridge_service.bridge_device)
        
        # /light
        for _, light in self.bridge_service.lights.items():
            data.append(dataclasses.asdict(light))
            
        data.append(self.bridge_service.bridgezigbee)
        
        # # homekit
        # data.append(v2HomeKit())
        # # device
        # data.append(v2BridgeDevice())
        # for key, light in bridgeConfig["lights"].items():
        #     data.append(light.getDevice())
        # for key, sensor in bridgeConfig["sensors"].items():
        #     if sensor.getDevice() != None:
        #         data.append(sensor.getDevice())
        # # bridge
        # data.append(v2Bridge())
        # # zigbee
        # data.append(v2BridgeZigBee())
        # for key, light in bridgeConfig["lights"].items():
        #     data.append(light.getZigBee())
        # for key, sensor in bridgeConfig["sensors"].items():
        #     if sensor.getZigBee() != None:
        #         data.append(sensor.getZigBee())
        # # entertainment
        # data.append(v2BridgeEntertainment())
        # for key, light in bridgeConfig["lights"].items():
        #     data.append(light.getV2Entertainment())
        # # scenes
        # for key, scene in bridgeConfig["scenes"].items():
        #     data.append(scene.getV2Api())
        # # lights
        # for key, light in bridgeConfig["lights"].items():
        #     data.append(light.getV2Api())
        # # room
        # for key, group in bridgeConfig["groups"].items():
        #     if group.type == "Room":
        #         data.append(group.getV2Room())
        #     elif group.type == "Zone":
        #         data.append(group.getV2Zone())
        # # group
        # for key, group in bridgeConfig["groups"].items():
        #     data.append(group.getV2GroupedLight())
        # # entertainment_configuration
        # for key, group in bridgeConfig["groups"].items():
        #     if group.type == "Entertainment":
        #         data.append(group.getV2Api())
        # # bridge home
        # data.append(v2BridgeHome())
        # data.append(v2GeofenceClient())
        # for script in behaviorScripts():
        #     data.append(script)
        # for key, sensor in bridgeConfig["sensors"].items():
        #     motion = sensor.getMotion()
        #     if motion != None:
        #         data.append(motion)
        # for key, sensor in bridgeConfig["sensors"].items():
        #     buttons = sensor.getButtons()
        #     if len(buttons) != 0:
        #         for button in buttons:
        #             data.append(button)
        # for key, sensor in bridgeConfig["sensors"].items():
        #     power = sensor.getDevicePower()
        #     if power != None:
        #         data.append(power)

        # log.info(data)
        return {"errors": [], "data": data}
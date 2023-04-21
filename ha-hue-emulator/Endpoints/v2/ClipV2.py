from flask_restful import Resource
from flask import request
from dependency_injector.wiring import Provide, inject
from Bridge.Bridge import Bridge
from Container import Container
import logging, dataclasses
import helpers as helper
from Bridge.LightProfiles import Device, Light

log = logging.getLogger(__name__)

class ClipV2(Resource):
    
    @inject
    def __init__(self, bridge_service: Bridge = Provide[Container.bridge_service]) -> None:
        self.bridge_service = bridge_service
    
    def get(self):
        
        if not self.bridge_service.validate_user(request.headers["hue-application-key"]):
            log.error("User not authorized")
            return "", 403
        data = []
        
        # # /homekit
        # data.append(self.bridge_service.homekit)
        
        # /bridge
        data.append(self.bridge_service.bridge)
        
        # /devices
        for _, device in self.bridge_service.devices.items():
            device: Device
            data.append(device.asdict())
        data.append(self.bridge_service.bridge_device)
        
        # /light
        for _, light in self.bridge_service.lights.items():
            light: Light
            data.append(light.asdict())
            # log.info(helper.prettydict(data[-1]))
            
        # data.append(self.bridge_service.bridgezigbee)
        
        return {"errors": [], "data": data}
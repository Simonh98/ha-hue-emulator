
import sys
sys.path.append('..')
from flask_restful import Resource
import logging, json
from flask import request
import uuid
from datetime import datetime
from dependency_injector.wiring import Provide, inject
from Bridge.Bridge import Bridge
from Container import Container


log = logging.getLogger(__name__)

class ShortConfig(Resource):
    
    @inject
    def __init__(self, bridge_service: Bridge = Provide[Container.bridge_service]) -> None:
        self.bridge_service = bridge_service
    
    def get(self):
        log.info(f"GET -> {request.path} -> {request.get_json(force=True, silent=True)}")
        return {'apiversion': '1.56.0', 'bridgeid': '000000FFFE000000', 'datastoreversion': '126', 'factorynew': False, 'mac': '00:00:00:00:00:00', 'modelid': 'BSB002', 'name': 'DiyHue Bridge', 'replacesbridgeid': None, 'starterkitid': '', 'swversion': '19561788040'}
        return {
            "apiversion": self.bridge_service.apiversion,
            "bridgeid": self.bridge_service.bridgeid,
            "datastoreversion": self.bridge_service.staticconfig["datastoreversion"],
            "factorynew": False,
            "mac": self.bridge_service.mac,
            "modelid": self.bridge_service.modelid,
            "name": self.bridge_service.name,
            "replacesbridgeid": None,
            "starterkitid": "",
            "swversion": self.bridge_service.swversion
        }

class NewUser(Resource):
    
    def __init__(self, bridge_service: Bridge = Provide[Container.bridge_service]) -> None:
        self.bridge_service = bridge_service

    def get(self):
        return [{
            "error": {
                "type": 4,
                "address": "/api",
                "description": "method, GET, not available for resource, /"
            }
        }]

    def post(self):
        data: dict = request.get_json(force=True)
        devicetype: str = data.get('devicetype', None)
        genclientkey: bool = data.get('generateclientkey', None)
        if devicetype is None or genclientkey is None or not genclientkey:
            log.error(f"{devicetype=} is None or {genclientkey=} is None or not {genclientkey=}")
            return [{
                "error": {
                    "type": 6,
                    "address": f"/api/{list(data.keys())[0]}",
                    "description": f"parameter, {list(data.keys())[0]}, not available"
                }
            }]
        # if self.bridge_service.lastlinkbuttonpushed + 30 >= datetime.now().timestamp():
        if True:
            id = str(uuid.uuid1()).replace('-', '')
            if devicetype.startswith("Hue Essentials"):
                id = f"hueess{id[-26:]}"
            clientkey = str(uuid.uuid4()).replace('-', '').upper()
            response = [{"success": {"username": id, 'clientkey': clientkey}}]
            self.bridge_service.add_user(id, devicetype, clientkey)
            log.info(f"POST -> {request.path} -> {request.get_json(force=True)} | {response=}")
            return response
        else:
            return [
                {"error": {"type": 101, "address": "/api/", "description": "link button not pressed"}}
            ]

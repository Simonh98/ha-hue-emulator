from flask_restful import Resource
from flask import request
from dependency_injector.wiring import Provide, inject
from Bridge.Bridge import Bridge
from Container import Container
from flask import Flask, Response, stream_with_context, Blueprint
import logging, time, json, uuid
from datetime import datetime
import helpers as helper

log = logging.getLogger(__name__)

class Format:

    @staticmethod
    def format_add_light(idv1: str, idv2: str, modelid):
        return {
            "creationtime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data": [helper.v2_entertainement(idv1, idv2, modelid)],
            "id": str(uuid.uuid4()),
            "type": "add"
        }

    @staticmethod
    def format_add_light(idv1: str, idv2: str, modelid):
        return {
            "creationtime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data": [helper.v2_entertainement(idv1, idv2, modelid)],
            "id": str(uuid.uuid4()),
            "type": "add"
        }

class EventStream(Resource):
    
    @inject
    def __init__(self, bridge_service: Bridge = Provide[Container.bridge_service]) -> None:
        self.bridge_service = bridge_service
    
    def get(self):
        def eventstream():
            i = 1
            while True:
                yield ""
                # yield  \
                    # f"id: {int(time.time())}:{i}\n" \
                    # f"data: {json.dumps([self.bridge_service.hass_stream.get()], separators=(',', ':'))}\n\n"
                i = 0 if i > 2e24 else i + 1 
        return Response(stream_with_context(eventstream()), mimetype='text/event-stream; charset=utf-8')
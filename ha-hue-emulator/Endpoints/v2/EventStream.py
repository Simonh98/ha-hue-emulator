from flask_restful import Resource
from flask import request
from dependency_injector.wiring import Provide, inject
from Bridge.Bridge import Bridge
from Messaging import Messaging
from Container import Container
from flask import Flask, Response, stream_with_context, Blueprint
import logging, time, json

log = logging.getLogger(__name__)

class EventStream(Resource):
    
    @inject
    def __init__(self,
        bridge_service: Bridge = Provide[Container.bridge_service],
        messaging: Messaging = Provide[Container.messaging_service]
    ) -> None:
        self.bridge_service = bridge_service
        self.messaging = messaging
    
    def get(self):
        def eventstream():
            i = 1
            while True:
                yield  \
                    f"id: {int(time.time())}:{i}\n" \
                    f"data: {json.dumps([self.messaging.v2eventstream.get()], separators=(',', ':'))}\n\n"
                i = 0 if i > 2e24 else i + 1 
        return Response(stream_with_context(eventstream()), mimetype='text/event-stream; charset=utf-8')
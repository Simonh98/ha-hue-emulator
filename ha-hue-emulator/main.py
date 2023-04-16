#!/usr/bin/python3

import logging, sys
from Container import Container

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s,%(msecs)03d %(name)-20s %(levelname)-8s %(message)s', stream=sys.stdout)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def main():
    
    container = Container()
    container.init_resources()
    container.wire(modules=[
        __name__,
        'Api.User',
        'Api.Resource',
        'Api.ResourceElements',
        'Api.ClipV2',
        'Api.ClipV2ResourceId'
    ])
    
    
    config_service = container.config_service()
    bridge_service = container.bridge_service()
    hass_service = container.hass_service()
    
    from Api.HueApi import HueApi
    hue_api = HueApi(config_service, bridge_service)
    
    hass_service.connect()
    hue_api.run_forever()

if __name__ == '__main__':
    main()
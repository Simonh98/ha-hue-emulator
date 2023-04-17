#!/usr/bin/python3

import logging, sys
from Container import Container
import helpers as helper

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
    
    
    from Bridge.LightProfiles import Device
    from Bridge.LightProfiles import Light
    from dataclasses import asdict
    light_hue_go = Light(
        id=helper.getuuid(),
        on=False,
        owner=Light.Owner(helper.getuuid()),
        metadata=Light.Metadata('Hue Go lightservice')
    )
    device_hue_go = Device(
        id=helper.getuuid(),
        services=[],
        product_data=Device.ProductData('LLC020', 'Signify Netherlands B.V.', 'Hue Go'),
        metadata=Device.Metadata('Hue Go device')
    )
    device_hue_go.link_lightservice(light_hue_go)
    
    bridge_service.add_device(device_hue_go)
    bridge_service.add_light(light_hue_go)
    
    
    from Api.HueApi import HueApi
    hue_api = HueApi(config_service, bridge_service)
    
    hass_service.connect()
    hue_api.run_forever()

if __name__ == '__main__':
    main()
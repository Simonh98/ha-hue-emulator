from lights.light_types import lightTypes, archetype
import uuid as uuidlib
import copy
import helpers as helper

class Light:
    
    name: str
    entityid: str
    modelid: str
    uuid: str
    uniqueid: str
    state: dict
    config: dict
    dynamics: dict

    def __init__(
        self, 
        name: str,
        entityid: str,
        modelid: str,
        uuid: str,
        uniqueid: str
    ):
        self.name = name
        self.entityid = entityid
        self.modelid = modelid
        self.uuid = uuid
        self.uniqueid = uniqueid
        self.state = copy.deepcopy(lightTypes[self.modelid]["state"])
        self.config = copy.deepcopy(lightTypes[self.modelid]["config"])
        self.dynamics = copy.deepcopy(lightTypes[self.modelid]["dynamics"])
        self.effect = "no_effect"
        
        self.device = helper.build_device(self.name, self.uuid, self.modelid)
        self.bridgehome = {"rid": self.uuid, "rtype": "light"}
        self.objectpath = {"resource": "lights", "id": self.uuid}
        
        # entertainment
        streamMessage = {"creationtime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "data": [{"id": str(uuid.uuid5(
                             uuid.NAMESPACE_URL, self.id_v2 + 'entertainment')), "type": "entertainent"}],
                         "id": str(uuid.uuid4()),
                         "type": "add"
                         }
        streamMessage["id_v1"] = "/lights/" + self.id_v1
        streamMessage["data"][0].update(self.getV2Entertainment())
        eventstream.append(streamMessage)
        # zigbee_connectivity
        streamMessage = {"creationtime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "data": [self.getZigBee()],
                         "id": str(uuid.uuid4()),
                         "type": "add"
                         }
        eventstream.append(streamMessage)
        # light
        streamMessage = {"creationtime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "data": [self.getV2Api()],
                         "id": str(uuid.uuid4()),
                         "type": "add"
                         }
        eventstream.append(streamMessage)
        # device
        streamMessage = {"creationtime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "data": [self.getDevice()],
                         "id": str(uuid.uuid4()),
                         "type": "add"
                         }
        streamMessage["data"][0].update(self.getDevice())
        eventstream.append(streamMessage)

    def __del__(self):
        ## light ##
        streamMessage = {"creationtime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "data": [{"id": self.id_v2, "type": "light"}],
                         "id": str(uuid.uuid4()),
                         "type": "delete"
                         }
        streamMessage["id_v1"] = "/lights/" + self.id_v1
        eventstream.append(streamMessage)
        ## device ##
        streamMessage = {"creationtime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "data": [{"id": self.getDevice()["id"], "type": "device"}],
                         "id": str(uuid.uuid4()),
                         "type": "delete"
                         }
        streamMessage["id_v1"] = "/lights/" + self.id_v1
        eventstream.append(streamMessage)
        # Zigbee Connectivity
        streamMessage = {"creationtime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "data": [{"id": self.getZigBee()["id"], "type": "zigbee_connectivity"}],
                         "id": str(uuid.uuid4()),
                         "type": "delete"
                         }
        streamMessage["id_v1"] = "/lights/" + self.id_v1
        eventstream.append(streamMessage)
        # Entertainment
        streamMessage = {"creationtime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "data": [{"id": self.getV2Entertainment()["id"], "type": "entertainment"}],
                         "id": str(uuid.uuid4()),
                         "type": "delete"
                         }
        streamMessage["id_v1"] = "/lights/" + self.id_v1
        eventstream.append(streamMessage)
        logging.info(self.name + " light was destroyed.")

    def update_attr(self, newdata):
        for key, value in newdata.items():
            updateAttribute = getattr(self, key)
            if isinstance(updateAttribute, dict):
                updateAttribute.update(value)
                setattr(self, key, updateAttribute)
            else:
                setattr(self, key, value)
        streamMessage = {"creationtime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "data": [self.getDevice()],
                         "id": str(uuid.uuid4()),
                         "type": "update"
                         }
        eventstream.append(streamMessage)

    def updateLightState(self, state):

        if "xy" in state and "xy" in self.state:
            self.state["colormode"] = "xy"
        elif "ct" in state and "ct" in self.state:
            self.state["colormode"] = "ct"
        elif ("hue" in state or "sat" in state) and "hue" in self.state:
            self.state["colormode"] = "hs"

    def setV2State(self, state):
        v1State = v2StateToV1(state)
        if "effects" in state:
            v1State["effect"] = state["effects"]["effect"]
            self.effect = v1State["effect"]
        if "dynamics" in state and "speed" in state["dynamics"]:
            self.dynamics["speed"] = state["dynamics"]["speed"]
        self.setV1State(v1State, advertise=False)
        self.genStreamEvent(state)

    def genStreamEvent(self, v2State):
        streamMessage = {"creationtime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "data": [{"id": self.id_v2, "type": "light"}],
                         "id": str(uuid.uuid4()),
                         "type": "update"
                         }
        streamMessage["id_v1"] = "/lights/" + self.id_v1
        streamMessage["data"][0].update(v2State)
        streamMessage["data"][0].update(
            {"owner": {"rid": self.getDevice()["id"], "rtype": "device"}})
        eventstream.append(streamMessage)

    def getZigBee(self):
        result = {}
        result["id"] = str(uuidlib.uuid5(uuidlib.NAMESPACE_URL, f'{self.uuid}zigbee_connectivity'))
        result["mac_address"] = self.uniqueid[:23]
        result["owner"] = {
            "rid": self.device["id"],
            "rtype": "device"
        }
        result["status"] = "connected" if self.state["reachable"] else "connectivity_issue"
        result["type"] = "zigbee_connectivity"
        return result

    def getV2Api(self):
        result = {}
        result["alert"] = {"action_values": ["breathe"]}
        if self.modelid in ["LCX002", "915005987201", "LCX004"]:
            result["effects"] = {
                "effect_values": [
                    "no_effect",
                    "candle",
                    "fire"
                ],
                "status": self.effect,
                "status_values": [
                    "no_effect",
                    "candle",
                    "fire"
                ]
            }
            result["gradient"] = {"points": self.state["gradient"]["points"],
                                  "points_capable": self.protocol_cfg["points_capable"]}

        # color lights only
        if self.modelid in ["LST002", "LCT001", "LCT015", "LCX002", "915005987201", "LCX004"]:
            colorgamut = lightTypes[self.modelid]["v1_static"]["capabilities"]["control"]["colorgamut"]
            result["color"] = {
                "gamut": {
                    "blue":  {"x": colorgamut[2][0], "y": colorgamut[2][1]},
                    "green": {"x": colorgamut[1][0], "y": colorgamut[1][1]},
                    "red":   {"x": colorgamut[0][0], "y": colorgamut[0][1]}
                },
                "gamut_type": lightTypes[self.modelid]["v1_static"]["capabilities"]["control"]["colorgamuttype"],
                "xy": {
                    "x": self.state["xy"][0],
                    "y": self.state["xy"][1]
                }
            }
        if "ct" in self.state:
            result["color_temperature"] = {
                "mirek": self.state["ct"] if self.state["colormode"] == "ct" else None,
                "mirek_schema": {
                    "mirek_maximum": 500,
                    "mirek_minimum": 153
                }
            }
            result["color_temperature"]["mirek_valid"] = True if self.state[
                "ct"] != None and self.state["ct"] < 500 and self.state["ct"] > 153 else False
        if "bri" in self.state:
            result["dimming"] = {
                "brightness": round(self.state["bri"] / 2.54, 2),
                "min_dim_level": 0.10000000149011612
            }
        result["dynamics"] = self.dynamics
        result["id"] = self.id_v2
        result["id_v1"] = "/lights/" + self.id_v1
        result["metadata"] = {"name": self.name,
                              "archetype": archetype[self.config["archetype"]]}
        result["mode"] = "normal"
        if "mode" in self.state and self.state["mode"] == "streaming":
            result["mode"] = "streaming"
        result["on"] = {
            "on": self.state["on"]
        }
        result["owner"] = {
            "rid": str(uuid.uuid5(uuid.NAMESPACE_URL, self.id_v2 + 'device')),
            "rtype": "device"
        }
        result["type"] = "light"
        return result

    def getV2Entertainment(self):
        entertainmenUuid = str(uuid.uuid5(
            uuid.NAMESPACE_URL, self.id_v2 + 'entertainment'))
        result = {
            "id": entertainmenUuid,
            "id_v1": "/lights/" + self.id_v1,
            "proxy": lightTypes[self.modelid]["v1_static"]["capabilities"]["streaming"]["proxy"],
            "renderer": lightTypes[self.modelid]["v1_static"]["capabilities"]["streaming"]["renderer"]
        }
        result["owner"] = {
            "rid": self.getDevice()["id"], "rtype": "device"}
        result["segments"] = {
            "configurable": False
        }
        if self.modelid == "LCX002":
            result["segments"]["max_segments"] = 7
            result["segments"]["segments"] = [
                {
                    "length": 2,
                    "start": 0
                },
                {
                    "length": 2,
                    "start": 2
                },
                {
                    "length": 4,
                    "start": 4
                },
                {
                    "length": 4,
                    "start": 8
                },
                {
                    "length": 4,
                    "start": 12
                },
                {
                    "length": 2,
                    "start": 16
                },
                {
                    "length": 2,
                    "start": 18
                }]
        elif self.modelid in ["915005987201", "LCX004"]:
            result["segments"]["max_segments"] = 10
            result["segments"]["segments"] = [
                {
                    "length": 3,
                    "start": 0
                },
                {
                    "length": 4,
                    "start": 3
                },
                {
                    "length": 3,
                    "start": 7
                }
            ]
        else:
            result["segments"]["max_segments"] = 1
            result["segments"]["segments"] = [{
                "length": 1,
                "start": 0
            }]
        result["type"] = "entertainment"
        return result

    def dynamicScenePlay(self, palette, index):
        logging.debug("Start Dynamic scene play for " + self.name)
        if "dynamic_palette" in self.dynamics["status_values"]:
            self.dynamics["status"] = "dynamic_palette"
        while self.dynamics["status"] == "dynamic_palette":
            transition = int(30 / self.dynamics["speed"])
            logging.debug("using transistiontime " + str(transition))
            if self.modelid in ["LCT001", "LCT015", "LST002", "LCX002", "915005987201", "LCX004"]:
                if index == len(palette["color"]):
                    index = 0
                points = []
                if self.modelid in ["LCX002", "915005987201", "LCX004"]:
                    gradientIndex = index
                    # for gradient lights
                    for x in range(self.protocol_cfg["points_capable"]):
                        points.append(palette["color"][gradientIndex])
                        gradientIndex += 1
                        if gradientIndex == len(palette["color"]):
                            gradientIndex = 0
                    self.setV2State(
                        {"gradient": {"points": points}, "transitiontime": transition})
                else:
                    lightState = palette["color"][index]
                    # based on youtube videos, the transition is slow
                    lightState["transitiontime"] = transition
                    self.setV2State(lightState)
            elif self.modelid == "LTW001":
                if index == len(palette["color_temperature"]):
                    index = 0
                lightState = palette["color_temperature"][index]
                lightState["transitiontime"] = transition
                self.setV2State(lightState)
            else:
                if index == len(palette["dimming"]):
                    index = 0
                lightState = palette["dimming"][index]
                lightState["transitiontime"] = transition
                self.setV2State(lightState)
            sleep(transition / 10)
            index += 1
            logging.debug("Step forward dynamic scene " + self.name)
        logging.debug("Dynamic Scene " + self.name + " stopped.")

    def save(self):
        result = {"id_v2": self.id_v2, "name": self.name, "modelid": self.modelid, "uniqueid": self.uniqueid,
                  "state": self.state, "config": self.config, "protocol": self.protocol, "protocol_cfg": self.protocol_cfg}
        return result

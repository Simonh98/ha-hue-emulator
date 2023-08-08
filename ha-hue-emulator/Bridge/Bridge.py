from Bridge.User import User
from Bridge.Scene import Scene
from Config import Config
from datetime import datetime
import threading, logging, uuid, traceback
import queue, copy
import helpers as helper
from Bridge.LightProfiles import Device
from Bridge.LightProfiles import Light
import re

log = logging.getLogger(__name__)

class Bridge:
    
    name: str
    mac: str
    apiversion: str
    swversion: str
    bridgeid: str
    modelid: str
    users: dict
    scenes: list[Scene]
    lastlinkbuttonpushed: int
    timezone: str = 'Europe/Berlin'
    
    hassstream = queue.Queue()
    huestream = queue.Queue()
    
    @property
    def staticconfig(self):
        return {
        "backup": {
            "errorcode": 0,
            "status": "idle"
        },
        "datastoreversion": "126",
        "dhcp": True,
        "factorynew": False,
        "internetservices": {
            "internet": "disconnected",
            "remoteaccess": "disconnected",
            "swupdate": "disconnected",
            "time": "disconnected"
        },
        "linkbutton": True,
        "modelid": "BSB002",
        "portalconnection": "disconnected",
        "portalservices": False,
        "portalstate": {
            "communication": "disconnected",
            "incoming": False,
            "outgoing": False,
            "signedon": False
        },
        "proxyaddress": "none",
        "proxyport": 0,
        "replacesbridgeid": None,
        "swupdate": {
            "checkforupdate": False,
            "devicetypes": {
                "bridge": False,
                "lights": [],
                "sensors": []
            },
            "notify": True,
            "text": "",
            "updatestate": 0,
            "url": ""
        },
        "swupdate2": {
            "autoinstall": {
                "on": True,
                "updatetime": "T14:00:00"
            },
            "bridge": {
                "lastinstall": "2022-12-11T17:08:55",
                "state": "noupdates"
            },
            "checkforupdate": False,
            "lastchange": "2022-12-13T10:30:15",
            "state": "unknown"
        },
        "zigbeechannel": 25
    }
    
    @property
    def capabilites(self):
        return  {
                "lights": {
                "available": 60,
                "total": 63
            },
                "sensors": {
                "available": 240,
                "total": 250,
                "clip": {
                    "available": 240,
                    "total": 250
                },
                "zll": {
                    "available": 63,
                    "total": 64
                },
                "zgp": {
                    "available": 63,
                    "total": 64
                }
            },
                "groups": {
                "available": 60,
                "total": 64
            },
                "scenes": {
                "available": 172,
                "total": 200,
                "lightstates": {
                    "available": 10836,
                    "total": 12600
                }
            },
                "schedules": {
                "available": 95,
                "total": 100
            },
                "rules": {
                "available": 233,
                "total": 250,
                "conditions": {
                    "available": 1451,
                    "total": 1500
                },
                "actions": {
                    "available": 964,
                    "total": 1000
                }
            },
                "resourcelinks": {
                "available": 59,
                "total": 64
            },
                "streaming": {
                "available": 1,
                "total": 1,
                "channels": 20
            },
                "timezones": {
                "values": [
                    "CET",
                    "CST6CDT",
                    "EET",
                    "EST",
                    "EST5EDT",
                    "HST",
                    "MET",
                    "MST",
                    "MST7MDT",
                    "PST8PDT",
                    "WET",
                    "Africa/Abidjan",
                    "Africa/Accra",
                    "Africa/Addis_Ababa",
                    "Africa/Algiers",
                    "Africa/Asmara",
                    "Africa/Bamako",
                    "Africa/Bangui",
                    "Africa/Banjul",
                    "Africa/Bissau",
                    "Africa/Blantyre",
                    "Africa/Brazzaville",
                    "Africa/Bujumbura",
                    "Africa/Cairo",
                    "Africa/Casablanca",
                    "Africa/Ceuta",
                    "Africa/Conakry",
                    "Africa/Dakar",
                    "Africa/Dar_es_Salaam",
                    "Africa/Djibouti",
                    "Africa/Douala",
                    "Africa/El_Aaiun",
                    "Africa/Freetown",
                    "Africa/Gaborone",
                    "Africa/Harare",
                    "Africa/Johannesburg",
                    "Africa/Juba",
                    "Africa/Kampala",
                    "Africa/Khartoum",
                    "Africa/Kigali",
                    "Africa/Kinshasa",
                    "Africa/Lagos",
                    "Africa/Libreville",
                    "Africa/Lome",
                    "Africa/Luanda",
                    "Africa/Lubumbashi",
                    "Africa/Lusaka",
                    "Africa/Malabo",
                    "Africa/Maputo",
                    "Africa/Maseru",
                    "Africa/Mbabane",
                    "Africa/Mogadishu",
                    "Africa/Monrovia",
                    "Africa/Nairobi",
                    "Africa/Ndjamena",
                    "Africa/Niamey",
                    "Africa/Nouakchott",
                    "Africa/Ouagadougou",
                    "Africa/Porto-Novo",
                    "Africa/Sao_Tome",
                    "Africa/Tripoli",
                    "Africa/Tunis",
                    "Africa/Windhoek",
                    "America/Adak",
                    "America/Anchorage",
                    "America/Anguilla",
                    "America/Antigua",
                    "America/Araguaina",
                    "America/Aruba",
                    "America/Asuncion",
                    "America/Atikokan",
                    "America/Bahia",
                    "America/Bahia_Banderas",
                    "America/Barbados",
                    "America/Belem",
                    "America/Belize",
                    "America/Blanc-Sablon",
                    "America/Boa_Vista",
                    "America/Bogota",
                    "America/Boise",
                    "America/Cambridge_Bay",
                    "America/Campo_Grande",
                    "America/Cancun",
                    "America/Caracas",
                    "America/Cayenne",
                    "America/Cayman",
                    "America/Chicago",
                    "America/Chihuahua",
                    "America/Costa_Rica",
                    "America/Creston",
                    "America/Cuiaba",
                    "America/Curacao",
                    "America/Danmarkshavn",
                    "America/Dawson",
                    "America/Dawson_Creek",
                    "America/Denver",
                    "America/Detroit",
                    "America/Dominica",
                    "America/Edmonton",
                    "America/Eirunepe",
                    "America/El_Salvador",
                    "America/Fort_Nelson",
                    "America/Fortaleza",
                    "America/Glace_Bay",
                    "America/Goose_Bay",
                    "America/Grand_Turk",
                    "America/Grenada",
                    "America/Guadeloupe",
                    "America/Guatemala",
                    "America/Guayaquil",
                    "America/Guyana",
                    "America/Halifax",
                    "America/Havana",
                    "America/Hermosillo",
                    "America/Inuvik",
                    "America/Iqaluit",
                    "America/Jamaica",
                    "America/Juneau",
                    "America/Kralendijk",
                    "America/La_Paz",
                    "America/Lima",
                    "America/Los_Angeles",
                    "America/Lower_Princes",
                    "America/Maceio",
                    "America/Managua",
                    "America/Manaus",
                    "America/Marigot",
                    "America/Martinique",
                    "America/Matamoros",
                    "America/Mazatlan",
                    "America/Menominee",
                    "America/Merida",
                    "America/Metlakatla",
                    "America/Mexico_City",
                    "America/Miquelon",
                    "America/Moncton",
                    "America/Monterrey",
                    "America/Montevideo",
                    "America/Montserrat",
                    "America/Nassau",
                    "America/New_York",
                    "America/Nipigon",
                    "America/Nome",
                    "America/Noronha",
                    "America/Nuuk",
                    "America/Ojinaga",
                    "America/Panama",
                    "America/Pangnirtung",
                    "America/Paramaribo",
                    "America/Phoenix",
                    "America/Port-au-Prince",
                    "America/Port_of_Spain",
                    "America/Porto_Velho",
                    "America/Puerto_Rico",
                    "America/Punta_Arenas",
                    "America/Rainy_River",
                    "America/Rankin_Inlet",
                    "America/Recife",
                    "America/Regina",
                    "America/Resolute",
                    "America/Rio_Branco",
                    "America/Santarem",
                    "America/Santiago",
                    "America/Santo_Domingo",
                    "America/Sao_Paulo",
                    "America/Scoresbysund",
                    "America/Sitka",
                    "America/St_Barthelemy",
                    "America/St_Johns",
                    "America/St_Kitts",
                    "America/St_Lucia",
                    "America/St_Thomas",
                    "America/St_Vincent",
                    "America/Swift_Current",
                    "America/Tegucigalpa",
                    "America/Thule",
                    "America/Thunder_Bay",
                    "America/Tijuana",
                    "America/Toronto",
                    "America/Tortola",
                    "America/Vancouver",
                    "America/Whitehorse",
                    "America/Winnipeg",
                    "America/Yakutat",
                    "America/Yellowknife",
                    "America/Argentina/Buenos_Aires",
                    "America/Argentina/Catamarca",
                    "America/Argentina/Cordoba",
                    "America/Argentina/Jujuy",
                    "America/Argentina/La_Rioja",
                    "America/Argentina/Mendoza",
                    "America/Argentina/Rio_Gallegos",
                    "America/Argentina/Salta",
                    "America/Argentina/San_Juan",
                    "America/Argentina/San_Luis",
                    "America/Argentina/Tucuman",
                    "America/Argentina/Ushuaia",
                    "America/Indiana/Indianapolis",
                    "America/Indiana/Knox",
                    "America/Indiana/Marengo",
                    "America/Indiana/Petersburg",
                    "America/Indiana/Tell_City",
                    "America/Indiana/Vevay",
                    "America/Indiana/Vincennes",
                    "America/Indiana/Winamac",
                    "America/Kentucky/Louisville",
                    "America/Kentucky/Monticello",
                    "America/North_Dakota/Beulah",
                    "America/North_Dakota/Center",
                    "America/North_Dakota/New_Salem",
                    "Antarctica/Casey",
                    "Antarctica/Davis",
                    "Antarctica/DumontDUrville",
                    "Antarctica/Macquarie",
                    "Antarctica/Mawson",
                    "Antarctica/McMurdo",
                    "Antarctica/Palmer",
                    "Antarctica/Rothera",
                    "Antarctica/Syowa",
                    "Antarctica/Troll",
                    "Antarctica/Vostok",
                    "Arctic/Longyearbyen",
                    "Asia/Aden",
                    "Asia/Almaty",
                    "Asia/Amman",
                    "Asia/Anadyr",
                    "Asia/Aqtau",
                    "Asia/Aqtobe",
                    "Asia/Ashgabat",
                    "Asia/Atyrau",
                    "Asia/Baghdad",
                    "Asia/Bahrain",
                    "Asia/Baku",
                    "Asia/Bangkok",
                    "Asia/Barnaul",
                    "Asia/Beirut",
                    "Asia/Bishkek",
                    "Asia/Brunei",
                    "Asia/Chita",
                    "Asia/Choibalsan",
                    "Asia/Colombo",
                    "Asia/Damascus",
                    "Asia/Dhaka",
                    "Asia/Dili",
                    "Asia/Dubai",
                    "Asia/Dushanbe",
                    "Asia/Famagusta",
                    "Asia/Gaza",
                    "Asia/Hebron",
                    "Asia/Ho_Chi_Minh",
                    "Asia/Hong_Kong",
                    "Asia/Hovd",
                    "Asia/Irkutsk",
                    "Asia/Istanbul",
                    "Asia/Jakarta",
                    "Asia/Jayapura",
                    "Asia/Jerusalem",
                    "Asia/Kabul",
                    "Asia/Kamchatka",
                    "Asia/Karachi",
                    "Asia/Kathmandu",
                    "Asia/Khandyga",
                    "Asia/Kolkata",
                    "Asia/Krasnoyarsk",
                    "Asia/Kuala_Lumpur",
                    "Asia/Kuching",
                    "Asia/Kuwait",
                    "Asia/Macau",
                    "Asia/Magadan",
                    "Asia/Makassar",
                    "Asia/Manila",
                    "Asia/Muscat",
                    "Asia/Nicosia",
                    "Asia/Novokuznetsk",
                    "Asia/Novosibirsk",
                    "Asia/Omsk",
                    "Asia/Oral",
                    "Asia/Phnom_Penh",
                    "Asia/Pontianak",
                    "Asia/Pyongyang",
                    "Asia/Qatar",
                    "Asia/Qostanay",
                    "Asia/Qyzylorda",
                    "Asia/Riyadh",
                    "Asia/Sakhalin",
                    "Asia/Samarkand",
                    "Asia/Seoul",
                    "Asia/Shanghai",
                    "Asia/Singapore",
                    "Asia/Srednekolymsk",
                    "Asia/Taipei",
                    "Asia/Tashkent",
                    "Asia/Tbilisi",
                    "Asia/Tehran",
                    "Asia/Thimphu",
                    "Asia/Tokyo",
                    "Asia/Tomsk",
                    "Asia/Ulaanbaatar",
                    "Asia/Urumqi",
                    "Asia/Ust-Nera",
                    "Asia/Vientiane",
                    "Asia/Vladivostok",
                    "Asia/Yakutsk",
                    "Asia/Yangon",
                    "Asia/Yekaterinburg",
                    "Asia/Yerevan",
                    "Atlantic/Azores",
                    "Atlantic/Bermuda",
                    "Atlantic/Canary",
                    "Atlantic/Cape_Verde",
                    "Atlantic/Faroe",
                    "Atlantic/Madeira",
                    "Atlantic/Reykjavik",
                    "Atlantic/South_Georgia",
                    "Atlantic/St_Helena",
                    "Atlantic/Stanley",
                    "Australia/Adelaide",
                    "Australia/Brisbane",
                    "Australia/Broken_Hill",
                    "Australia/Currie",
                    "Australia/Darwin",
                    "Australia/Eucla",
                    "Australia/Hobart",
                    "Australia/Lindeman",
                    "Australia/Lord_Howe",
                    "Australia/Melbourne",
                    "Australia/Perth",
                    "Australia/Sydney",
                    "Europe/Amsterdam",
                    "Europe/Andorra",
                    "Europe/Astrakhan",
                    "Europe/Athens",
                    "Europe/Belgrade",
                    "Europe/Berlin",
                    "Europe/Bratislava",
                    "Europe/Brussels",
                    "Europe/Bucharest",
                    "Europe/Budapest",
                    "Europe/Busingen",
                    "Europe/Chisinau",
                    "Europe/Copenhagen",
                    "Europe/Dublin",
                    "Europe/Gibraltar",
                    "Europe/Guernsey",
                    "Europe/Helsinki",
                    "Europe/Isle_of_Man",
                    "Europe/Istanbul",
                    "Europe/Jersey",
                    "Europe/Kaliningrad",
                    "Europe/Kiev",
                    "Europe/Kirov",
                    "Europe/Lisbon",
                    "Europe/Ljubljana",
                    "Europe/London",
                    "Europe/Luxembourg",
                    "Europe/Madrid",
                    "Europe/Malta",
                    "Europe/Mariehamn",
                    "Europe/Minsk",
                    "Europe/Monaco",
                    "Europe/Moscow",
                    "Europe/Nicosia",
                    "Europe/Oslo",
                    "Europe/Paris",
                    "Europe/Podgorica",
                    "Europe/Prague",
                    "Europe/Riga",
                    "Europe/Rome",
                    "Europe/Samara",
                    "Europe/San_Marino",
                    "Europe/Sarajevo",
                    "Europe/Saratov",
                    "Europe/Simferopol",
                    "Europe/Skopje",
                    "Europe/Sofia",
                    "Europe/Stockholm",
                    "Europe/Tallinn",
                    "Europe/Tirane",
                    "Europe/Ulyanovsk",
                    "Europe/Uzhgorod",
                    "Europe/Vaduz",
                    "Europe/Vatican",
                    "Europe/Vienna",
                    "Europe/Vilnius",
                    "Europe/Volgograd",
                    "Europe/Warsaw",
                    "Europe/Zagreb",
                    "Europe/Zaporozhye",
                    "Europe/Zurich",
                    "Indian/Antananarivo",
                    "Indian/Chagos",
                    "Indian/Christmas",
                    "Indian/Cocos",
                    "Indian/Comoro",
                    "Indian/Kerguelen",
                    "Indian/Mahe",
                    "Indian/Maldives",
                    "Indian/Mauritius",
                    "Indian/Mayotte",
                    "Indian/Reunion",
                    "Pacific/Apia",
                    "Pacific/Auckland",
                    "Pacific/Bougainville",
                    "Pacific/Chatham",
                    "Pacific/Chuuk",
                    "Pacific/Easter",
                    "Pacific/Efate",
                    "Pacific/Enderbury",
                    "Pacific/Fakaofo",
                    "Pacific/Fiji",
                    "Pacific/Funafuti",
                    "Pacific/Galapagos",
                    "Pacific/Gambier",
                    "Pacific/Guadalcanal",
                    "Pacific/Guam",
                    "Pacific/Honolulu",
                    "Pacific/Kiritimati",
                    "Pacific/Kosrae",
                    "Pacific/Kwajalein",
                    "Pacific/Majuro",
                    "Pacific/Marquesas",
                    "Pacific/Midway",
                    "Pacific/Nauru",
                    "Pacific/Niue",
                    "Pacific/Norfolk",
                    "Pacific/Noumea",
                    "Pacific/Pago_Pago",
                    "Pacific/Palau",
                    "Pacific/Pitcairn",
                    "Pacific/Pohnpei",
                    "Pacific/Port_Moresby",
                    "Pacific/Rarotonga",
                    "Pacific/Saipan",
                    "Pacific/Tahiti",
                    "Pacific/Tarawa",
                    "Pacific/Tongatapu",
                    "Pacific/Wake",
                    "Pacific/Wallis"
                ]
            }
        }

    @property
    def general(self):
        return {
            "type": "bridge",
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{self.bridgeid}bridge")),
            "id_v1": "",
            "owner": {
                "rid": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{self.bridgeid}device")),
                "rtype": "device"
            },
            "bridge_id": self.bridgeid.lower(),
            "time_zone": { "time_zone":  self.timezone },
        }    
    
    @property
    def general(self):
        return {
            "type": "bridge",
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{self.bridgeid}bridge")),
            "id_v1": "",
            "owner": {
                "rid": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{self.bridgeid}device")),
                "rtype": "device"
            },
            "bridge_id": self.bridgeid.lower(),
            "time_zone": { "time_zone":  self.timezone },
        }
        
    @property
    def bridge(self):
        return {
            # 'bridge_id': self.bridgeid.lower(), # TODO
            'bridge_id': '000000fffe000000',
            'id': str(uuid.uuid5(uuid.NAMESPACE_URL, f'{self.bridgeid}bridge')),
            'id_v1': '',
            'identify': {},
            'owner': {'rid': str(uuid.uuid5(uuid.NAMESPACE_URL, f'{self.bridgeid}device')), 'rtype': 'device'},
            'time_zone': {'time_zone': 'Europe/Berlin'},
            'type': 'bridge'
        }

    @property
    def bridge_device(self):
        result = {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, f'{self.bridgeid}device')), "type": "device"}
        result["metadata"] = {
            "archetype": "bridge_v2",
            "name": self.name
        }
        result["product_data"] = {
            "certified": True,
            "manufacturer_name": "Signify Netherlands B.V.",
            "model_id": "BSB002",
            "product_archetype": "bridge_v2",
            "product_name": "Philips hue",
            "software_version": self.apiversion[:5] + self.swversion
        }
        result["services"] = [
            {
                "rid": str(uuid.uuid5(uuid.NAMESPACE_URL, self.bridgeid + 'bridge')),
                "rtype": "bridge"
            },
            {
                "rid": str(uuid.uuid5(uuid.NAMESPACE_URL, self.bridgeid + 'zigbee_connectivity')),
                "rtype": "zigbee_connectivity"
            },
            {
                "rid": str(uuid.uuid5(uuid.NAMESPACE_URL, self.bridgeid + 'entertainment')),
                "rtype": "entertainment"
            }
        ]
        return result
    
    @property
    def bridgezigbee(self):
        return {
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, self.bridgeid + 'zigbee_connectivity')),
            "owner": {
                "rid": str(uuid.uuid5(uuid.NAMESPACE_URL, self.bridgeid + 'device')),
                "rtype": "device"
            },
            "status": "connected",
            "mac_address": self.mac[:8] + ":01:01:" +  self.mac[9:],
            "channel": {
                "value": "channel_25",
                "status": "set"
            },
            "type": "zigbee_connectivity"
        }

    @property
    def homekit(self):
        return {
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f'{self.bridgeid}homekit')),
            "status": "unpaired",
            "type": "homekit",
            "status_values": [
                "pairing",
                "paired",
                "unpaired"
            ]
        }
        
    def __init__(self, config_service: Config) -> None:
        self.name="Emulated Hue"
        self.id = helper.getuuid()
        self.hue_essentials_key = str(uuid.uuid1()).replace('-', '')
        self.remote_api_enabled = False
        self.mac = config_service.mac
        self.apiversion = "1.56.0"
        self.swversion = "19561788040"
        # self.mac = config_service.mac.replace(':', '')
        self.bridgeid = f"{ config_service.mac.replace(':', '')[:6]}FFFE{ config_service.mac.replace(':', '')[-6:]}".upper()
        self.modelid = "BSB002"
        self.lastlinkbuttonpushed = 1680384712
        self.users = {}
        self.scenes = []
        self.lights = {}
        self.devices = {}
        self.mutex = threading.Lock()
        
    def add_user(self, id: str, name: str, clientkey: str):
        user = User(id, name, clientkey)
        with self.mutex:
            # TODO: save as yaml
            self.users[id] = user
        log.info(f"Added user -> ({user})")

    def get_user(self, id: str) -> User:
        return self.users.get(id, None)
    
    def validate_user(self, id: str):
        user = self.get_user(id)
        if user is None:
            return False
        user.lastused = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        return True
        
    def add_device(self, device: Device):
        with self.mutex:
            self.devices[device.id] = device
        log.info(f"Added device -> ({device.metadata.name})")
        
    def add_light(self, light: Light):
        with self.mutex:
            self.lights[light.id] = light
        log.info(f"Added light -> ({light.metadata.name})")
        
    def getv1lights(self):
        ret = {}
        for _, device in self.devices.items():
            device: Device
            lightids: list = device.get_light_services()
            if len(lightids) == 0:
                continue
            light: Light = self.lights[lightids[0]] # TODO: consider all linked light services?
            v1id =re.search("\d+", device.id_v1)[0] # TODO
            ret[v1id] = {
                'capabilites': {
                    'certified': True,
                    'control': {
                        'maxlumen': 806, # TODO
                        'mindimlevel': 5000 # TODO
                    },
                    'streaming': {
                        'proxy': False,
                        'renderer': False
                    }
                },
                'config': {
                    'archtype': device.product_data.product_archtype,
                    'direction': 'omnidirectional',
                    'function': 'mixed',
                    'startup': {
                        'configured': True,
                        'mode': 'safety'
                    }
                },
                'type': 'Dimmable light',
                'swversion': device.product_data.software_version,
                'uniqueid': light.uniqueid, # TODO should be part of device
                'manufacturername': device.product_data.manufacturer_name,
                'modelid': device.product_data.model_id,
                'name': device.product_data.product_name,
                'state': {
                    'on': light.on,
                    'alert': 'none', # TODO
                    'reachable': True, # TODO
                    'mode': 'homeautomation',
                },
                'swupdate': {
                    'lastinstall': '2020-12-09T19:13:52',
                    'state': 'noupdates'
                }
            }
            if light.dimming is not None:
                ret[v1id]['state']['bri'] = light.dimming.brightness

            if light.color_temperature is not None:
                ret[v1id]["state"]["ct"] = light.color_temperature.mirek
                ret[v1id]["state"]["colormode"] = 'ct' # TODO (?)

            if light.color is not None:
                ret[v1id]["state"]["xy"] = [light.color.xy.x, light.color.xy.y]
                ret[v1id]["state"]["hue"] = 0 # TODO
                ret[v1id]["state"]["sat"] = 0 # TODO
                ret[v1id]["state"]["colormode"] = 'xy' # TODO (?)

            # if "mode" in self.state:
            #     result["state"]["mode"] = self.state["mode"]
            
        return ret
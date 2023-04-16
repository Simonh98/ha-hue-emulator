from HueObjects.light_types import lightTypes, archetype
import uuid as uuidlib

def safeget(dct, default=None, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return default
    return dct

# def v2_entertainement(idv1, idv2, modelid):
#     result = {
#         "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f'{idv2}entertainment')),
#         "id_v1": f"/lights/{idv1}",
#         "proxy": lightTypes[modelid]["v1_static"]["capabilities"]["streaming"]["proxy"],
#         "renderer": lightTypes[modelid]["v1_static"]["capabilities"]["streaming"]["renderer"]
#     }
#     result["owner"] = {
#         "rid": self.getDevice()["id"], "rtype": "device"}
#     result["segments"] = {
#         "configurable": False
#     }
#     if modelid == "LCX002":
#         result["segments"]["max_segments"] = 7
#         result["segments"]["segments"] = [
#             {
#                 "length": 2,
#                 "start": 0
#             },
#             {
#                 "length": 2,
#                 "start": 2
#             },
#             {
#                 "length": 4,
#                 "start": 4
#             },
#             {
#                 "length": 4,
#                 "start": 8
#             },
#             {
#                 "length": 4,
#                 "start": 12
#             },
#             {
#                 "length": 2,
#                 "start": 16
#             },
#             {
#                 "length": 2,
#                 "start": 18
#             }]
#     elif modelid in ["915005987201", "LCX004"]:
#         result["segments"]["max_segments"] = 10
#         result["segments"]["segments"] = [
#             {
#                 "length": 3,
#                 "start": 0
#             },
#             {
#                 "length": 4,
#                 "start": 3
#             },
#             {
#                 "length": 3,
#                 "start": 7
#             }
#         ]
#     else:
#         result["segments"]["max_segments"] = 1
#         result["segments"]["segments"] = [{
#             "length": 1,
#             "start": 0
#         }]
#     result["type"] = "entertainment"
#     return result

# def build_device(name, uuid, modelid):
#     result = {"id": str(uuidlib.uuid5(uuidlib.NAMESPACE_URL,  f'{uuid}device'))}
#     result["identify"] = {}
#     result["metadata"] = {
#         "archetype": lightTypes[modelid]["device"]["product_archetype"],
#         "name": name
#     }
#     result["product_data"] = lightTypes[modelid]["device"]
#     result["product_data"]["model_id"] = modelid

#     result["services"] = [{
#             "rid": uuid,
#             "rtype": "light"
#         },{
#             "rid": str(uuidlib.uuid5(uuidlib.NAMESPACE_URL, f'{uuid}zigbee_connectivity')),
#             "rtype": "zigbee_connectivity"
#         },{
#             "rid": str(uuidlib.uuid5(uuidlib.NAMESPACE_URL, f'{uuid}entertainment')),
#             "rtype": "entertainment"
#         }]
#     result["type"] = "device"
#     return result

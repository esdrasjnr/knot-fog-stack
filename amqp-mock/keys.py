# ==================== KNoT routing keys ====================

# Northbound routing keys
REGISTER_DEVICE = "device.register"
UNREGISTER_DEVICE = "device.unregister"
UPDATE_SCHEMA = "schema.update"
PUBLISH_DATA = "data.publish"     # has no response message
LIST_DEVICES = "device.cmd.list"
AUTH_DEVICE = "device.cmd.auth"

# Southbound routing keys
UPDATE_DATA = "data.update"       # has no response message
REQUEST_DATA = "data.request"     # has no response message
DEVICE_REGISTERED = "device.registered"
DEVICE_UNREGISTERED = "device.unregistered"
SCHEMA_UPDATED = "schema.updated"
LIST_DEVICES_RESPONSE = "device.list"
AUTH_DEVICE_RESPONSE = "device.auth"

# Routing keys mapper
RESPONSE_ROUTING_KEYS = {
  # northbound messages
  REGISTER_DEVICE: DEVICE_REGISTERED,
  UNREGISTER_DEVICE: DEVICE_UNREGISTERED,
  UPDATE_SCHEMA: SCHEMA_UPDATED,
  LIST_DEVICES: LIST_DEVICES_RESPONSE,
  AUTH_DEVICE: AUTH_DEVICE_RESPONSE,
}

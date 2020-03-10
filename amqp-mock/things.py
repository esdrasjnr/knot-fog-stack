import amqp
import json
import keys
import time

class Things:
  # ==================== CONSTRUCTOR ====================
  def __init__(self, host, port, auth_token):
    self.amqp = amqp.AMQP(host, port)
    self.__auth_token = auth_token

    self.client_publish_exchange = "fogIn"
    self.client_consume_exchange = "fogOut"
    self.connector_publish_exchange = "connOut"
    self.connector_consume_exchange = "connIn"
  # end_def

  # ==================== PRIVATE METHODS ====================

  # ========== Client side methods (KNoTd) ==========

  def __client_publish(self, routing_key, message):
    print("Sending message at %s:%s" % (self.client_publish_exchange, routing_key))
    self.amqp.publish_message(self.client_publish_exchange, routing_key, message, self.__auth_token)
    print("Message sent: %r" % message)
  # end_def

  # def __client_consume(self, routing_key):
  #   print("Listen to message at %s:%s" % (self.client_consume_exchange, routing_key))
  #   self.amqp.consume_message(self.client_consume_exchange, routing_key, lambda msg: print("Message received: %r" % msg))
  # # end_def

  # def __client_publish_and_consume(self, routing_key, message):
  #   self.__client_publish(routing_key, message)
  #   VERIFY IF TIME TO GET RESPONSE MESSAGE AT QUEUE IS ENOUGH
  #   if routing_key in keys.RESPONSE_ROUTING_KEYS:
  #     time.sleep(0.25)    # delay: 15 milliseconds
  #     self.__client_consume(keys.RESPONSE_ROUTING_KEYS[routing_key])
  # # end_def

  def __client_start_consumer(self, on_message):
    southbound_routing_keys = [
      keys.UPDATE_DATA,
      keys.REQUEST_DATA,
      keys.DEVICE_REGISTERED,
      keys.DEVICE_UNREGISTERED,
      keys.SCHEMA_UPDATED,
      keys.LIST_DEVICES_RESPONSE,
      keys.AUTH_DEVICE_RESPONSE,
    ]

    self.amqp.start_messages_consumer(self.client_consume_exchange, southbound_routing_keys, on_message)
  # end_def

  # ========== Connector side methods ==========

  def __connector_publish(self, routing_key, message):
    self.amqp.publish_message(self.connector_publish_exchange, routing_key, message, self.__auth_token)
  # end_def

  def __connector_start_consumer(self, on_message):
    northbound_routing_keys = [
      keys.REGISTER_DEVICE,
      keys.UNREGISTER_DEVICE,
      keys.UPDATE_SCHEMA,
      keys.PUBLISH_DATA,
      keys.LIST_DEVICES,
      keys.AUTH_DEVICE,
    ]

    self.amqp.start_messages_consumer(self.connector_consume_exchange, northbound_routing_keys, on_message)
  # end_def

  # ==================== PUBLIC METHODS ====================

  # ========== Client interactors ==========

  def register_device(self, ID, name):
    message = {
      "id": ID,
      "name": name,
    }

    self.__client_publish(keys.REGISTER_DEVICE, message)
  # def_end

  def unregister_device(self, ID):
    message = {
      "id": ID,
    }

    self.__client_publish(keys.UNREGISTER_DEVICE, message)
  # def_end

  def update_schema(self, ID, schema):
    message = {
      "id": ID,
      "schema": json.loads(schema),
    }

    self.__client_publish(keys.UPDATE_SCHEMA, message)
  # def_end

  def publish_data(self, ID, data):
    # list(map(lambda d: dict(zip(["sensorId", "value"], d)), zip(sensorId, value)))
    message = {
      "id": ID,
      "data": json.loads(data),
    }

    self.__client_publish(keys.PUBLISH_DATA, message)
  # end_def

  def list_devices(self):
    message = {}

    self.__client_publish(keys.LIST_DEVICES, message)
  # end_def

  def auth_device(self, ID, token):
    message = {
      "id": ID,
      "token": token,
    }

    self.__client_publish(keys.AUTH_DEVICE, message)
  # end_def

  # ========== Connector interactors ==========

  def update_data(self, ID, data):
    message = {
      "id": ID,
      "data": data,
    }

    self.__connector_publish(keys.UPDATE_DATA, message)
  # end_def

  def request_data(self, ID, sensors):
    message = {
      "id": ID,
      "data": sensors,
    }

    self.__connector_publish(keys.REQUEST_DATA, message)
  # end_def

  # ========== CLI-only methods ==========

  def send(self, exchange, routing_key, message):
    self.amqp.publish_message(exchange, routing_key, message, self.__auth_token)
  # end_def

  def listen(self, exchange, routing_key, on_message):
    self.amqp.start_messages_consumer(exchange, [routing_key], lambda _, msg: on_message(msg))
  # end_def

# end_class


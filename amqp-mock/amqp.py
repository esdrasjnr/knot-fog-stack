import json
import keys
import pika

MESSAGE_EXPIRATION_MS = "10000"

class AMQP:
  # ========== Constructor ==========
  def __init__(self, host, port):
    credentials = pika.credentials.PlainCredentials("knot", "knot")
    self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials))
    self.channel = self.connection.channel()
  # end_def

  # ========== Private methods ==========

  def __declare_exchange(self, exchange):
    self.channel.exchange_declare(exchange=exchange, durable=True, exchange_type="topic")
  # end_def

  def __bind_queue(self, queue, exchange, routing_key):
    self.channel.queue_declare(queue, durable=True)
    self.channel.queue_bind(queue, exchange, routing_key)
  # end_def

  def __bind_response_queue(self, exchange, routing_key):
    if routing_key in keys.RESPONSE_ROUTING_KEYS:
      queue = "_" + ":".join([exchange, keys.RESPONSE_ROUTING_KEYS[routing_key]])
      self.__bind_queue(queue, exchange, routing_key)
  # end_def

  # ========== Public methods ==========

  def publish_message(self, exchange, routing_key, message, auth_token):
    self.__declare_exchange(exchange)
    self.__bind_response_queue(exchange, routing_key)

    props = pika.BasicProperties(expiration=MESSAGE_EXPIRATION_MS, headers={"Authorization": auth_token})
    self.channel.basic_publish(exchange, routing_key, json.dumps(message), props)
  # end_def

  # def consume_message(self, exchange, routing_key, on_message):
  #   queue = "_" + ":".join([exchange, routing_key])
  #   self.__declare_exchange(exchange)
  #   self.__bind_queue(queue, exchange, routing_key)

  #   self.channel.basic_get(queue, lambda _method, _prop, body:  on_message(__load(body)))
  # # end_def

  def start_messages_consumer(self, exchange, routing_keys, on_message):
    queue = "_" + ":".join([exchange, *routing_keys])
    self.__declare_exchange(exchange)
    for routing_key in routing_keys:
      self.__bind_queue(queue, exchange, routing_key)

    load = lambda msg: json.loads(msg) if msg != None else dict()
    on_message_callback = lambda _ch, method, _prop, body: on_message(method.routing_key, load(body))
    self.channel.basic_consume(queue, on_message_callback)
    self.channel.start_consuming()
  # end_def

# end_class
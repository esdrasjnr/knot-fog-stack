import argparse
import json
import logging
import os
import things
import users

# ======= Load configuration file into local constants =======

with open(os.path.join(os.path.dirname(__file__), "config.json")) as fd:
  __config = json.load(fd)

DEFAULT_AMQP_HOST = __config.get("amqp-hostname")
DEFAULT_AMQP_PORT = __config.get("amqp-port")

DEFAULT_AUTH_TOKEN = __config.get("authorization-token")

DEFAULT_USERS_HOST = __config.get("users-hostname")
DEFAULT_USERS_PORT = __config.get("users-port")

# ============================================================

# ==================== Parser definitions ====================

send = ("send", "Send AMQP message")
listen = ("listen", "Listen to AMQP messages")

register_device = ("register-device", "registers a device on the cloud")
unregister_device = ("unregister-device", "unregisters a device on the cloud")
update_schema = ("update-schema", "updates device's schema on the cloud")
publish_data = ("publish-data", "publishes device's data on the cloud")
list_devices = ("list-devices", "list the devices registered on cloud")
auth_device = ("auth-device", "authenticate the device on cloud")

update_data = ("update-data", "updates a device's sensor value")
request_data = ("request-data", "request a device's sensor value")

create_user = ("create-user", "create a new user on the cloud")
create_token = ("create-token", "create a new token for a registered user")

# ============================================================

# =================== Argument definitions ===================

host = {
  "flags": ["-H", "--host", "--hostname"],
  "help": "hostname for RabbitMQ server. Default: " + DEFAULT_AMQP_HOST,
  "default": DEFAULT_AMQP_HOST,
}

port = {
  "flags": ["-p", "--port"],
  "help": "port for RabbitMQ server. Default: " + str(DEFAULT_AMQP_PORT),
  "default": DEFAULT_AMQP_PORT,
  "type": int,
}

auth_token = {
  "flags": ["-t", "--auth-token"],
  "help": "authorization token",
  "default": DEFAULT_AUTH_TOKEN,
}

users_host = {
  "flags": ["-uh", "--user-host", "--user-hostname"],
  "help": "hostname for HTTP server. Default: " + DEFAULT_USERS_HOST,
  "default": DEFAULT_USERS_HOST,
}

users_port = {
  "flags": ["-up", "--user-port"],
  "help": "port for HTTP server. Default: " + str(DEFAULT_USERS_PORT),
  "default": DEFAULT_USERS_PORT,
  "type": int,
}

exchange = {
  "flags": ["exchange"],
  "help": "exchange name",
}

routing_key = {
  "flags": ["routing_key"],
  "help": "routing key name",
}

message = {
  "flags": ["message"],
  "help": "message to be sent",
}

device_id = {
  "flags": ["device_id"],
  "help": "device's ID",
}

device_name = {
  "flags": ["device_name"],
  "help": "device's name",
}

schema = {
  "flags": ["schema"],
  "help": "schema items list",
}

data = {
  "flags": ["data"],
  "help": "data items list",
}

device_token = {
  "flags": ["device_token"],
  "help": "device's token",
}

sensors = {
  "flags": ["sensors"],
  "help": "sensors list",
}

email = {
  "flags": ["email"],
  "help": "user email",
}

password = {
  "flags": ["password"],
  "help": "user password",
}

# ============================================================

class CLI:
  # ========== Constructor ==========
  def __init__(self):
    self.parser = argparse.ArgumentParser(description="Mock messages for KNoT Fog")
    self.subparser = self.parser.add_subparsers(help="sub-command help", dest="subcommand")
    
    self.__add_arguments_to_parser(self.parser, [host, port, auth_token, users_host, users_port])
    
    self.__create_parser(send, [exchange, routing_key, message])
    self.__create_parser(listen, [exchange, routing_key])

    self.__create_parser(register_device, [device_id, device_name])
    self.__create_parser(unregister_device, [device_id])
    self.__create_parser(update_schema, [device_id, schema])
    self.__create_parser(publish_data, [device_id, data])
    self.__create_parser(list_devices, [])
    self.__create_parser(auth_device, [device_id, device_token])

    self.__create_parser(update_data, [device_id, data])
    self.__create_parser(request_data, [device_id, sensors])

    self.__create_parser(create_user, [email, password])
    self.__create_parser(create_token, [email, password])
  # end_def

  # ========== Private methods ==========

  def __add_parser(self, name, description):
    return self.subparser.add_parser(name, help=description)
  # end_def

  def __add_arguments_to_parser(self, parser, arguments):
    for options in arguments:
      parser.add_argument(*options.get("flags"), default=options.get("default"), type=options.get("type"), help=options.get("help"))
  # end_def

  def __create_parser(self, command, arguments):
    self.__add_arguments_to_parser(self.__add_parser(*command), arguments)
  # end_def

  # ========== Public methods ==========

  def run(self):
    args = self.parser.parse_args()
    t = things.Things(args.host, args.port, args.auth_token)
    u = users.Users(args.user_host, args.user_port)

    if args.subcommand == send[0]:
      t.amqp.publish_message(args.exchange, args.routing_key, args.message, args.auth_token)
    elif args.subcommand == listen[0]:
      t.amqp.start_messages_consumer(args.exchange, [args.routing_key], lambda key, msg: print(key, msg))
    elif args.subcommand == register_device[0]:
      t.register_device(args.device_id, args.device_name)
    elif args.subcommand == unregister_device[0]:
      t.unregister_device(args.device_id)
    elif args.subcommand == update_schema[0]:
      t.update_schema(args.device_id, args.schema)
    elif args.subcommand == publish_data[0]:
      t.publish_data(args.device_id, args.data)
    elif args.subcommand == list_devices[0]:
      t.list_devices()
    elif args.subcommand == auth_device[0]:
      t.auth_device(args.device_id)
    elif args.subcommand == update_data[0]:
      t.update_data(args.device_id, args.data)
    elif args.subcommand == request_data[0]:
      t.request_data(args.device_id, args.sensors)
    elif args.subcommand == create_user[0]:
      u.create_user(args.email, args.password)
    elif args.subcommand == create_token[0]:
      u.create_token(args.email, args.password)
    else:
      self.parser.print_help()
  # end_def

# end_class

cli = CLI()
cli.run()




# logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S -")

# args = parser.parse_args()
# mock = things.Things(args.host, args.port, args.auth_token)

# if args.subcommand == "listen":
#   logging.info("Listening messages at %s:%s" % (args.exchange, args.routing_key))
#   mock.listen(args.exchange, args.routing_key, lambda msg: logging.info(msg))
# elif args.subcommand == "send":
#   logging.info("Sending messages at %s:%s" % (args.exchange, args.routing_key))
#   mock.send(args.exchange, args.routing_key, args.message)
#   logging.info("Message sent: %s" % args.message)
# elif args.subcommand == "get-token":
#   get_auth_token(args.users_host, args.users_port)
# elif args.subcommand == "set-token":
#   set_auth_token(args.auth_token)
# else:
#   parser.print_help()


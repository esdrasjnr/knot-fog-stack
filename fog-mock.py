import argparse
import json
import logging
import pika
from os import path, system

MAINFLUX_EMAIL = "knot@knot.com"
MAINFLUX_PASSWORD = "123qwe123qwe"

MESSAGE_EXPIRATION_MS = "10000"
DEFAULT_AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1ODUyMTQxMzQsImlhdCI6MTU4NTE3ODEzNCwiaXNzIjoibWFpbmZsdXguYXV0aG4iLCJzdWIiOiJrbm90QGtub3QuY29tIiwidHlwZSI6MH0.UyBDri_vOEthREKRRU8OojuR5Ws60oJWiG5-LgmtgPg"


def get_auth_token(host, port):
  mainflux_url = "http://" + host + ":" + str(port)
  cmd = " ".join(["mainflux-cli users token", MAINFLUX_EMAIL, MAINFLUX_PASSWORD, "-m", mainflux_url])
  system(cmd)
# def_end

def set_auth_token(auth_token):
  cmd = "sed -i 's/^DEFAULT_AUTH_TOKEN.*/DEFAULT_AUTH_TOKEN = \"" + auth_token + "\"/' fog-mock.py"
  system(cmd)
# def_end


def create_amqp_channel(host, port, exchange):
  connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
  channel = connection.channel()
  logging.info("OK")

  channel.exchange_declare(exchange=exchange, durable=True, exchange_type="topic")
  return channel
# def_end

def config_amqp_queue(channel, exchange, routing_key):
  queue_name = exchange + "-messages"

  channel.queue_declare(queue_name, durable=True)
  channel.queue_bind(queue_name, exchange, routing_key)

  return queue_name
# def_end

def parse_json_message(msg):
  if path.exists(msg):
    with open(msg) as fd:
      parsed_msg = json.dumps(json.load(fd))
  else:
    parsed_msg = msg

  return parsed_msg
# def_end


def msg_consume(host, port, exchange, routing_key):
  channel = create_amqp_channel(host, port, exchange)
  queue = config_amqp_queue(channel, exchange, routing_key)

  on_message = lambda ch, method, prop, body: logging.info("%r" % body)
  channel.basic_consume(queue=queue, on_message_callback=on_message)

  logging.info("Listening to messages at %s: %s" % (exchange, routing_key))
  channel.start_consuming()
# def_end

def msg_publish(host, port, exchange, routing_key, message, auth_token):
  channel = create_amqp_channel(host, port, exchange)
  msg = parse_json_message(message)

  props = pika.BasicProperties(expiration=MESSAGE_EXPIRATION_MS, headers={"Authorization": auth_token})
  channel.basic_publish(exchange=exchange, properties=props, routing_key=routing_key, body=msg)
# def_end


def get_args():
  parser = argparse.ArgumentParser(description="Mock messages for KNoT Fog")
  parser.add_argument("-H", "--host", help="hostname for RabbitMQ server. Default: localhost", default="localhost")
  parser.add_argument("-p", "--port", help="port for RabbitMQ server. Default: 5672", default=5672, type=int)
  subparsers = parser.add_subparsers(help="sub-command help", dest="subcommand")

  parser_listen = subparsers.add_parser("listen", help="Listen to AMQP messages")
  parser_listen.add_argument("exchange", help="exchange for listen")
  parser_listen.add_argument("routing_key", help="routing key for listen")

  parser_send = subparsers.add_parser("send", help="Send AMQP message")
  parser_send.add_argument("exchange", help="exchange for send message")
  parser_send.add_argument("routing_key", help="routing key for send message")
  parser_send.add_argument("message", help="message to be sent")
  parser_send.add_argument("-t", "--auth-token", help="authorization token", default=DEFAULT_AUTH_TOKEN)

  parser_get_token = subparsers.add_parser("get-token", help="Get authorization token")
  parser_get_token.add_argument("--users-host", help="hostname for Users Mainflux service. Default: localhost", default="localhost")
  parser_get_token.add_argument("--users-port", help="port for Users Mainflux service. Default: 8180", default=8180)

  parser_set_token = subparsers.add_parser("set-token", help="Set default authorization token")
  parser_set_token.add_argument("auth_token", help="authorization token")

  return parser.parse_args(), parser.print_help
# def_end

def config_logging():
  logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S -")
# def_end


def main():
  config_logging()
  args, cli_help = get_args()

  if args.subcommand == "listen":
    msg_consume(args.host, args.port, args.exchange, args.routing_key)
  elif args.subcommand == "send":
    msg_publish(args.host, args.port, args.exchange, args.routing_key, args.message, args.auth_token)
  elif args.subcommand == "get-token":
    get_auth_token(args.users_host, args.users_port)
  elif args.subcommand == "set-token":
    set_auth_token(args.auth_token)
  else:
    cli_help()
# def_end


main()

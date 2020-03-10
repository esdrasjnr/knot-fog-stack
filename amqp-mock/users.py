import json
import requests

class Users:
  # ========== Constructor ==========
  def __init__(self, host, port):
    self.base_url = "http://" + host + ":" + str(port)
  # end_def

  def __post(self, path, body):
    response = requests.post(self.base_url + path, data=json.dumps(body))

    if response.status_code == 201:
      print(response.text)
    else:
      print("Status code: %d" % response.status_code)
  # end_def

  def create_user(self, email, password):
    body = {
      "email": email,
      "password": password,
    }

    self.__post("/users", body)
  # end_def

  def create_token(self, email, password):
    body = {
      "email": email,
      "password": password,
    }

    self.__post("/tokens", body)
  # end_def

# end_class
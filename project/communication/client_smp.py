from project.services.smartphone_service import insert_data
import threading
import paho.mqtt.client as mqtt
import json


class ClientSMP:
    def __init__(self):
        self.client = mqtt.Client("smp")
        self.client.connect(host="dojot.atlantico.com.br", port=1883)
        self.client.on_message = self.callback
        self.confirmation = False

    def publish_to_bm(self, data):
        data["from"] = "smp"
        data["to"] = "bm"
        self.client.publish("/gesad/9e4ed4/attrs", payload=json.dumps(data))

    def publish_to_tv(self, data):
        data["from"] = "smp"
        data["to"] = "tv"
        self.client.publish("/gesad/f0bf6d/attrs", payload=json.dumps(data))

    def subscribe(self):
        self.client.subscribe("/gesad/434339/attrs")

    def callback(self, msg):
        body = json.loads(msg.payload)
        if body["from"] == "bm":
            self.bm_message_received(body)

        elif body["from"] == "tv":
            self.tv_message_received(body)

    def bm_message_received(self, body):
        print(f'from BM {body}' )
        # insert_data(body)
        if body["type"] == "notification":
            print("Received Notification")
            self.confirmation = False
            threading.Thread(target=self.wait_for_confirmation, args=(body,)).start()
            return "ok"

        if body["type"] == "status":
            return "ok"

    def tv_message_received(self, body):
        print(f'from TV {body}')
        if "unlocked" in body["msg"]:
            self.confirmation = True
            data = {
                "type": "confirmation",
                "msg": "The notification is confirmed",
                "from": "smp",
                "to": "bm",
            }
            self.publish_to_bm(data)
            return "Confirmation Sent"

    def wait_for_confirmation(self, data):
        time = 0
        while not client_smp.confirmation:
            print(f"I'm waiting for {time} seconds.")
            if time >= 7:
                client_smp.publish_to_tv(data)
                break
            sleep(1)
            time += 1

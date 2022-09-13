import json
import time

from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer

all_rooms = []


class AllRoomsConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        self.group_name = "group_" + str(time.time())
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        print(self.channel_layer)
        await self.send({
            "type": "websocket.accept"
        })
        obj = json.dumps({
            'rooms': all_rooms
        })

        await self.send({
            'type': 'websocket.send',
            'text': obj,
        })

    async def websocket_receive(self, event):
        if event['text'] == 'alive':
            obj = json.dumps({
                'rooms': all_rooms
            })

            await self.send({
                'type': 'websocket.send',
                'text': obj,
            })
        print("receive", event)

    async def websocket_disconnect(self, event):
        all_rooms.remove(self.group_name)
        raise StopConsumer()


class ChatRoomConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_name = None
        self.room_name = None
        self.rooms = None

    async def connect(self):
        youser = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.group_name = "group_" + self.room_name
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        all_rooms.append(self.room_name)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': 'Chat Connected!!',
                'username': youser.username
            }
        )

    async def test_message(self, event):
        tester = event['tester']

        await self.send(text_data=json.dumps({
            'tester': tester,
        }))

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    async def disconnect(self, code):
        all_rooms.remove(self.room_name)
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        raise StopConsumer()

    async def receive(self, text_data):
        message_json = json.loads(text_data)
        message = message_json['message']
        username = message_json['username']
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    pass

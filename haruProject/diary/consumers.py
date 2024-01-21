from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from diary.models import HaruRoom, Diary
from django.contrib.sessions.models import Session


class HaruConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        # 인스턴스 변수는 생성자 내에서 정의.
        # 인스턴스 변수 group_name 추가
        self.room_name = None
        self.user = None
        self.room = None

        # session_key = self.scope['cookies'].get('sessionid')
        # if session_key:
        #     user_id = database_sync_to_async(Session.objects.get)(session_key=session_key)
        #     if user_id:
        #         self.user = user_id.get_decoded().get('_auth_user_id')
        #     else:
        #         self.close()
        #     session = database_sync_to_async(Session.objects.get)(session_key=session_key)
        #     if

    # ChatConsumer는 동기식 장고 모델에는 접근하지 않고, 비동기식 채널, 채널 레이어에만 접근한다.
    async def connect(self):
        # self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['diary_id']
        # session_key = self.scope['cookies'].get('sessionid')
        # if session_key:
        #     session = await database_sync_to_async(Session.objects.get)(session_key=session_key)
        #     member_id = session.get_decoded().get('member_id', None)
        #     if member_id:
        #         self.user = member_id
        #     if member_id is None:
        #         self.user = "AnonymousUser"
        #     else:
        #         return
        if not self.room_name or len(self.room_name) > 100:
            await self.close(code=400)
            return
        self.room = await self.get_or_create_room()
        # join room group
        await self.channel_layer.group_add(self.room_name, self.channel_name)

        print("WebSocket connected:", self.channel_name)
        print("User:", self.scope['user'])

        await self.accept()

        # await self.send_user_list()
        # 각 애플리케이션 인스턴스는 단일 소비자 인스턴스를 생성, -> self.channel_name
        # 채널 레이어를 활성화한 경우 소비자는 고유한 채널 이름을 생성하고 이벤트를 수신 대기하기 시작

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        await self.remove_online_user()
        # await self.send_user_list()

    async def websocket_receive(self, message):
        # = self.scope['user']
        _type = message['type']  # chat.message, chat.url,
        if _type == "image.dragdrop":
            x = message['x']
            y = message['y']
            width = message['width']
            height = message['height']
            rotate = message['rotate']
            image_id = message['image_id']
        data = json.loads(message['text'])
        _type = data['type']

        if _type == "text_input":
            x = data['x']
            y = data['y']
            width = data['width']
            height = data['height']
            rotate = data['rotate']
            text = data['text']
            writer = data['writer']
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'image_dragdrop',
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height,
                    'rotate': rotate,
                    'image_id': image_id
                    'text': text,
                    'writer': writer,
                }
            )
        elif _type == "text.input":
            x = message['x']
            y = message['y']
            width = message['width']
            height = message['height']
            rotate = message['rotate']
            text = message['text']
        elif _type == "image_dragdrop":
            x = data['x']
            y = data['y']
            width = data['width']
            height = data['height']
            rotate = data['rotate']
            image_url = data['image_url']
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'image_dragdrop',
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height,
                    'rotate': rotate,
                    'text': text
                    'image_url': image_url,
                }
            )

    async def image_dragdrop(self, event):
        # Send the image dragdrop event to the WebSocket
        await self.send(text_data=json.dumps(event))

    async def text_input(self, event):
        # Send the text input event to the WebSocket
        await self.send(text_data=json.dumps(event))

    # Receive message from WebSocket

    # Receive message from room group
    # async def chat_message(self, event):
    #     message = event['message']
    #     # Send message to WebSocket
    #     await self.send(text_data=json.dumps({'message': message}))
    # await self.close()
    @database_sync_to_async
    def get_or_create_room(self):
        diary_instance = Diary.objects.get(diary_id=self.room_name)
        room, _ = HaruRoom.objects.get_or_create(diary_id=self.room_name)
        haruroom_instance = HaruRoom.objects.get(diary_id=self.room_name)
        print(diary_instance)
        print(haruroom_instance)
        return room

    @database_sync_to_async
    def create_online_user(self):
        try:
            self.room.user_count += 1
            self.room.save()
        except Exception as e:
            print(str(e))
            self.close()
            return None

    @database_sync_to_async
    def get_user_count(self):
        user_count = self.room.user_count
        print(user_count)

    @database_sync_to_async
    def remove_online_user(self):
        try:
            self.room.user_count -= 1
            self.room.save()
        except Exception as e:
            print(str(e))
            self.close()
            return None

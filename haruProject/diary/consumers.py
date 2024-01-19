from channels.generic.websocket import AsyncWebsocketConsumer
import json
from diary.models import HaruRoom


class HaruConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        # 인스턴스 변수는 생성자 내에서 정의.
        # 인스턴스 변수 group_name 추가
        self.room_name = None

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



        #join room group
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        # 각 애플리케이션 인스턴스는 단일 소비자 인스턴스를 생성, -> self.channel_name
        # 채널 레이어를 활성화한 경우 소비자는 고유한 채널 이름을 생성하고 이벤트를 수신 대기하기 시작

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def websocket_receive(self, message):
        # = self.scope['user']
        _type = message['type'] #chat.message, chat.url,
        if _type == "image.dragdrop":
            x = message['x']
            y = message['y']
            width = message['width']
            height = message['height']
            rotate = message['rotate']
            image_id = message['image_id']
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
                }
            )
        elif _type == "text.input":
            x = message['x']
            y = message['y']
            width = message['width']
            height = message['height']
            rotate = message['rotate']
            text = message['text']
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'text_input',
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height,
                    'rotate': rotate,
                    'text': text
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

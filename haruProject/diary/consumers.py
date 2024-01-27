import logging
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from diary.models import HaruRoom, Diary, DiarySticker, DiaryTextBox
from diary.serializers import (HaruRoomDetailSerializer,
                               DiaryTextBoxModifySerializer, DiaryStickerModifySerializer)
from rest_framework.generics import get_object_or_404

# from django.contrib.sessions.models import Session
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
        await self.create_online_user()
        # if self.room.user_count > 5:
        #     await self.close()
        await self.accept()
        await self.send_user_count()
        await self.send_db_info()
        logger.debug("accepted")
        logger.debug(self.send_db_info())
        # await self.send_user_list()
        # 각 애플리케이션 인스턴스는 단일 소비자 인스턴스를 생성, -> self.channel_name
        # 채널 레이어를 활성화한 경우 소비자는 고유한 채널 이름을 생성하고 이벤트를 수신 대기하기 시작

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        await self.remove_online_user()
        await self.send_user_count()
        # await self.send_user_list()

    async def websocket_receive(self, message):
        # = self.scope['user']
        data = json.loads(message['text'])
        _type = data['type']

        if _type == "text_input":
            text_id = data['id']
            content = data['content']
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'text_input',
                    'text_id': text_id,
                    'content': content,
                }
            )
            logger.debug(f"groupSend(text_input: {text_id}, content type: {type(content)}, content: {content})")
            print('print: ' + content)

        elif _type == "nickname_input":
            text_id = data['id']
            writer = data['nickname']
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'nickname_input',
                    'text_id': text_id,
                    'nickname': writer,
                }
            )
            logger.debug(f"groupSend(nickname_input: text_id: {text_id}, nickname: {writer})")

        elif _type == "text_drag":
            text_id = data['id']
            text_drag_data = data['position']
            x = text_drag_data['x']
            y = text_drag_data['y']
            # width = text_drag_data['width']
            # height = text_drag_data['height']
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'text_drag',
                    'text_id': text_id,
                    'position': {
                        'x': x,
                        'y': y,
                        # 'width': width,
                        # 'height': height,
                    },
                }
            )
            logger.debug(f"groupSend(text_drag): text_id: {text_id}, x: {x}, y: {y}")

        elif _type == "text_resize":
            text_id = data['id']
            text_resize_data = data['position']
            width = text_resize_data['width']
            height = text_resize_data['height']
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'text_resize',
                    'text_id': text_id,
                    'position': {
                        'width': width,
                        'height': height,
                    },
                }
            )
            logger.debug(f"groupSend(text_resize): text_id: {text_id}, width: {width}, height: {height}")

        elif _type == "save_text":
            text_id = data['id']
            content = data['content']
            writer = data['nickname']
            text_data = data['position']
            x = text_data['x']
            y = text_data['y']
            width = text_data['width']
            height = text_data['height']
            await self.save_textbox(text_id, content, writer, text_data)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'save_text',
                    'text_id': text_id,
                    'content': content,
                    'nickname': writer,
                    'position': {
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height,
                    },
                }
            )
            logger.debug(
                f"groupSend(save_text): text_id: {text_id}, content: {content}, nickname: {writer}, "
                f"position: {text_data}")

        elif _type == "create_textbox":
            # object_type = data['object_type']
            text_data = data['position']
            width = text_data['width']
            height = text_data['height']
            x = text_data['x']
            y = text_data['y']
            # writer = data['nickname']
            textbox_id = data.get('id', None)
            if textbox_id is None:
                textbox_id = await self.create_textbox(x, y, width, height)  # writer
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'create_textbox',
                    # 'object_type': object_type,
                    # 'text': text,
                    'text_id': textbox_id,
                    'position': {
                        'width': width,
                        'height': height,
                        'x': x,
                        'y': y,
                    },
                }
            )
            logger.debug(f"After group_send:, text_id: {textbox_id}, {width}, {height}, {x}, {y}")

        elif _type == "image_drag":
            drag_data = data['drag']
            width = drag_data['width2']
            height = drag_data['height2']
            top = drag_data['top2']
            left = drag_data['left2']
            rotate = drag_data['rotate2']
            image_url = drag_data['image_url']
            image_box_id = data.get('image_box_id', None)
            if image_box_id is None:
                image_box_id = await self.save_image(width, height, top, left, rotate, image_url)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'image_drag',
                    'drag': {
                        'width2': width,
                        'height2': height,
                        'top2': top,
                        'left2': left,
                        'rotate2': rotate,
                        'image_url': image_url,
                        'image_box_id': image_box_id
                    },            # 'image_box_id': image_box_id
                }
            )
        elif _type == "image_resize":
            resize_data = data['resize']
            width = resize_data['width2']
            height = resize_data['height2']
            top = resize_data['top2']
            left = resize_data['left2']
            rotate = resize_data['rotate2']
            image_url = resize_data['image_url']
            image_box_id = data.get('image_box_id', None)
            if image_box_id is None:
                image_box_id = await self.save_image(width, height, top, left, rotate, image_url)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'image_resize',
                    'resize': {
                        'width2': width,
                        'height2': height,
                        'top2': top,
                        'left2': left,
                        'rotate2': rotate,
                        'image_url': image_url,
                        'image_box_id': image_box_id
                    },
                }
            )
        elif _type == "image_rotate":
            rotate_data = data['rotate']
            width = rotate_data['width2']
            height = rotate_data['height2']
            top = rotate_data['top2']
            left = rotate_data['left2']
            rotate = rotate_data['rotate2']
            image_url = rotate_data['image_url']
            image_box_id = data.get('image_box_id', None)
            if image_box_id is None:
                image_box_id = await self.save_image(width, height, top, left, rotate, image_url)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'image_rotate',
                    'rotate': {
                        'width2': width,
                        'height2': height,
                        'top2': top,
                        'left2': left,
                        'rotate2': rotate,
                        'image_box_id': image_box_id
                    },
                }
            )
        elif _type == "create_sticker":
            image_data = data['image']
            width = image_data['width']
            height = image_data['height']
            top = image_data['top']
            left = image_data['left']
            rotate = image_data['rotate']
            image_url = image_data['image_url']
            image_box_id = data.get('sticker_id', None)
            if image_box_id is None:
                image_box_id = await self.save_image(width, height, top, left, rotate, image_url)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'create_sticker',
                    'image': {
                        'width': width,
                        'height': height,
                        'top': top,
                        'left': left,
                        'rotate': rotate,
                        'image_url': image_url,
                        'image_box_id': image_box_id
                    },
                }
            )
        elif _type == "delete_object":
            object_type = data['object_type']
            object_id = data['object_id']
            deleted = await self.delete_box(object_id, object_type)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'delete_object',
                    'object_type': object_type,
                    'object_id': object_id,
                    'message': deleted
                }
            )

    async def send_user_count(self):
        user_count = self.room.user_count
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'user_count',
                'user_count': user_count
            }
        )

    async def send_db_info(self):
        diary_info = await self.get_diary()
        await self.send(text_data=json.dumps({
            'type': 'send_db_info',
            'diary_info': diary_info
        }))

    async def text_input(self, event):
        logger.debug("sendTextInput")
        await self.send(text_data=json.dumps(event))

    async def nickname_input(self, event):
        logger.debug("sendNicknameInput")
        await self.send(text_data=json.dumps(event))

    async def text_drag(self, event):
        logger.debug("sendTextDrag")
        await self.send(text_data=json.dumps(event))

    async def text_resize(self, event):
        logger.debug("sendTextResize")
        await self.send(text_data=json.dumps(event))

    async def image_drag(self, event):  # save
        logger.debug("sendDragged")
        await self.send(text_data=json.dumps(event))

    async def image_rotate(self, event):  # save
        logger.debug("sendRotated")
        await self.send(text_data=json.dumps(event))

    async def image_resize(self, event):  # save
        logger.debug("sendResized")
        await self.send(text_data=json.dumps(event))

    async def create_sticker(self, event):
        logger.debug("sendStickerCreated")
        await self.send(text_data=json.dumps(event))

    async def create_textbox(self, event):
        logger.debug("sendTextBoxCreated")
        await self.send(text_data=json.dumps(event))

    async def send_static_image(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_count(self, event):
        await self.send(text_data=json.dumps(event))

    async def delete_object(self, event):
        object_type = event['object_type']
        object_id = event['object_id']
        await self.send(text_data=json.dumps({
            'type': 'delete_object',
            'object_type': object_type,
            'object_id': object_id,
        }))

    # Receive message from WebSocket
    # Receive message from room group
    # async def chat_message(self, event):
    #     message = event['message']
    #     # Send message to WebSocket
    #     await self.send(text_data=json.dumps({'message': message}))
    # await self.close()

    def get_user_count(self):
        return self.room.user_count

    @database_sync_to_async
    def get_diary(self):
        diary = Diary.objects.get(diary_id=self.room_name)
        diary_serializer = HaruRoomDetailSerializer(diary).data
        return diary_serializer

    @database_sync_to_async
    def get_or_create_room(self):
        room, _ = HaruRoom.objects.get_or_create(diary_id=self.room_name)
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

    # @database_sync_to_async
    @database_sync_to_async
    def remove_online_user(self):
        try:
            self.room.user_count -= 1
            self.room.save()
        except Exception as e:
            print(str(e))
            self.close()
            return None

    @database_sync_to_async
    def save_image(self, width, height, top, left, rotate, image_url):
        image_url = 'uurrrlll'
        image_box, _ = (DiarySticker.objects.get_or_create
                        (diary_id=self.room_name, sticker_image_url=image_url, xcoor=top, ycoor=left, width=width,
                         height=height, rotate=rotate))
        return image_box.sticker_id

    @database_sync_to_async
    def save_textbox(self, x, y, width, height, rotate, text, writer):
        textbox, _ = (DiaryTextBox.objects.get_or_create
                      (diary_id=self.room_name, xcoor=x, ycoor=y, width=width, height=height))
        logger.debug(f"create_textbox: {textbox}")

        return textbox.textbox_id

    @database_sync_to_async
    def save_textbox(self, text_id, content, writer, text_data):
        text_box = get_object_or_404(DiaryTextBox, textbox_id=text_id)
        DiaryTextBoxModifySerializer(text_box, text_data={
            'content': content,
            'writer': writer,
            'x': text_data.x,
            'y': text_data.y,
            'width': text_data.width,
            'height': text_data.height,
        }).is_valid(raise_exception=True)
        logger.debug(f"update_textbox: {text_box.textbox_id}")

    @database_sync_to_async
    def delete_box(self, box_id, box_type):
        if box_type == 'image':
            DiarySticker.objects.filter(sticker_id=box_id).delete()
        if box_type == 'textbox':
            DiaryTextBox.objects.filter(textbox_id=box_id).delete()
        return f'{box_type} {box_id} deleted'

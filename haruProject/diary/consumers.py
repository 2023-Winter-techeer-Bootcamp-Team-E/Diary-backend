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
            sticker_data = data['position']
            top = sticker_data['top2']
            left = sticker_data['left2']
            # image_url = data['image']
            sticker_id = data.get('id', None)
            # if image_box_id is None:
            #     image_box_id = await self.save_image(width, height, top, left, rotate, image_url)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'image_drag',
                    'sticker_id': sticker_id,
                    'position': {
                        'top2': top,
                        'left2': left,
                        'rotate2': rotate,
                        'image_url': image_url,
                        'image_box_id': image_box_id
                    },            # 'image_box_id': image_box_id
                }
            )
            logger.debug(f"groupSend(image_drag):, sticker_id: {sticker_id} top: {top}, left: {left}")

        elif _type == "image_resize":
            sticker_data = data['position']
            width = sticker_data['width2']
            height = sticker_data['height2']
            top = sticker_data['top2']
            left = sticker_data['left2']
            sticker_id = data.get('id', None)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'image_resize',
                    'sticker_id': sticker_id,
                    'position': {
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
            logger.debug(
                f"After resize_group_send:, sticker_id: {sticker_id}, w: {width},h: {height},t: {top}, l: {left}")

        elif _type == "image_rotate":
            sticker_data = data['position']
            rotate = sticker_data['rotate2']
            sticker_id = data.get('id', None)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'image_rotate',
                    'sticker_id': sticker_id,
                    'position': {
                        'rotate2': rotate,
                    },
                }
            )
            logger.debug(f"After group_send:{rotate}, {sticker_id}")

        elif _type == "save_image":
            sticker_id = data['id']
            sticker_url = data['image']
            sticker_data = data['position']
            width = sticker_data['width2']
            height = sticker_data['height2']
            top = sticker_data['top2']
            left = sticker_data['left2']
            rotate = sticker_data['rotate2']
            await self.save_sticker(sticker_id, sticker_url, sticker_data)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'save_image',
                    'sticker_id': sticker_id,
                    'sticker_url': sticker_url,
                    'position': {
                        'width2': width,
                        'height2': height,
                        'top2': top,
                        'left2': left,
                        'rotate2': rotate,
                    },
                }
            )

        elif _type == "create_sticker":
            sticker_url = data['image']
            sticker_data = data['position']
            width = sticker_data['width2']
            height = sticker_data['height2']
            top = sticker_data['top2']
            left = sticker_data['left2']
            rotate = sticker_data['rotate2']
            sticker_id = data.get('sticker_id', None)
            if sticker_id is None:
                sticker_id = await self.create_sticker(width, height, top, left, rotate, sticker_url)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'create_sticker',
                    'image': sticker_url,
                    'sticker_id': sticker_id,
                    'position': {
                        'width2': width,
                        'height2': height,
                        'top2': top,
                        'left2': left,
                        'rotate2': rotate,
                    },
                }
            )
            logger.debug(f"After group_send:, {sticker_url}, {sticker_id}, {width}, {height}, {top}, {left}, {rotate}")

        elif _type == "dalle_drag":
            sticker_id = data['id']
            sticker_data = data['position']
            top = sticker_data['top2']
            left = sticker_data['left2']
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'dalle_drag',
                    'sticker_id': sticker_id,
                    'position': {
                        'top2': top,
                        'left2': left,
                    },
                }
            )
            logger.debug(f"groupSend(dragged):, sticker_id: {sticker_id}, top: {top}, left: {left}")

        elif _type == "dalle_resize":
            sticker_id = data['id']
            sticker_data = data['position']
            width = sticker_data['width2']
            height = sticker_data['height2']
            top = sticker_data['top2']
            left = sticker_data['left2']
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'dalle_resize',
                    'sticker_id': sticker_id,
                    'position': {
                        'width2': width,
                        'height2': height,
                        'top2': top,
                        'left2': left,
                    },
                }
            )
            logger.debug(f"groupSend(resized):, sticker_id: {sticker_id}, width: {width}, height: {height}, "
                         f"top: {top}, left: {left}")

        elif _type == "dalle_rotate":
            sticker_id = data['id']
            sticker_data = data['position']
            rotate = sticker_data['rotate2']
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'dalle_rotate',
                    'sticker_id': sticker_id,
                    'position': {
                        'rotate2': rotate,
                    },
                }
            )

        elif _type == "save_dalle":
            sticker_id = data['id']
            sticker_url = data['image']
            sticker_data = data['position']
            width = sticker_data['width2']
            height = sticker_data['height2']
            top = sticker_data['top2']
            left = sticker_data['left2']
            rotate = sticker_data['rotate2']
            await self.save_sticker(sticker_id, sticker_url, sticker_data)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'save_dalle',
                    'sticker_id': sticker_id,
                    'sticker_url': sticker_url,
                    'position': {
                        'width2': width,
                        'height2': height,
                        'top2': top,
                        'left2': left,
                        'rotate2': rotate,
                    },
                }
            )
        elif _type == "create_dalle":
            sticker_url = data['image']
            sticker_data = data['position']
            width = sticker_data['width2']
            height = sticker_data['height2']
            top = sticker_data['top2']
            left = sticker_data['left2']
            rotate = sticker_data['rotate2']
            sticker_id = data.get('sticker_id', None)
            if sticker_id is None:
                sticker_id = await self.create_sticker(width, height, top, left, rotate, sticker_url)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'create_dalle',
                    'image': sticker_url,
                    'sticker_id': sticker_id,
                    'position': {
                        'width2': width,
                        'height2': height,
                        'top2': top,
                        'left2': left,
                        'rotate2': rotate,
                    },
                }
            )

        elif _type == "delete_object":
            object_type = data['object_type']
            object_id = data['object_id']
            await self.delete_box(object_id, object_type)
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

    async def save_text(self, event):
        logger.debug("sendTextSaved")
        await self.send(text_data=json.dumps(event))

    async def save_image(self, event):
        logger.debug("sendImageSaved")
        await self.send(text_data=json.dumps(event))

    async def create_dalle(self, event):
        logger.debug("sendDalleCreated")
        await self.send(text_data=json.dumps(event))

    async def dalle_drag(self, event):
        logger.debug("sendDalleDragged")
        await self.send(text_data=json.dumps(event))

    async def dalle_resize(self, event):
        logger.debug("sendDalleResized")
        await self.send(text_data=json.dumps(event))

    async def dalle_rotate(self, event):
        logger.debug("sendDalleRotated")
        await self.send(text_data=json.dumps(event))

    async def save_dalle(self, event):
        logger.debug("sendDalleSaved")
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
    def create_sticker(self, width, height, top, left, rotate, sticker_url):
        sticker, _ = (DiarySticker.objects.get_or_create
                      (diary_id=self.room_name, sticker_image_url=sticker_url, top=top, left=left, width=width,
                       height=height, rotate=rotate))
        logger.debug(f"create_sticker: {sticker}")
        return sticker.sticker_id

    @database_sync_to_async
    def save_sticker(self, sticker_id, sticker_url, sticker_data):
        sticker = get_object_or_404(DiarySticker, sticker_id=sticker_id)
        DiaryStickerModifySerializer(sticker, data={
            'sticker_image_url': sticker_url,
            'top': sticker_data.top2,
            'left': sticker_data.left2,
            'width': sticker_data.width2,
            'height': sticker_data.height2,
            'rotate': sticker_data.rotate2,
        }).is_valid(raise_exception=True)
        logger.debug(f"save_sticker: {sticker.sticker_id}")

    @database_sync_to_async
    def create_textbox(self, x, y, width, height):
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
        if box_type == 'sticker':
            DiarySticker.objects.filter(sticker_id=box_id).delete()
        if box_type == 'textbox':
            DiaryTextBox.objects.filter(textbox_id=box_id).delete()

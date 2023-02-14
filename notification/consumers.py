import json
from channels.generic.websocket import WebsocketConsumer
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from accounts.models import Account
from .models import NotificationModel
import asyncio


class NotifiacationConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        # check if user is available in database
        self.userId = self.scope["url_route"]["kwargs"]["userId"]
        is_user_valid = await self.validate_user()
        if not is_user_valid:
            await self.send({"type": "websocket.disconnect"})
        # add to general notifications group
        self.general_notifications_group = "notifications"
        await self.channel_layer.group_add(
            self.general_notifications_group, self.channel_name
        )
        # add the user to his own notification
        self.user_notification_group = "notifications" + "_" + self.userId
        await self.channel_layer.group_add(
            self.user_notification_group, self.channel_name
        )
        notifications = await self.get_user_notifications()
        await self.send({"type": "websocket.send", "text": json.dumps(notifications)})

    async def websocket_disconnect(self, event):
        self.channel_layer.group_discard(
            self.user_notification_group, self.channel_name
        )
        self.channel_layer.group_discard(
            self.general_notifications_group, self.channel_name
        )
        self.send({"type": "websocket.disconnect"})

    async def websocket_receive(self, event):
        print(event)
        await self.send({"type": "websocket.send", "text": event["text"]})

    async def send_notification(self, event):
        text = event["text"]
        # send message to websocket
        await self.send({"type": "websocket.send", "text": text})

    @database_sync_to_async
    def validate_user(self):
        # if the user exists in the database return true
        # else return false
        if Account.objects.filter(pk=self.userId).exists():
            return True
        else:
            return False

    @database_sync_to_async
    def get_user_notifications(self):
        user_saved_notifications = NotificationModel.objects.filter(pk=self.userId)
        user_notificaions = []
        for ntn in user_saved_notifications:
            ntn_dict = {}
            ntn_dict["message"] = ntn.message
            user_notificaions.append(ntn_dict)
        return user_notificaions

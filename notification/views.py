# Test sending data to group from channel layer group sendfrom django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import NotificationModel
from accounts.models import Account
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

# Create your views here.

# get the channel layer
channel_layer = get_channel_layer()
# view to get payment request from user
class SendNotificationView(APIView):
    def post(self, request):
        if "userId" not in request.data:
            return Response(
                data={"message": "missing field userId"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif "otherUserId" not in request.data:
            return Response(
                data={"message": "missing field otherUserId"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif "message" not in request.data:
            return Response(
                data={"message": "missing field message"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.userId = request.data["userId"]
        self.otherUserId = request.data["otherUserId"]
        message = request.data["message"]
        if Account.objects.filter(pk=self.userId).exists():
            user = Account.objects.filter(pk=self.userId).get()
            notification = NotificationModel(user=user, message=message)
            notification.save()
            text = {"message": message}
            self.send_notification(text, self.otherUserId)
            print(user)
            return Response(
                data={"status": True, "message": "Notification sent successfully"},
                status=status.HTTP_200_OK,
            )
        elif not Account.objects.filter(pk=self.otherUserId).exists():

            return Response(
                data={"status": False, "message": "User does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            t = type(self.userId)
            l = len(User.objects.all())
            return Response(
                data={"status": False, "message": f"Invalid User {l}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def send_notification(self, text, otherUserId):
        notification_data = {"text": json.dumps(text)}
        # send the notification to the specific user
        group_name = "notifications" + "_" + str(otherUserId)
        async_to_sync(channel_layer.group_send)(
            group_name, {"type": "send_notification", "text": notification_data}
        )

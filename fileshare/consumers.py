import json
from channels.generic.websocket import WebsocketConsumer
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from .models import FileReceive, FileSend
from accounts.models import Account
from .models import FileSend
import ast
import asyncio


class FileSendSocket(AsyncConsumer):
    async def websocket_connect(self, event):
        # get all the keyword arguments
        self.userId = self.scope["url_route"]["kwargs"]["userId"]
        self.fileId = self.scope["url_route"]["kwargs"]["fileId"]
        self.pointer = self.scope["url_route"]["kwargs"]["pointer"]
        is_user_valid = self.validate_user(self.userId)
        # initiate the download from a http request,
        # create a filesend with pointer 0 and also create
        # an empty file with userId_fileId
        # containing a list string
        # then pass the socket link and continue from there
        if is_user_valid:
            if self.validate_file(self.fileId):
                # this means download has just been initiated by the client
                filepath = f"filesend/{self.userId}_{self.fileId}.txt"
                with open(filepath, "r") as fs:
                    chunks_string = fs.read()
                    chunks = json.loads(chunks_string)
                    start_index = int(self.pointer)
                    while (start_index + 1) < len(chunks):
                        next_chunk = chunks[start_index]
                        data = {"data": next_chunk}
                        # send the next chunk of data
                        await self.send(
                            {
                                "type": "websocket.send",
                                "text": json.dumps(data),
                            }
                        )
                        # increment the start_index
                        start_index += 1
                        # if start_index == len(chunks):
                        #     pass
                    # next_chunk = chunks[]
            else:
                await self.send({"type": "websocket.disconnect"})

        else:
            await self.send({"type": "websocket.disconnect"})

    async def websocket_receive(self, event):
        pass

    async def websocket_disconnect(self, event):
        self.send({"type": "websocket.disconnect"})

    @database_sync_to_async
    def validate_user(self, id):
        # if the user exists in the database return true
        # else return false
        if Account.objects.filter(pk=id).exists():
            return True
        else:
            return False

    @database_sync_to_async
    def validate_file(self, id):
        # if the file exists in the database return true
        # else return false
        if FileSend.objects.filter(pk=id).exists():
            return True
        else:
            return False

    @database_sync_to_async
    def collect_data(self):
        # This function is responsible for collecting and organizing questions
        # in the requested form
        pass


class FileReceiveSocket(AsyncConsumer):
    async def websocket_connect(self, event):
        # get all the keyword arguments
        self.userId = self.scope["url_route"]["kwargs"]["userId"]
        self.fileId = self.scope["url_route"]["kwargs"]["fileId"]
        self.pointer = self.scope["url_route"]["kwargs"]["pointer"]
        is_user_valid = self.validate_user(self.userId)
        if is_user_valid:
            pass
        else:
            await self.send({"type": "websocket.disconnect"})

    async def websocket_receive(self, event):
        # nitiate the file receieve from a http put request
        # create a filesend with pointer 0 and also create
        # an empty file with userId_fileId
        # containing a list string
        # then pass the socket link and continue from there
        filepath = f"filereceive/{self.userId}_{self.fileId}.txt"
        # open the file in append mode
        with open(filepath, "a") as fr:
            data = json.loads(event["text"])
            chunk = data["data"]
            fr.write(f"{chunk}\n")

    async def websocket_disconnect(self, event):
        self.send({"type": "websocket.disconnect"})

    @database_sync_to_async
    def validate_user(self, id):
        # if the user exists in the database return true
        # else return false
        if Account.objects.filter(pk=id).exists():
            return True
        else:
            return False

    @database_sync_to_async
    def increment_pointer(self, fileId):
        pass

    @database_sync_to_async
    def unpack_data(self, filepath):
        # This function is responsible for doing the following
        # reading the bytes line by line from the filepath
        # converting the bytes string into json
        # saving the questions and answers one after the other into the database
        pass

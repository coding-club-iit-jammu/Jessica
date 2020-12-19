import discord
class log_emit:
    def __init__(self, bot, DEBUG):
        self.bot = bot
        self.DEBUG = DEBUG 

    async def print(self, log, log_channel):
        if(self.DEBUG):
            return print(log)
        return await log_channel.send(log)
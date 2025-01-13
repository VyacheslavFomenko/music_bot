import discord
import os
import yt_dlp
from dotenv import load_dotenv
import asyncio

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.all()
    intents.message_content = True
    client = discord.Client(intents=intents)
    voice_clients = {}
    yt_dl_options = {"format": "bestaudio"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)
    ffmpeg_options = {"options": "-vn"}

    @client.event
    async def on_ready():
        print(f'{client.user} logged in and ready!')

    @client.event
    async def on_message(message):
        if message.author.bot:
            return

        if message.content.startswith("/play"):
            try:
                if message.guild.id in voice_clients and voice_clients[message.guild.id].is_connected():
                    voice_client = voice_clients[message.guild.id]
                else:
                    voice_client = await message.author.voice.channel.connect()
                    voice_clients[message.guild.id] = voice_client

                url = message.content.split()[1]
                data = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                song = data['url']
                player = discord.FFmpegPCMAudio(song, **ffmpeg_options)
                voice_clients[message.guild.id].play(player)

            except Exception as e:
                print(f"Error in /play: {e}")

        elif message.content.startswith("/pause"):
            try:
                voice_clients[message.guild.id].pause()
            except Exception as e:
                print(f"Error in /pause: {e}")

        elif message.content.startswith("/resume"):
            try:
                voice_clients[message.guild.id].resume()
            except Exception as e:
                print(f"Error in /resume: {e}")

        elif message.content.startswith("/stop"):
            try:
                voice_clients[message.guild.id].stop()
                await voice_clients[message.guild.id].disconnect()
                del voice_clients[message.guild.id]
            except Exception as e:
                print(f"Error in /stop: {e}")

    client.run(TOKEN)
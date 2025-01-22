from asyncio import queues

import discord
import os
import yt_dlp
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

load_dotenv()


class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    @commands.command(name="join")
    async def join(self, ctx):
        try:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                if ctx.guild.voice_client is None:
                    await channel.connect()
                    await ctx.send(f"{channel.name} joined")
                else:
                    await ctx.send("I'm already connected to a voice channel!")
            else:
                await ctx.send("You must be in a voice channel to use this command.")

        except Exception as e:
            await ctx.send(e)

    def get_audio_url(url):
        pass

    @commands.command(name="play")
    async def play(self, ctx, url: str):
        if ctx.author.voice is None:
            await ctx.send("You should be in channel to use bot")
            return

        vc = ctx.guild.voice_client

        if vc is None:
            await ctx.invoke(self.bot.get_command("join"))
            vc = ctx.guild.voice_client


        guild_id = ctx.guild.id
        if guild_id not in self.queues:
            self.queues[guild_id] = []

        yt_dl_options = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }],
        }
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        try:
            with yt_dlp.YoutubeDL(yt_dl_options) as ytdl:
                data = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                print(data)
                song = data["url"]
                title = data["title"]
                await ctx.send(f"Now playing: **{title}**")
        except Exception as e:
            await ctx.send(e)
            return

        player = discord.FFmpegPCMAudio(song, **ffmpeg_options)
        vc.play(player)

    @commands.command(name="pause")
    async def pause(self, ctx):
        vc = ctx.guild.voice_client
        try:
            if vc.is_playing():
                vc.pause()
        except Exception as e:
            print(f"Error in pause: {e}")

    @commands.command(name="resume")
    async def resume(self, ctx):
        vc = ctx.guild.voice_client
        try:
            if vc:
                vc.resume()
        except Exception as e:
            print(f"Error in pause: {e}")

    @commands.command(name="stop")
    async def resume(self, ctx):
        vc = ctx.guild.voice_client
        try:
            if vc:
                vc.disconnect()
        except Exception as e:
            print(f"Error in pause: {e}")

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user} logged in and ready!')
    await bot.add_cog(MusicBot(bot))


TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)

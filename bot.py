import discord
from discord.ext.commands import bot
from discord.ext.tasks import loop
from discord.ext import commands
from dotenv import load_dotenv
from dl_func import *
import asyncio

# Create dictionaries to store server queues and current song information and server ids
ids = []
server_queues = {}
current_song = {}

# Taken from tutorial 
# Load the token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Taken from tutorial 

# Load the token from the .env file
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Defines the song class
class song:
    def  __init__(self,dl_info,voice_id,guild_id,voice_client,voice_channel,current_song = None):
        self.file_name = dl_info.file_name
        self.duration = dl_info.duration
        self.voice_id = voice_id
        self.guild_id = guild_id
        self.path = guild_id + '_songs/' + dl_info.file_name
        self.voice_state = voice_client
        self.voice_channel = voice_channel
        self.title = dl_info.title
        self.current_song = current_song       

# Define the command for playing a son
@bot.command()
async def p(ctx, *, message):
    # Creates a new server queue if one doesn't exist
    entry = {ctx.guild.id : []}   
    if ctx.guild.id not in server_queues:
        server_queues.update(entry)
        current_song.update(entry)
    # Download the requested song and add it to the server queue
    if ctx.author.voice:
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        server_queues[ctx.guild.id].append(song(dl(message,ctx.guild.id), ctx.author.voice, str(ctx.guild.id),voice_client, ctx.author.voice.channel))

# Defines the command for displaying the server queue
@bot.command()
async def queue(ctx):
    try:
        # If a song is playing, display its title at the top of the queue
        if current_song[ctx.guild.id].voice_state.is_playing() == False:
            current_song[ctx.guild.id].title = 'None'
        q = f'Current Song: {current_song[ctx.guild.id].title}\nQueue:\n'
    except AttributeError:
        # If the current song object doesn't have a voice_state attribute, wait 0.5 seconds and try again
        await asyncio.sleep(.5)
        q = f'Current Song: {current_song[ctx.guild.id].title}\nQueue:\n'
        await ctx.channel.send(q)
    except KeyError:
         # If there is no current song object, display "None"
        await ctx.channel.send('Current Song: None\nQueue:\n')
    else:
        # Display the titles of all songs in the server queue
        for pos in range(len(server_queues[ctx.guild.id])):
            q += f'{pos+1}: {server_queues[ctx.guild.id][pos].title}\n'
        await ctx.channel.send(q)

# Defines the command for stopping the current song
@bot.command()
async def sp(ctx):
    if ctx.author.voice:
        # Stops current song
        current_song[ctx.guild.id].voice_state.stop()

# Define the command for removing a song from the server queue
@bot.command()
async def sq(ctx,message):
    if ctx.author.voice:
        try:
            if int(message) <= 0:
                raise ValueError('No negative/zero queue position')
        except ValueError as e:
            # Stops negative or 0 from being entered as a queue position
            await ctx.channel.send(e)
        except IndexError:
            # Exception if poistion entered does not exist
            await ctx.channel.send(f'This queue positon does not exist. The queue is currently {len(server_queues[ctx.guild.id])} items long')
        else:
            #removes the requested queue postion song file and from queue
            os.remove(server_queues[ctx.guild.id][int(message) - 1].path)
            del server_queues[ctx.guild.id][int(message) - 1]

# defines a command to display help information about each command
@bot.command(pass_context=True)
async def help(ctx, message):
    if message == 'p':
        await ctx.channel.send('To use this command type <!p> followed by your desired song\nExample: !p song')
    if message == 'sp':
        await ctx.channel.send('To use this command type <!sp> to remove the current song playing\nExample: !sp')
    if message == 'sq':
        await ctx.channel.send('To use this command type <!sq> followed by the postion in the queue you would like to remove\nExample: !sq 4')
    if message == 'queue':
        await ctx.channel.send('To use this command type <!queue> to show the songs in queue\nExample: !queue')

# Sets how often playing_check() should be run
@loop(seconds = 1)
async def playing_check():  
    # Get the list of server IDs.      
    ids = server_queues.keys()
    # Iterate over the servers.
    for id in ids:
        # Check if the queue is not empty.
        if len(server_queues[id]) > 0:
            # Check if the bot is not currently connected to a voice channel.
            if not server_queues[id][0].voice_state:
                # Connect to the voice channel.
                server_queues[id][0].voice_state = await server_queues[id][0].voice_channel.connect() 
            # Check if the bot is not currently playing audio.
            if server_queues[id][0].voice_state.is_playing() == False:
                # Creates an audio source from the next song in the queue.
                audio_source = discord.FFmpegPCMAudio(server_queues[id][0].path)
                # Plays the audio.
                server_queues[id][0].voice_state.play(audio_source)
                # Remove the song from the queue and store it as the current song.
                current_song[id] = server_queues[id].pop(0)

            # Checks if the current song is still playing.
            if current_song[id].voice_state.is_playing() == True:
                # Deletes the audio file from the system.
                if os.path.exists(current_song[id].path):
                     # Wait for half a second
                    await asyncio.sleep(.5)
                    os.remove(current_song[id].path)   

# This event is triggered when a command is not recognized.
@bot.event
async def on_command_error(ctx, error):
    # Checks if the error is a 'CommandNotFound' error.
    if isinstance(error, commands.CommandNotFound):
        # Sends a message to the channel indicating that the command was not found.
        await ctx.channel.send("No such command. Here is a list of valid commands: "
                               '< p | sp | sq | queue >\n'
                               'For more information on a specific command type !help followed by the command:\n'
                               'Example: !help <queue>')    
              
# This event is triggered when the bot is ready to start processing events.
@bot.event
async def on_ready():
    # Start the 'playing_check()'
    playing_check.start()   

def main():
    # Runs the bot using the provided Discord token.
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
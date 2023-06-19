import discord
import requests
import os
import typing
from discord.ext import commands, tasks
from discord import app_commands, utils


def scan_servers(sorting=None):
    print('scanning servers')
    servers = []
    all_servers = requests.get('https://api.minehut.com/servers')
    output = all_servers.json()['servers']
    print('getting all servers')
    all_categories = []
    server_blacklist = []
    blacklisted_plugins = []  # create a list of all plugin ids that are anticheats

    for server in output:
        try:
            if int(server['playerData']['playerCount']) >= 1 and server['allCategories'] != []:
                unwanted_categories = ['farming', 'prison', 'skyblock', 'parkour', 'rpg', 'escapeRoom', 'mem', 'gens',
                                       'modded', 'box']

                for unwanted_category in unwanted_categories:
                    if unwanted_category not in server['allCategories']:
                        servers.append(server['name'])
                        categories = server['allCategories']
                        for c in categories:
                            all_categories.append(c)
                    else:
                        server_blacklist.append(server['name'])

        except KeyError:
            pass

    servers = list(set(servers))
    print('got all servers')

    for server in servers:
        if server in server_blacklist:
            servers.remove(server)
    print('sorted servers')

    if sorting != 'None':
        if sorting == 'A-Z':
            servers = sorted(servers)
        elif sorting == 'Z-A':
            servers = sorted(servers, reverse=True)
    return servers


def ping_server(server_name: str):
    request = requests.get(f'https://api.minehut.com/server/{server_name}?byName=true')
    data = request.json()
    return data


def strip_fancytext(x: str):
    x = x.replace("<", "*<")
    x = x.replace(">", ">*")
    y = x.split("*")
    res = []
    for i in y:
        if len(i) != 0:
            if i[0] == "<" and i[-1] == ">":
                res.append("")
            else:
                res.append(i)
    res = "".join(res)
    return res

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scan_server.start()

    def cog_unload(self):
        self.scan_server.cancel()

    @tasks.loop(minutes=1)
    async def scan_server(self):
        info = ping_server('Locktup')['server']
        online = info['online']
        last_online = round(info['last_online']/1000)
        if online:
            try:
                me = await self.bot.fetch_user(650923352097292299)  # put ID here
                history = [msg.content async for msg in me.history(limit=75)]
                if f'<t:{last_online}:R>' not in "".join(history):
                    await me.send(f'locktup last went online about <t:{last_online}:R>, but its online rn lol')
                else:
                    pass
            except Exception as err:
                print(err)

    @scan_server.before_loop
    async def wait_for_bot(self):
        print('waiting...')
        await self.bot.wait_until_ready()

    @app_commands.command(name='scan', description='scans the minehut network')
    async def scan(self, interaction: discord.Interaction, output_type: typing.Literal['.txt file'], sorting: typing.Literal['None','A-Z','Z-A']):
        await interaction.response.defer(thinking=True)
        if output_type == '.txt file':
            servers = scan_servers(sorting)
            print('generating txt file')
            content = "Servers: \n- " + "\n- ".join(servers)
            with open('output.txt', 'w') as file:
                file.write(content)
                file.close()
            print('generated file, attempting to send')
            try:
                await interaction.followup.send(file=discord.File('output.txt'))
                print('successfully sent')
            except Exception as err:
                print(err)
            os.remove('output.txt')
            print('temporary file deleted')

    @app_commands.command(name='server', description='ping a specific server')
    async def server_ping(self, interaction: discord.Interaction, server_name: str):
        await interaction.response.defer(thinking=True)
        try:
            info = ping_server(server_name)['server']
            id = info['_id']
            categories = ', '.join(info['categories'])
            server_type = info['server_version_type']
            motd = info['motd'].replace('\n','')
            motd = strip_fancytext(motd)
            server_plan = info['server_plan']
            name = info['name']
            visibility = info['visibility']
            platform = info['platform']
            online = info['online']
            player_count = info['playerCount']
            max_players = info['maxPlayers']
            if online:
                colour = discord.Colour.brand_green()
            else:
                colour = discord.Colour.brand_red()
            embed = discord.Embed(title=name, colour=colour)
            embed.add_field(name='Categories', value=categories.title())
            embed.add_field(name='Server ID', value=str(id))
            embed.add_field(name='Platform', value=platform.upper())
            embed.add_field(name='Server Type', value=server_type)
            embed.add_field(name='Server Plan', value=server_plan)
            embed.add_field(name='MOTD', value=motd)
            embed.add_field(name='Visibility', value=str(visibility))
            embed.add_field(name='Current Player Count', value=f"{player_count}/{max_players} (max: {max_players})")
            await interaction.followup.send(embed=embed)
        except:
            embed = discord.Embed(description='Invalid server name :(', colour=discord.Colour.dark_red())
            await interaction.followup.send(embed=embed)



async def setup(bot):
    await bot.add_cog(Commands(bot))

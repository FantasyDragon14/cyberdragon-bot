"""For Administration shit. stuff like 'ban for so long', 'kick for *reason*'
all the administrative stuff other bots also have, for properly guarding the nest or sum shit
isn't that already built into discord nowadays? 
"""

#i don't even know what functions/commands to put here yet. Haven't had anything come up where normal discord mod tools didn't suffice (or where having a bot have this functionality woulda been more convenient i guess?)

import hikari
import lightbulb as commands
import logging
import Util.data as Data
import Util.utils as Utils

class Loader(commands.Loader):
    async def remove_from_client(self, client: commands.Client) -> None:
        #unload / close db connections here?
        logger.info('Removing admin Extension')
        return await super().remove_from_client(client)
    
    async def add_to_client(self, client:commands.Client) -> None:
        logger.info('adding admin extension')
        await register_commands()
        await super().add_to_client(client)
        
loader = Loader()

logger = logging.getLogger("admin")

group = commands.Group('admin', 'general administrator utilities')

@group.register
class config_reload(
    commands.SlashCommand,
    name="configreload",
    description="reloads the config file of the guild, reverting missing values to default",
    hooks=[commands.prefab.has_permissions(hikari.Permissions.ADMINISTRATOR)],
):
    @commands.invoke
    async def configreload(self, ctx:commands.Context) -> None:
        Data.assert_guild_config(ctx.guild_id)
        await ctx.respond('done', ephemeral=True)

@group.register
class see_extensions_CMD(
    commands.SlashCommand,
    name="see-extensions",
    description="see what (toggleable) extensions your Guild has enabled and which not",
    hooks=[commands.prefab.has_permissions(hikari.Permissions.ADMINISTRATOR),]
):
    @commands.invoke
    async def get_extensions(self, ctx:commands.Context) -> None:
        data = Data.config_guild_get_extensions(ctx.guild_id)
        msg = Utils.pretty_dict_tostring(data)
        await ctx.respond(msg)

async def register_commands(guild_ids:list = []):
    if len(guild_ids) < 1:
        guilds_it = Data.bot.rest.fetch_my_guilds()
        async for guild in guilds_it:
            guild_ids.append(guild.id)
    loader.command(command=group, guilds=guild_ids)
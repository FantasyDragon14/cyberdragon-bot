#extension to handle all command errors

import os
import sys
import hikari
import lightbulb as commands
import asyncio
import logging
import Util.data as Data

class Loader(commands.Loader):
    async def remove_from_client(self, client: commands.Client) -> None:
        #unload / close db connections here?
        logger.info('Removing Error Extension')
        return await super().remove_from_client(client)
    
    async def add_to_client(self, client:commands.Client) -> None:
        logger.info('adding Error extension')
        await super().add_to_client(client)
        
loader = Loader()

logger = logging.getLogger("error")

@loader.error_handler(priority=100)
async def handle_not_owner(exc: commands.exceptions.ExecutionPipelineFailedException) -> bool:
    logger.debug('catching owner only...')
    for exception in exc.hook_failures:
        if isinstance(exception, commands.prefab.checks.NotOwner):
            logger.info(f"{exc.context.member.display_name} (from {exc.context.guild_id}) tried to use a dev only command")
            await exc.context.respond('Nuh uh, only my Developers can do that', ephemeral=True)
            return True
    return False

@loader.error_handler(priority=99)
async def handle_no_permission(exc: commands.exceptions.ExecutionPipelineFailedException) -> bool:
    logger.debug('catching permission errors...')
    for exception in exc.hook_failures:
        if isinstance(exception, commands.prefab.checks.MissingRequiredPermission):
            logger.debug(f"{exc.context.member.display_name} (from {exc.context.guild_id}) tried executing a gated command without Permission {exception.missing}")
            await exc.context.respond(f"You need the permission(s) {exception.missing} to be able to do that", ephemeral=True)
            return True
    return False
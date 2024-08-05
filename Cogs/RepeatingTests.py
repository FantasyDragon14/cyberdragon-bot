from discord.ext import tasks, commands



class RepeatingTests(commands.Cog):
        def __init__(self, bot):
                self.bot = bot
                self.loop_channel = None
                
        '''
        async def setup_hook(self):
                await self.bot.wait_until_ready()
                self.repeat_refresh.start()
        '''
        
        @commands.hybrid_command(name='start_ping_loop')
        async def start(self, ctx):
                if not self.repeat_refresh.is_running():
                        self.loop_channel = ctx
                        self.repeat_refresh.start(ctx)
                
        @commands.hybrid_command(name='ping_stop', )
        async def stop(self, ctx):
                if self.repeat_refresh.is_running():
                        self.repeat_refresh.cancel()
                
        @tasks.loop(seconds=10)
        async def repeat_refresh(self, ctx):
                print(f"refresh: {self.repeat_refresh.current_loop}")
                await self.loop_channel.send(f"ping {self.repeat_refresh.current_loop}")
        
async def setup(bot):
        await bot.add_cog(RepeatingTests(bot))
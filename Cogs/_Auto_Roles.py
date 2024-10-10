class Auto_Roles(commands.Cog):
        def __init__(self, bot):
                self.bot = bot
                self._last_member = None
                self.bot.logger.info("[Auto_Roles] starting Auto_Roles")

        @commands.Cog.listener()
        async def on_member_join(self, member):
                await wait()
                        
        @commands.hybrid_command(name="verify_member")
        async def verify(self, ctx, *, member: discord.Member = None):
                """gives a user the member role"""
                pass
                
                
async def setup(bot):
        bot.logger.info("[Auto_Roles] adding AutoRoles")
        await bot.add_cog(Greetings(bot))
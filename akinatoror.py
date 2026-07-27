import asyncio
import discord
import akipy
from akipy.async_akinator import Akinator
from discord import app_commands
from discord.ext import commands

class Akinatoror(commands.Cog):
    def __init__(self, bot):
        self.message_embed = discord.Embed(
            title="",
            description="You have 30 seconds to select an answer.",
            color=discord.Color.blue()
        )
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is online and ready to start guessing!")

    @app_commands.command(name="aki", description="Begins a game of Akinator.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def aki(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            aki = Akinator()
            self.message_embed.title = "Select a Gamemode"
            await interaction.followup.send(embed=self.message_embed, view=selection)
            await selection.wait()
    
            await aki.start_game()
            await interaction.followup.send(str(aki))

        except Exception as e:
            print(e)


class GamemodeSelection(discord.ui.View):
    @discord.ui.button(label="Characters", style=discord.ButtonStyle.primary)
    async def callback_char(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.ans = "c"
        self.stop()
     
    @discord.ui.button(label="Animals", style=discord.ButtonStyle.primary)
    async def callback_irs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.ans = "a"
        self.stop()
      
    @discord.ui.button(label="Objects", style=discord.ButtonStyle.primary)
    async def callback_obj(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.ans = "o"
        self.stop()

class QuestionInterface(discord.ui.View):
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.primary, emoji="✅")
    async def callback_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
     
    @discord.ui.button(label="No", style=discord.ButtonStyle.primary, emoji="👎")
    async def callback_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
      
    @discord.ui.button(label="Don't Know", style=discord.ButtonStyle.primary, emoji="🤷")
    async def callback_idk(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
       
    @discord.ui.button(label="Probably", style=discord.ButtonStyle.primary, emoji="🤷‍♀️👍")
    async def callback_idk(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
        
    @discord.ui.button(label="Probably Not", style=discord.ButtonStyle.primary, emoji="🤷‍♂️👎")
    async def callback_idk(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
 
    @discord.ui.button(label="Go Back", style=discord.ButtonStyle.primary, emoji="⬅️")
    async def callback_idk(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

async def setup(bot):
    await bot.add_cog(Akinatoror(bot))

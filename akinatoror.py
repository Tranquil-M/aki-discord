import asyncio
import discord
import akipy
from akipy.async_akinator import Akinator
from discord import app_commands
from discord.ext import commands

class Akinatoror(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def main_loop(self, interaction):
        self.message_embed = discord.Embed(
            title="",
            description="You have 30 seconds to select an answer.",
            color=discord.Color.blue()
        )

        try:
            aki = Akinator()
            last_message = None
            last_question = ""
            last_choice = ""

            await aki.start_game()
            while not aki.win:
                self.message_embed.title = str(aki)
                selection = QuestionInterface()

                if last_message is not None:
                    await last_message.edit(embed=discord.Embed(title=last_question, description=last_choice), view=None)
                last_message = await interaction.followup.send(embed=self.message_embed, view=selection)

                await selection.wait()
                
                last_choice = selection.ans
                last_question = str(aki)
                await aki.answer(selection.ans)

            if last_message is not None:
                await last_message.edit(embed=discord.Embed(title=last_question, description=last_choice), view=None)
                
            self.message_embed.title = str(aki)
            self.message_embed.description = aki.description_proposition
            self.message_embed.set_image(url=aki.photo)

            correct = WinCheck()

            await interaction.followup.send(embed=self.message_embed, view=correct)
            await correct.wait()
            return correct.ans

        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is online and ready to start guessing!")

    @app_commands.command(name="aki", description="Begins a game of Akinator.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def aki(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            while True:
                result = await self.main_loop(interaction)
                if result == True:
                    break

            await interaction.followup.send(f"I'm just that cool 😎")
        except Exception as e:
            print(e)

class WinCheck(discord.ui.View):
    @discord.ui.button(label="Correct", style=discord.ButtonStyle.primary)
    async def callback_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.ans = True
        self.stop()
     
    @discord.ui.button(label="Incorrect", style=discord.ButtonStyle.primary)
    async def callback_loss(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.ans = False
        self.stop()

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
        await interaction.response.defer()
        self.ans = "yes"
        self.stop()
     
    @discord.ui.button(label="No", style=discord.ButtonStyle.primary, emoji="👎")
    async def callback_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.ans = "no"
        self.stop()
      
    @discord.ui.button(label="Don't Know", style=discord.ButtonStyle.primary, emoji="🤷")
    async def callback_idk(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.ans = "idk"
        self.stop()
      
    @discord.ui.button(label="Probably", style=discord.ButtonStyle.primary, emoji="🤷‍♀️")
    async def callback_prob(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.ans = "probably"
        self.stop()
      
    @discord.ui.button(label="Probably Not", style=discord.ButtonStyle.primary, emoji="🤷‍♂️")
    async def callback_probn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.ans = "probably not"
        self.stop()
 
    #@discord.ui.button(label="Go Back", style=discord.ButtonStyle.primary, emoji="⬅️")
    #async def callback_back(self, interaction: discord.Interaction, button: discord.ui.Button):
    #    await interaction.response.defer()
    #    self.ans = 5
    #    self.stop()
 
async def setup(bot):
    await bot.add_cog(Akinatoror(bot))

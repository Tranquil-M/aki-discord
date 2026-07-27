import asyncio
from datetime import datetime, timezone
import discord
import akipy
from akipy.async_akinator import Akinator
from discord import app_commands
from discord.ext import commands

class Akinatoror(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def main_loop(self, interaction, thread: discord.Thread):
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
                selection = QuestionInterface(interaction.user)

                if last_message is not None:
                    await last_message.edit(embed=discord.Embed(title=last_question, description=last_choice), view=None)
                last_message = await thread.send(embed=self.message_embed, view=selection)

                selection.game_message = last_message

                await selection.wait()

                last_choice = selection.ans
                last_question = str(aki)
                await aki.answer(selection.ans)

            if last_message is not None:
                await last_message.edit(embed=discord.Embed(title=last_question, description=last_choice), view=None)
                
            self.message_embed.title = str(aki)
            self.message_embed.description = aki.description_proposition
            self.message_embed.set_image(url=aki.photo)

            correct = WinCheck(interaction.user)

            await thread.send(embed=self.message_embed, view=correct)
            await correct.wait()
            return correct.ans

        except Exception as e:
            return None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is online and ready to start guessing!")

    @app_commands.command(name="aki", description="Begins a game of Akinator.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def aki(self, interaction: discord.Interaction):
        try:
            if isinstance(interaction.channel, discord.Thread):
                await interaction.response.send_message("This command can not be used in threads, sorry! 🫠", ephemeral=True)
                return

            await interaction.response.defer()
            now = datetime.now(timezone.utc)
            readable_date = now.strftime("%m-%d-%Y %H:%M:%S UTC")

            thread = await interaction.channel.create_thread(
                name=f"Akinator - {interaction.user.display_name} - {readable_date}",
                type=discord.ChannelType.public_thread,
                auto_archive_duration=60
            )

            await interaction.followup.send(f"I've made you a thread so you can enjoy your game without convo! Have fun :D <#{thread.id}>")
        except Exception as e:
            print(e)

        try:
            while True:
                result = await self.main_loop(interaction, thread)
                if result == True:
                    await thread.send(f"I'm just that cool 😎")
                    break
                elif result == False:
                    await thread.send(f"Damn it! Let me try again...")
                elif result is None:
                    break

        except Exception as e:
            print(e)
        finally:
            await asyncio.sleep(5)
            try:
                await thread.edit(archived=True, locked=True)
            except discord.HTTPException:
                pass

class WinCheck(discord.ui.View):
    def __init__(self, owner: discord.User | discord.Member):
            super().__init__(timeout=30.0)
            self.owner = owner
            self.game_message = None
            self.timed_out = False

    async def on_timeout(self):
        self.timed_out = True
        self.stop()
        
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
                
        if self.game_message:
            try:
                embed = self.game_message.embeds[0]
                embed.title = "Game Timed Out"
                embed.description = "You took too long to answer. Start a new game with `/aki`!"
                embed.color = discord.Color.red()
                await self.game_message.edit(embed=embed, view=self)
            except discord.HTTPException:
                pass 

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.owner.id:
            return True
            
        await interaction.response.send_message(
            "Hey, don't interfere with other's fun!", 
            ephemeral=True
        )
        return False

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
    def __init__(self, owner: discord.User | discord.Member):
            super().__init__(timeout=30.0)
            self.owner = owner
            self.game_message = None
            self.timed_out = False

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.owner.id:
            return True
            
        await interaction.response.send_message(
            "Hey, don't interfere with other's fun!", 
            ephemeral=True
        )
        return False

    async def on_timeout(self):
        self.timed_out = True
        self.stop()
        
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
                
        if self.game_message:
            try:
                embed = self.game_message.embeds[0]
                embed.title = "Game Timed Out"
                embed.description = "You took too long to answer. Start a new game with `/aki`!"
                embed.color = discord.Color.red()
                await self.game_message.edit(embed=embed, view=self)
            except discord.HTTPException:
                pass 

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
    def __init__(self, owner: discord.User | discord.Member):
            super().__init__(timeout=30.0)
            self.owner = owner
            self.game_message = None
            self.timed_out = False

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.owner.id:
            return True
            
        await interaction.response.send_message(
            "Hey, don't interfere with other's fun!", 
            ephemeral=True
        )
        return False

    async def on_timeout(self):
        self.timed_out = True
        self.stop()
        
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
                
        if self.game_message:
            try:
                embed = self.game_message.embeds[0]
                embed.title = "Game Timed Out"
                embed.description = "You took too long to answer. Start a new game with `/aki`!"
                embed.color = discord.Color.red()
                await self.game_message.edit(embed=embed, view=self)
            except discord.HTTPException:
                pass 

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

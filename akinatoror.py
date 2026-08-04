import asyncio
from datetime import datetime, timezone
from collections import deque
import discord
import akipy
from akipy.async_akinator import Akinator
from discord import app_commands
from discord.ext import commands

class Akinatoror(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def edit_last_question(self, messages):
        if len(messages) > 0:
            last_question = messages[-1]
            await last_question["message"].edit(
                embed=discord.Embed(
                    title = last_question["question"],
                    description = last_question["choice"],
                ),
                view=None
            )

    async def main_loop(self, interaction, game_mode: str, child_mode: bool, game_message = None, thread: discord.Thread = None):
        try:
            aki = Akinator()
            messages = deque(maxlen=2)

            await aki.start_game(game_mode=game_mode, child_mode=child_mode)
            
            if game_message and thread is None:
                while not aki.win:
                    embed = discord.Embed(
                        title=str(aki),
                        description="You have 30 seconds to select an answer.",
                        color=discord.Color.blue(),
                    )

                    selection = QuestionInterface(interaction.user, aki)
                    await game_message.edit(
                        embed=embed,
                        view=selection
                    )

                    selection.game_message = game_message
                    await selection.wait()

                    if selection.ans is None:
                        return "timeout"

                    if selection.ans == "back":
                        await aki.back()
                        continue

                    await aki.answer(selection.ans)

                embed = discord.Embed(
                    title=str(aki),
                    description=aki.description_proposition,
                    color=discord.Color.yellow(),
                )
                embed.set_image(url=aki.photo)

                win_check = WinCheck(interaction.user)

                await game_message.edit(
                    embed=embed,
                    view=win_check,
                )

                win_check.game_message = game_message
                await win_check.wait()

                if win_check.ans is None:
                    return "timeout"

                if win_check.ans:
                    embed.color = discord.Color.green()
                    embed.set_footer(text="✅ Correct")
                else:
                    embed.color = discord.Color.red()
                    embed.set_footer(text="👎 Incorrect")

                await game_message.edit(
                    embed=embed,
                    view=None,
                )

                return win_check.ans

            while not aki.win:
                message_embed = discord.Embed(
                    title = str(aki),
                    description="You have 30 seconds to select an answer.",
                    color = discord.Color.blue(),
                )

                await self.edit_last_question(messages)

                selection = QuestionInterface(interaction.user, aki)

                question = {
                    "message": await thread.send(
                        embed=message_embed,
                        view=selection,
                    ),
                    "question": str(aki),
                    "choice": None,
                }
                
                await selection.wait()

                if selection.timed_out or selection.ans is None:
                    return "timeout"

                question["choice"] = selection.ans

                messages.append(question)

                if selection.ans == "back":
                    await aki.back()
                    await messages[-1]["message"].delete()
                    await messages[-2]["message"].delete()
                    messages.clear()
                    continue

                await aki.answer(selection.ans)

            await self.edit_last_question(messages)

            message_embed = discord.Embed(
                title = str(aki),
                description = aki.description_proposition,
                color = discord.Color.yellow()
            )
            message_embed.set_image(url = aki.photo)

            win_check = WinCheck(interaction.user)
            proposition = await thread.send(embed=message_embed, view=win_check)

            await win_check.wait()

            if win_check.ans is None:
                return "timeout"

            if win_check.ans == True:
                message_embed.set_footer(text="✅ Correct")
                message_embed.color = discord.Color.green()
            else:
                message_embed.set_footer(text="👎 Incorrect")
                message_embed.color = discord.Color.red()

            await proposition.edit(embed=message_embed, view=None)

            return win_check.ans

        except Exception as e:
            print(e)
            return None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is online and ready to start guessing!")

    async def dm_cmd(self, interaction: discord.Interaction):
        await interaction.response.defer()

        message_embed = discord.Embed(
            title = "Select a gamemode!",
            description = "You have 30 seconds to select an answer.",
            color=discord.Color.blue(),
        )
        mode = GamemodeSelection(interaction.user)
        setup_message = await interaction.followup.send(embed=message_embed, view=mode)
        mode.game_message = setup_message

        await mode.wait()

        if mode.ans is None:
            return

        message_embed = discord.Embed(
            title = "Would you like to play in child mode? (No NSFW)",
            description = "You have 30 seconds to select an answer.",
            color=discord.Color.blue(),
        )

        child = ChildmodeSelection(interaction.user)
        await setup_message.edit(embed=message_embed, view=child)
        child.game_message = setup_message

        await child.wait()

        if child.ans is None:
            return

        while True:
            result = await self.main_loop(interaction, mode.ans, child.ans, setup_message)
            if result:
                break
            elif result == False:
                await asyncio.sleep(1.5)
                await interaction.followup.send("Darn! I'll get it next time...")
                break
            elif result == "timeout":
                break

    async def server_cmd(self, interaction: discord.Interaction):
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
            message_embed = discord.Embed(
                title = "Select a gamemode!",
                description = "You have 30 seconds to select an answer.",
                color=discord.Color.blue(),
            )
            mode = GamemodeSelection(interaction.user)
            last_message = await thread.send(embed=message_embed, view=mode)
            mode.game_message = last_message

            await mode.wait()

            if mode.ans is None:
                return

            if mode.ans == "c":
                message_embed.description = "🧑 Character"
            elif mode.ans == "a":
                message_embed.description = "😺 Animal"
            else:
                message_embed.description = "🍴 Object"

            message_embed.color = discord.Color.green()

            await last_message.edit(embed=message_embed, view=None)

            message_embed = discord.Embed(
                title = "Would you like to play in child mode? (No NSFW)",
                description = "You have 30 seconds to select an answer.",
                color=discord.Color.blue(),
            )

            child = ChildmodeSelection(interaction.user)
            last_message = await thread.send(embed=message_embed, view=child)
            child.game_message = last_message

            await child.wait()

            if child.ans is None:
                return

            if child.ans:
                message_embed.description = "🫰 Family friendly please!"
                message_embed.color = discord.Color.green()
            else:
                message_embed.description = "🚫 No"
                message_embed.color = discord.Color.red()

            await last_message.edit(embed=message_embed, view=None)

            while True:
                result = await self.main_loop(interaction, thread, mode.ans, child.ans)
                if result == True:
                    await thread.send(f"I'm just that cool 😎")
                    break
                elif result == False:
                    await thread.send(f"Damn it! Let me try again...")
                elif result == "timeout":
                    break

        except Exception as e:
            print(e)
        finally:
            await asyncio.sleep(5)
            try:
                await thread.edit(archived=True, locked=True)
            except discord.HTTPException:
                pass

    @app_commands.command(name="aki", description="Begins a game of Akinator.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def aki(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await self.dm_cmd(interaction)
        else:
            await self.server_cmd(interaction)

class _Base(discord.ui.View):
    def __init__(self, owner: discord.User | discord.Member):
        super().__init__(timeout=30.0)
        self.owner = owner
        self.game_message = None
        self.timed_out = False
        self.ans = None
        self.cd_mapping = commands.CooldownMapping.from_cooldown(
            1, 1.0, commands.BucketType.user
        )

    async def select(self, interaction, value):
        await interaction.response.defer()
        self.ans = value
        self.stop()

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
        if interaction.user.id != self.owner.id:
            await interaction.response.send_message(
                "Hey, don't interfere with other's fun!", 
                ephemeral=True
            )
            return False

        bucket = self.cd_mapping.get_bucket(interaction.message)
        retry_after = bucket.update_rate_limit()

        if retry_after:
          await interaction.response.send_message(
              f"Slow down! Try again in {retry_after:.1f} seconds.", ephemeral=True
          )
          return False
        return True     

class WinCheck(_Base):
    def __init__(self, owner: discord.User | discord.Member):
            super().__init__(owner)

    @discord.ui.button(label="Correct", style=discord.ButtonStyle.primary)
    async def callback_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select(interaction, True)
             
    @discord.ui.button(label="Incorrect", style=discord.ButtonStyle.primary)
    async def callback_loss(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select(interaction, False)

class ChildmodeSelection(_Base):
    def __init__(self, owner: discord.User | discord.Member):
            super().__init__(owner)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.primary)
    async def callback_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select(interaction, True)
     
    @discord.ui.button(label="No", style=discord.ButtonStyle.primary)
    async def callback_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select(interaction, False)

class GamemodeSelection(_Base):
    def __init__(self, owner: discord.User | discord.Member):
            super().__init__(owner)

    @discord.ui.button(label="Characters", style=discord.ButtonStyle.primary)
    async def callback_char(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select(interaction, "c")
     
    @discord.ui.button(label="Animals", style=discord.ButtonStyle.primary)
    async def callback_irs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select(interaction, "a")
      
    @discord.ui.button(label="Objects", style=discord.ButtonStyle.primary)
    async def callback_obj(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select(interaction, "o")

class QuestionInterface(_Base):
    def __init__(self, owner: discord.User | discord.Member, aki):
        super().__init__(owner)
        self.aki = aki
        if int(self.aki.step) <= 0:
            self.remove_item(self.callback_back)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.primary, emoji="✅")
    async def callback_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select(interaction, "yes")
     
    @discord.ui.button(label="No", style=discord.ButtonStyle.primary, emoji="👎")
    async def callback_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select(interaction, "no")

    @discord.ui.button(label="Don't Know", style=discord.ButtonStyle.primary, emoji="🤷")
    async def callback_idk(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select(interaction, "idk")
      
    @discord.ui.button(label="Probably", style=discord.ButtonStyle.primary, emoji="🤷‍♀️")
    async def callback_prob(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select(interaction, "probably")
      
    @discord.ui.button(label="Probably Not", style=discord.ButtonStyle.primary, emoji="🤷‍♂️")
    async def callback_probn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select(interaction, "probably not")

    @discord.ui.button(label="Go Back", style=discord.ButtonStyle.primary, emoji="⬅️")
    async def callback_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select(interaction, "back")
     
async def setup(bot):
    await bot.add_cog(Akinatoror(bot))

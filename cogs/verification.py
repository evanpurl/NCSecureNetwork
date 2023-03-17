import discord
from discord import app_commands
from discord.ext import commands
from util.dbsetget import dbget, dbset

# Needs "manage role" perms
"Requires verifiedroleid in db"


def verifymessageembed(server):
    embed = discord.Embed(title=f"**{server.name} Verification Process**",
                          description=f"Are you a member of the Hazel Police department? If yes, click the yes button "
                                      f"below.",
                          color=discord.Color.red())
    return embed


class Verifybuttonpanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green,
                       custom_id="NCSN:yes")
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.user.ban(reason="Possible cop")

        except Exception as e:
            print(e)

    @discord.ui.button(label="No", style=discord.ButtonStyle.red,
                       custom_id="NCSN:no")
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            verrole = await dbget(interaction.guild.id, "ncsn", "verifiedroleid")
            role = discord.utils.get(interaction.guild.roles, id=verrole[0])
            if role:
                if role in interaction.user.roles:
                    await interaction.response.send_message(f"You have already been verified.", ephemeral=True)
                else:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message(f"User verified.",
                                                            ephemeral=True)
            else:
                await interaction.response.send_message(f"Verified role does not exist, please contact an admin.",
                                                        ephemeral=True)

        except discord.Forbidden:
            await interaction.response.send_message(
                content=f"""Unable to set your role, make sure my role is higher than the role you're trying to add!""",
                ephemeral=True)


class verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="verification", description="Command used by an admin to send the verification message")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def vbutton(self, interaction: discord.Interaction) -> None:
        try:
            await interaction.response.send_message(embed=verifymessageembed(interaction.guild),
                                                    view=Verifybuttonpanel())
        except Exception as e:
            print(e)

    @app_commands.command(name="setverifiedrole", description="Command used to set the Verified role")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def verifiedrole(self, interaction: discord.Interaction, role: discord.Role) -> None:
        try:
            await dbset(interaction.guild.id, "ncsn", "verifiedroleid", role.id)
            await interaction.response.send_message(content=f"Verified role set to {role.mention}", ephemeral=True)
        except Exception as e:
            print(e)

    @app_commands.command(name="resetverifiedrole", description="Command used to reset the Verified role")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def resetverifiedrole(self, interaction: discord.Interaction) -> None:
        try:
            await dbset(interaction.guild.id, "ncsn", "verifiedroleid", 0)
            await interaction.response.send_message(f"Verified Role config has been reset.", ephemeral=True)
        except Exception as e:
            print(e)

    @verifiedrole.error
    @resetverifiedrole.error
    async def onerror(self, interaction: discord.Interaction, error: app_commands.MissingPermissions):
        await interaction.response.send_message(content=error,
                                                ephemeral=True)


async def setup(bot):
    await bot.add_cog(verification(bot))
    bot.add_view(Verifybuttonpanel())

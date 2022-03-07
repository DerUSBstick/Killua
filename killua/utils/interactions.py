import discord

from typing import Union

class View(discord.ui.View):
    """Subclassing this for buttons enabled us to not have to define interaction_check anymore, also not if we want a select menu"""
    def __init__(self, user_id:int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.value = None
        self.timed_out = False

    async def on_timeout(self) -> None:
        self.timed_out = True

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not (val := interaction.user.id == self.user_id):
            await interaction.response.defer()
        return val

    async def disable(self, msg:discord.Message) -> Union[discord.Message, None]:
        """"Disables the children inside of the view"""
        if not [c for c in self.children if not c.disabled]: # if every child is already disabled, we don't need to edit the message again
            return

        for c in self.children:
            c.disabled = True

        await msg.edit(view=self)

class Select(discord.ui.Select):
    """Creates a select menu to view the command groups"""
    def __init__(self, options, **kwargs):
        super().__init__( 
            min_values=1, 
            max_values=1, 
            options=options,
            **kwargs
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.value = int(interaction.data["values"][0])
        for opt in self.options:
            if opt.value == str(self.view.value):
                opt.default = True
        self.view.stop()

class Button(discord.ui.Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.custom_id
        self.view.stop()

class ConfirmButton(discord.ui.View):
    """A button that is used to confirm a certain action or deny it"""
    def __init__(self, user_id:int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.timed_out = False # helps subclasses using Button to have set this to False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not (val := interaction.user.id == self.user_id):
            await interaction.response.defer()
        return val

    async def disable(self, msg:discord.Message) -> discord.Message:
        if len([c for c in self.children if not c.disabled]) == 0: # if every child is already disabled, we don't need to edit the message again
            return

        for child in self.children:
            child.disabled = True

        await msg.edit(view=self)

    async def on_timeout(self):
        self.value = False
        self.timed_out = True
    
    @discord.ui.button(label="confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.timed_out = False
        self.stop()

    @discord.ui.button(label="cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.timed_out = False
        self.stop()
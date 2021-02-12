import discord
import random as r
import asyncio

intents = discord.Intents.default()
intents.members = True
r.seed(a=None)
f = open('token.txt')
token = f.read()
f.close()


def return_full_name(user):
    return f'{user.name}#{user.discriminator}'


def hasRole(user, roleName):
    for role in user.roles:
        if role.name == roleName:
            return True
    return False


class Bot(discord.Client):
    async def on_ready(self):
        print('logged in as')
        print(self.user)
        print(self.user.id)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='you all'))

    async def on_message(self, message):
        await self.wait_until_ready()
        c = discord.Color.from_rgb(0, 0, 0)
        c2 = discord.Color.from_rgb(255, 0, 0)
        embed = discord.Embed(title='Battle Results', color=c)
        embed2 = discord.Embed(title='Covert Operation Ressults', color=c2)
        if message.channel.type is discord.ChannelType.private and message.content.startswith('!covert'):
            guild = self.get_guild(803719660645515364)
            logChannel = discord.utils.get(guild.channels, name='logs')
            args = message.content.removeprefix('!covert').split()
            attack = message.author
            try:
                defense = self.get_user(int(args[0]))
            except IndexError:
                await message.author.send("You didn't mention anyone in your message. Please try again.")
                return
            except ValueError:
                await message.author.send("That is not a user ID. Please try again.")
                return
            if 1 in range(len(args)):
                location = args[1]
            else:
                location = None
            embed2.add_field(name='Target', value=defense, inline=True)
            embed2.add_field(name='Initiator', value=attack, inline=True)
            if location is not None:
                embed2.add_field(name='Purpose', value=location, inline=True)
                if location == 'quell' and message.author.id == int(args[0]):
                    embed2.add_field(name='Defensive Number', value='*None*', inline=True)
                    embed2.add_field(name='Attacking Number', value='*None*', inline=True)
                    embed2.add_field(name='Difference', value='*None*', inline=True)
                    embed2.add_field(name='Result', value='Success', inline=False)
                    await message.author.send('Success.')
                    await logChannel.send(embed=embed2)
                    return
            else:
                embed2.add_field(name='Purpose', value='*Not Specified*', inline=True)
            await message.author.send(f'Covert operation has started on {defense}. Guess a number between `1` and '
                                      f'`1000`')

            defnumber = r.randint(1, 1000)

            def is_num_off(m):
                try:
                    return m.author == attack and 1 <= int(
                        m.content) <= 1000 and m.channel.type is discord.ChannelType.private
                except ValueError:
                    return False

            try:
                attnumber = await self.wait_for('message', check=is_num_off, timeout=43200)
            except asyncio.TimeoutError:
                await attack.send('12 hours have passed and no response. Operation cancelled.')
                embed2.add_field(name='Defensive Number', value=str(defnumber), inline=True)
                embed2.add_field(name='Attacking Number', value='*None*', inline=True)
                embed2.add_field(name='Difference', value='*Aborted*', inline=True)
                await logChannel.send(embed=embed2)
                return

            diff = abs(int(attnumber.content) - defnumber)
            if diff > 500:
                diff = 1000 - diff
            embed2.add_field(name='Defensive Number', value=str(defnumber), inline=True)
            embed2.add_field(name='Attacking Number', value=attnumber.content, inline=True)
            embed2.add_field(name='Difference', value=str(diff), inline=True)
            reply = f'Submitted Number: {attnumber.content}\nDefensive Number: {defnumber}\nDifference: {diff}\n'
            if 1 <= diff <= 50:
                reply += 'Critical Success!'
                embed2.add_field(name='Result', value='Critical Success', inline=False)
            elif 51 <= diff <= 150:
                reply += 'Success!'
                embed2.add_field(name='Result', value='Success', inline=False)
            elif 151 <= diff <= 250:
                reply += 'Failure. Target did not find out.'
                embed2.add_field(name='Result', value='Silent Failure', inline=False)
            elif 251 <= diff <= 400:
                reply += "Failure. They found out, but they don't know who did it."
                embed2.add_field(name='Result', value='Failure', inline=False)
            else:
                reply += 'Critical failure. They found out, and they know we did it.'
                embed2.add_field(name='Result', value='Critical Failure', inline=False)
            await message.author.send(reply)
            await logChannel.send(embed=embed2)
        if message.author.id == self.user.id or message.channel is None:
            return

        if message.content.startswith('!roll'):
            rollNumber = r.randint(0, 4)
            await message.reply(f'The random number is {rollNumber + 1}')

        if message.content.startswith('!startbattle'):
            if hasRole(message.author, 'Bot Operator'):
                logChannel = discord.utils.get(message.guild.channels, name='logs')
                args = message.content.removeprefix('!startbattle').split(maxsplit=1)
                attack = discord.utils.get(message.guild.members, id=int(args[0]))
                defense = discord.utils.get(message.guild.members, id=int(args[1]))
                if 2 in range(len(args)):
                    location = args[2]
                else:
                    location = None
                embed.add_field(name='Defender', value=defense, inline=True)
                embed.add_field(name='Attacker', value=attack, inline=True)
                if location is not None:
                    embed.add_field(name='Location', value=location, inline=True)
                else:
                    embed.add_field(name='Location', value='*Not Specified*', inline=True)
                await defense.send(f'You are being attacked by {attack}! Respond with a number between `1` and `1000`.')
                await message.channel.send(f'Attack has started on {defense}')

                def is_num_def(m):
                    return m.author.id == int(args[1]) and 1 <= int(
                        m.content) <= 1000 and m.channel.type is discord.ChannelType.private

                try:
                    defnumber = await self.wait_for('message', check=is_num_def, timeout=43200)
                except asyncio.TimeoutError:
                    await defense.send('12 hours have passed and no response. Battle is an auto defeat!')
                    embed.add_field(name='Defensive Number', value='*None*', inline=True)
                    embed.add_field(name='Attacking Number', value='*None*', inline=True)
                    embed.add_field(name='Difference', value='Attackers auto-win', inline=True)
                    await logChannel.send(embed=embed)
                    return

                await attack.send(f'{defense} has submitted their number. Reply with a number between `1` and `1000`.')

                def is_num_off(m):
                    return m.author.id == int(args[0]) and 1 <= int(
                        m.content) <= 1000 and m.channel.type is discord.ChannelType.private

                try:
                    attnumber = await self.wait_for('message', check=is_num_off, timeout=43200)
                except asyncio.TimeoutError:
                    await attack.send('12 hours have passed and no response. Battle is an auto defeat!')
                    embed.add_field(name='Defensive Number', value=defnumber, inline=True)
                    embed.add_field(name='Attacking Number', value='*None*', inline=True)
                    embed.add_field(name='Difference', value='Defenders auto-win', inline=True)
                    await logChannel.send(embed=embed)
                    return

                diff = abs(int(attnumber.content) - int(defnumber.content))
                if diff > 500:
                    diff = 1000 - diff
                embed.add_field(name='Defensive Number', value=defnumber.content, inline=True)
                embed.add_field(name='Attacking Number', value=attnumber.content, inline=True)
                embed.add_field(name='Difference', value=str(diff), inline=True)
                await logChannel.send(embed=embed)
            else:
                await message.channel.send('You do not have permission to use this command.\n' +
                                           'If you want to start a battle with another user,' +
                                           'use the !attack command instead.')

        if message.content.startswith('!attack'):
            logChannel = discord.utils.get(message.guild.channels, name='logs')
            args = message.content.removeprefix('!attack').split(maxsplit=1)
            attack = message.author
            try:
                defense = message.mentions[0]
            except IndexError:
                await message.channel.send("You didn't mention anyone in your message. Please try again.")
                return
            if 1 in range(len(args)):
                location = args[1]
            else:
                location = None
            embed.add_field(name='Defender', value=defense, inline=True)
            embed.add_field(name='Attacker', value=attack, inline=True)
            if location is not None:
                embed.add_field(name='Location', value=location, inline=True)
            else:
                embed.add_field(name='Location', value='*Not Specified*', inline=True)
            await defense.send(f'You are being attacked by {attack}! Respond with a number between `1` and `1000`.')
            await message.channel.send(f'Attack has started on {defense}')

            def is_num_def(m):
                try:
                    return m.author == defense and 1 <= int(
                        m.content) <= 1000 and m.channel.type is discord.ChannelType.private
                except ValueError:
                    return False

            try:
                defnumber = await self.wait_for('message', check=is_num_def, timeout=43200)
            except asyncio.TimeoutError:
                await defense.send('12 hours have passed and no response. Battle is an auto defeat!')
                embed.add_field(name='Defensive Number', value='*None*', inline=True)
                embed.add_field(name='Attacking Number', value='*None*', inline=True)
                embed.add_field(name='Difference', value='Attackers auto-win', inline=True)
                await logChannel.send(embed=embed)
                return

            await attack.send(f'{defense} has submitted their number. Reply with a number between `1` and `1000`.')

            def is_num_off(m):
                try:
                    return m.author == attack and 1 <= int(
                        m.content) <= 1000 and m.channel.type is discord.ChannelType.private
                except ValueError:
                    return False

            try:
                attnumber = await self.wait_for('message', check=is_num_off, timeout=43200)
            except asyncio.TimeoutError:
                await attack.send('12 hours have passed and no response. Battle is an auto defeat!')
                embed.add_field(name='Defensive Number', value=defnumber, inline=True)
                embed.add_field(name='Attacking Number', value='*None*', inline=True)
                embed.add_field(name='Difference', value='Defenders auto-win', inline=True)
                await logChannel.send(embed=embed)
                return

            diff = abs(int(attnumber.content) - int(defnumber.content))
            if diff > 500:
                diff = 1000 - diff
            embed.add_field(name='Defensive Number', value=defnumber.content, inline=True)
            embed.add_field(name='Attacking Number', value=attnumber.content, inline=True)
            embed.add_field(name='Difference', value=str(diff), inline=True)
            await logChannel.send(embed=embed)


client = Bot(intents=intents)
client.run(token)

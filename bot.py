# IMPORT
import discord
from discord.ext import commands
from discord.ext.commands import BucketType, cooldown, CommandOnCooldown
import json
import os
import random

# INIT

client = commands.Bot(command_prefix = '.')

client.remove_command('help')

os.chdir("Your file location")


@client.event
async def on_ready():
	await client.change_presence(status=discord.Status.idle, activity = discord.Game(".help"))
	print('Bot is ready!')  # Bot ready
	print("Logged in as")
	print(client.user.name)
	print(client.user.id)
	print("-----------------")
	print("")


@client.event
async def on_command_error(ctx, error):
	if isinstance(error, CommandOnCooldown):
		await ctx.send(f"The command is on cooldown, wait for {error.retry_after:.2f}s")
	else:
		raise error

@client.command(aliases=['ba'])
async def balance(ctx):
	await open_account(ctx.author)

	user = ctx.author

	users = await bank_data()

	bank = users[str(user.id)]["bank"]

	em = discord.Embed(title = f"{ctx.author.name}'s balance", color = discord.Color.red())
	em.add_field(name = "Coins", value = bank)
	await ctx.send(embed = em)


async def open_account(user):
	users = await bank_data()

	if str(user.id) in users:
		return False
	else:
		users[str(user.id)] = {}
		users[str(user.id)]["bank"] = 0

	with open("bank.json", "w") as f:
		json.dump(users, f)
	return True


async def bank_data():
	with open("bank.json", "r") as f:
		users = json.load(f)

	return users


async def update_bank(user, change = 0, mode = 'bank'):
	users = await bank_data()

	users[str(user.id)][mode] += change

	with open("bank.json", "w") as f:
		json.dump(users, f)

	bal = users[str(user.id)]["bank"]
	return bal

@client.command(aliases=['bg'])
@cooldown(1, 300, BucketType.user)
async def beg(ctx):
	await open_account(ctx.author)

	user = ctx.author

	users = await bank_data()

	earnings = random.randrange(100)

	await ctx.send(f"You got {earnings} coins!")

	users[str(user.id)]["bank"] += earnings

	with open("bank.json", "w") as f:
		json.dump(users, f)


@client.command(aliases=['s'])
@cooldown(1, 600, BucketType.user)
async def steal(ctx, member:discord.Member, amount = 0):
	await open_account(ctx.author)
	await open_account(member)

	bal = await update_bank(ctx.author)

	amount = int(amount)

	if amount > 100:
		await ctx.send("Maximal must be 100")
		return
	if amount < 0:
		await ctx.send("Amount must be positive!")
		return
	if amount == 0:
		await ctx.send("Please enter a number")
		return

	await update_bank(member, -1 * amount, "bank")
	await update_bank(ctx.author, amount, "bank") 
	await ctx.send(f"You stole {amount} coin from {member.mention}")
	

@client.command(aliases=['g'])
async def give(ctx, member:discord.Member, amount = None):
	await open_account(ctx.author)
	await open_account(member)

	bal = await update_bank(ctx.author)
	member_amt = await update_bank(member)

	amount = int(amount)

	if amount > 100:
		await ctx.send("Maximal must be 100")
		return
	if amount < 0:
		await ctx.send("Amount must be positive!")
		return
	if amount == None:
		await ctx.send("Please enter a number")
		return

	await update_bank(ctx.author, -1 * amount, "bank")
	await update_bank(member, amount, "bank")
	await ctx.send(f"You give {amount} coin to {member.mention}")


@client.command(aliases=['bt'])
@cooldown(1, 60, BucketType.user)
async def bet(ctx, amount = None):
	await open_account(ctx.author)

	amount = int(amount)

	if amount == None:
		await ctx.send("Please enter a number")
		return
	if amount < 0:
		await ctx.send("Amount must be positive")
		return

	final = []
	
	for i in range(2):
		a = random.choice(["X", "O"])

		final.append(a)

	await ctx.send(str(final))

	if "O" in final:
		await update_bank(ctx.author, -1*2*amount)
		await ctx.send(f"You lose {amount*2}")
	else:
		await update_bank(ctx.author, 1*2*amount)
		await ctx.send(f"You win {amount*2}")


@client.command(aliases = ["top"])
async def leaderboard(ctx, x = 3):
	users = await bank_data()
	leader_board = {}
	total = []

	for user in users:
		name = int(user)
		total_amount = users[user]["bank"]
		leader_board[total_amount] = name
		total.append(total_amount)

	total = sorted(total, reverse = True)

	em = discord.Embed(title = f"Leaderboard")
	index = 1
	for amt in total:
		id_ = leader_board[amt]
		member = await client.fetch_user(id_)
		name = member.name
		em.add_field(name = f"{index}. {name}", value = f"{amt}", inline = False)
		if index == x:
			break
		else:
			index += 1
	await ctx.send(embed = em)

@client.command(pass_context=True)
async def help(ctx):
	embed = discord.Embed(
			title = 'ᅠᅠ',
			colour = discord.Colour.blue()
		)

	embed.set_author(name='Coins Bot', icon_url='https://cdn.discordapp.com/app-icons/775545732446158860/cd990ba1e1c5f3bf8d9151cd4690b5b2.png?size=512')
	embed.add_field(name='.balance', value='Your balance', inline=False)
	embed.add_field(name='.beg', value='Beg for coins in the street', inline=False)
	embed.add_field(name='.steal', value='Steal someone coins', inline=False)
	embed.add_field(name='.give', value='Give someone money', inline=False)
	embed.add_field(name='.leaderboard', value='Leaderboard', inline=False)
	embed.add_field(name='.bet', value='Get 2x more coins', inline=False)

	await ctx.send(embed=embed)


client.run('Your token')   # token here

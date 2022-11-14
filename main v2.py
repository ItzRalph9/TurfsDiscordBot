import discord
from discord.ext import commands
from discord.ext.commands import Bot
import os
import json

intents = discord.Intents.default()
intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None, activity=discord.Game(name="Hacking the matrix"))

@bot.event
async def on_ready():
    print("connected!")

@bot.command(pass_context=True)
async def help(ctx):
    if not ctx.channel.name == "turfs":
        return
    await ctx.channel.send("This bot will keep track of the amount of money you have earned. For the bot to keep track of your turf, it needs:" +
    "\n1. a screenshot of the turf\n2. the value of the turf (800k or 1m)\n3. (optional) The people who you did the turf with, tagged in the message. " +
    "**If you don't tag anyone, the bot will use your name**\nAnd thats it, if you follow these steps when posting a turf screenshot, the bot will keep track of " +
    "the amount of money you have earned.\nExample of how you would use the bot: \n'Picture here' 800k @Ralph\n\nTo check how much money you have earned in total, type: " +
    "**!money** and it will show you the money earned.\nYou can also tag people (so !money @yourname) to check how much they've earned\nif you want to revert the previous save, " +
    "type **!undo**. This command will revert the money added by last sent turf **You can only do !undo once!**\nYou can do !undo again after a new turf has been sent in!")

def AddNewUser(gang_name, gang_id, name, id):
    file_path = f"data/{gang_name} - {gang_id}/{gang_name} - {gang_id}.json"
    with open(f"{file_path}") as json_file:
        data = json.load(json_file)
        data_to_write = {"name" : f"{name}", "money" : 0, "turfs" : 0, "mentions" : {}}
        data[f"{id}"] = data_to_write

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def IdInFile(user_id, gang_name, gang_id):
    file_path = f"data/{gang_name} - {gang_id}/{gang_name} - {gang_id}.json"
    with open(f"{file_path}", "r") as json_file:
        data = json.load(json_file)
        for id in data:
            if int(id) == int(user_id):
                return True
        else:
            return False

def CheckPaths(ctx):
    server_name = ctx.guild.name
    server_id = ctx.guild.id
    folder_name = f"{server_name} - {server_id}"
    file_name = f"data/{folder_name}/{server_name} - {server_id}.json"
    undofile_name = f"data/{folder_name}/undo - {server_name} - {server_id}.json"
    if not os.path.exists(f"data/{folder_name}"):
        print("Made server folder!")
        os.mkdir(f"data/{folder_name}")
    if not os.path.exists(file_name):
        print("File doesn't exist yet! I'll create one right now!")
        with open(f"{file_name}", "w") as f:
            f.write("{\n\n}")
    if not os.path.exists(undofile_name):
        print("Undo file doesn't exist yet! I'll create one right now!")
        with open(f"{undofile_name}", "w") as f:
            f.write("{\n\n}")

def UpdateUndoFile(ctx):
    GetFileName(ctx)
    GetFileNameUndo(ctx)
    server_name = ctx.guild.name
    server_id = ctx.guild.id
    folder_name = f"{server_name} - {server_id}"
    file_name = f"data\\{folder_name}\{server_name} - {server_id}.json"
    undo_file_name = f"data\\{folder_name}\\undo - {server_name} - {server_id}.json"
    copy_command = str(f'copy "{file_name}" "{undo_file_name}"') # CHANGE "copy" TO "cp" IN LINUX IF IT SAYS LIKE SH: CAN'T COPY FILE
    os.system(copy_command)

def UpdateValues(id, name, mentions, turf_value, amount_of_people, data, ctx):
    # Add money
    money_to_add = int(turf_value / amount_of_people)
    data[f"{id}"]["money"] += money_to_add

    # Add one Turf
    data[f"{id}"]["turfs"] += 1

    # Add mentioned people
    # Only does this if the amount of people is 0 or the tagged persons id is the same as the authors id
    # Otherwise it is useless to add mentions, because there were none
    if not mentions == []:
        if len(mentions) == 1 and mentions[0] == id:
            pass
        else:
            for name in mentions:
                if str(name) in data[f"{id}"]["mentions"]:
                    data[f"{id}"]["mentions"][f"{name}"] += 1
                else:
                    data[f"{id}"]["mentions"][f"{name}"] = 1  

    return data

def GetFileName(ctx):
    server_name = ctx.guild.name
    server_id = ctx.guild.id
    folder_name = f"{server_name} - {server_id}"
    file_name = f"data/{folder_name}/{server_name} - {server_id}.json"
    CheckPaths(ctx)
    return file_name

def GetFileNameUndo(ctx):
    server_name = ctx.guild.name
    server_id = ctx.guild.id
    folder_name = f"{server_name} - {server_id}"
    file_name = f"data/{folder_name}/undo - {server_name} - {server_id}.json"
    CheckPaths(ctx)
    return file_name

def GetUserData(server_name, server_id, id):
    file_path = f"data/{server_name} - {server_id}/{server_name} - {server_id}.json"
    with open(f"{file_path}", "r") as json_file:
        data = json.load(json_file)
    if id in data:
        money = int(data[f"{id}"]["money"])
        turfs = int(data[f"{id}"]["turfs"])
        return money, turfs
    else:
        return 0, 0

def GetTotalMoney(ctx):
    file_path = GetFileName(ctx)
    with open(f"{file_path}", "r") as json_file:
        data = json.load(json_file)
    total_money = 0
    for id in data:
        value = int(data[f"{id}"]["money"])
        total_money += value
    return total_money

def ClearStats(gang_name, gang_id, id):
    if IdInFile(id, gang_name, gang_id) == False:
        return

    file_path = f"data/{gang_name} - {gang_id}/{gang_name} - {gang_id}.json"
    with open(f"{file_path}", "r") as json_file:
        data = json.load(json_file)

    data[f"{id}"]["money"] = 0
    data[f"{id}"]["turfs"] = 0

    with open(f"{file_path}", "w") as json_file:
        data = json.dump(data, json_file, indent=4)

def UndoSave(ctx):
    file_path = GetFileName(ctx)
    undo_file_path = GetFileNameUndo(ctx)
    with open(undo_file_path, "r") as f_UndoData:
        text = f_UndoData.read()
    with open(file_path, "w") as f_Data:
        f_Data.write(text)
    print("Reverted last save!")

async def GetName(id):
    # to get id of user who sent the message:
    # id = ctx.message.author.id
    name = str(await bot.fetch_user(id))
    # Removes the '#1234' from the name so that it looks better
    return name[:-5]

@bot.command(pass_context=True)
async def reset_data(ctx):
    await ctx.channel.send("Are you sure? yes or no")
    msg = await bot.wait_for("message", check=lambda m:m.author==ctx.author and m.channel.id==ctx.channel.id)
    if msg.content.lower() in ("y", "yes"):
        # Gets all the people tagged in the message
        server_name = ctx.guild.name
        server_id = ctx.guild.id
        members = ctx.message.mentions
        ids = []
        for member in members:
            # Appends the users name and id to the list
            ids.append(member.id)
        if ids == []:
            id = ctx.message.author.id
            ClearStats(server_name, server_id, id)
            name = await GetName(id) 
            await ctx.channel.send(f"Deleted {name}'s turfs!")
        else:
            for id in ids:
                try:
                    ClearStats(server_name, server_id, id)
                    name = await GetName(id)
                    await ctx.channel.send(f"Deleted {name}'s turfs!")
                except:
                    await ctx.channel.send("Couldn't reset {name}'s data!")

check_message = True
@bot.command(pass_context=True)
async def undo(ctx):
    if not ctx.channel.name == "turfs":
        return
    await ctx.channel.send("Are you sure? yes or no")
    msg = await bot.wait_for("message", check=lambda m:m.author==ctx.author and m.channel.id==ctx.channel.id)
    global check_message
    check_message = False
    if msg.content.lower() in ("y", "yes"):
        UndoSave(ctx)
        check_message = True
    else:
        await ctx.channel.send("Didn't revert last save!")
    check_message = True

@bot.command(pass_context=True)
async def mentions(ctx):
    file_path = GetFileName(ctx)
    with open(f"{file_path}", "r") as json_file:
        data = json.load(json_file)

    id = ctx.message.author.id
    for mentioned_id in (path := data[f"{id}"]["mentions"]):
        mentioned_times = path[f"{mentioned_id}"]
        name = await GetName(mentioned_id)
        await ctx.channel.send(f"You did turfs with {name}: {mentioned_times} times")

@bot.command(pass_context=True)
@commands.has_role("owner")
async def clear_chat(ctx):
    if not ctx.channel.name == "turfs":
        return
    await ctx.channel.send("Are you sure you want to delete all the messages? yes or no")
    msg = await bot.wait_for("message", check=lambda m:m.author==ctx.author and m.channel.id==ctx.channel.id)
    if msg.content.lower() in ("y", "yes"):
        # This deletes all the messages in the channel
        await ctx.channel.purge()
        await ctx.channel.send("**Removed all messages!!**")
    else:
        await ctx.channel.send("Didn't remove all messages!")

@bot.command(pass_context=True)
async def totalmoney(ctx):
    total = GetTotalMoney(ctx)
    await ctx.channel.send(f"The gang earned ${f'{total:,}'} in total this week") 

def NameLayoutMentions(names):
    return ''.join([f"{name}" if cnt == len(names) - 1 else f"{name}, " for cnt, name in enumerate(names)])

# when user type !money it will return them the total money he has earned
@bot.command(pass_context=True)
async def money(ctx):
    if not ctx.channel.name == "turfs":
        return
    if len(ctx.message.mentions) == 0:
        ids = [str(ctx.message.author.id)]
    else:
        ids = []
        count = 0
        for id in ctx.message.mentions:
            ids.append(str(ctx.message.mentions[count].id))
            count += 1
    server_name = ctx.guild.name
    server_id = ctx.guild.id
    for id in ids:
        money = GetUserData(server_name, server_id, id)[0]
        turfs = GetUserData(server_name, server_id, id)[1]
        name = await GetName(id)
        if money == 0:
            await ctx.channel.send(f"{name}, you have done no turfs! Step up yo game goofy!")
        else:
            await ctx.channel.send(f"{name}, you did {turfs} turfs and earned ${f'{money:,}'}!")

@bot.event
async def on_message(message):
    if not message.channel.name == "turfs":
        await bot.process_commands(message)
        return
    if not check_message:
        await bot.process_commands(message)
        return
    # Makes sure that the message is not sent by the bot self
    if message.author.id == bot.user.id:
        await bot.process_commands(message)
        return
    try:
        if (message.content)[0] == "!":
            await bot.process_commands(message)
            return
    except:
        pass
    if "yes" in message.content.lower() or "no" in message.content.lower():
        await bot.process_commands(message)
        return
    # Checks if the message contains an attachment
    if not message.attachments: 
        await message.channel.send("Turf **not saved!**\nYou need the screenshot of the turf in your message!")
        await bot.process_commands(message)
        return
    if "800" in message.content.lower() or "800000" in message.content.lower() or "800.000" in message.content.lower() or "800,000" in message.content.lower():
        turf_value = 800000
        turf_value_for_message = "800,000"
    elif "1m" in message.content.lower() or "1000" in message.content.lower() or "1000000" in message.content.lower() or "1.000.000" in message.content.lower() or "1,000,000" in message.content.lower():
        turf_value = 1000000
        turf_value_for_message = "1,000,000"
    else:
        await message.channel.send("Turf **not saved!**\nYou have to mention the value of the turf (800k or 1m) in your message!")
        await bot.process_commands(message)
        return

    # Gets all the people tagged in the message
    members = message.mentions
    ids = []
    for member in members:
        # Appends the users name and id to the list
        ids.append(member.id)
    if ids == []:
        server_name = message.guild.name
        server_id = message.guild.id
        id = message.author.id
        name = await GetName(id)
        temp = []
        amount_of_people = 1
        file_path = GetFileName(message)

        UpdateUndoFile(message)
        CheckPaths(message)
        if IdInFile(id, server_name, server_id) == False:
            AddNewUser(server_name, server_id, name, id)
            print(f"Added {name} to the database!")

        # get the data
        with open(f"{file_path}", "r") as json_file:
            data = json.load(json_file)

        UpdateValues(id, name, temp, turf_value, amount_of_people, data, message)

        # Write all the new data to the file
        with open(f"{file_path}", "w") as json_file:
            data = json.dump(data, json_file, indent=4)

        await message.channel.send(f"The turf has been saved!\nTurf value: **{turf_value_for_message}**\nYou didn't tag anyone, so I did it for you\ntagged people: {name}")
    else:
        server_id = message.guild.id
        server_name = message.guild.name
        file_path = GetFileName(message)

        names = []
        amount_of_people = len(ids)
        for id in ids:
            temp = [id for id in ids]
            temp.remove(id)
            name = await GetName(id)
            names.append(name)

            UpdateUndoFile(message)
            CheckPaths(message)
            if IdInFile(id, server_name, server_id) == False:
                AddNewUser(server_name, server_id, name, id)
                print(f"Added {name} to the database!")

            # get the data
            with open(f"{file_path}", "r") as json_file:
                data = json.load(json_file)

            data = UpdateValues(id, name, temp, turf_value, amount_of_people, data, message)
            # IF MULTIPLE PEOPLE NOT IN FILE. IT WONT ADD THE MENTIONS TO ALL THE NEW PEOPLE
        names = NameLayoutMentions(names)

        # Write all the new data to the file
        with open(f"{file_path}", "w") as json_file:
            data = json.dump(data, json_file, indent=4)

        await message.channel.send(f"The turf has been saved!\nTurf value: **{turf_value_for_message}**\nYou tagged **{len(ids)}** people: {names}")

# Token for LinuxBot
LinuxBot_token = "No"
# Token for Auto Turf Bot
AutoTurfBot_token = "Just no"

bot.run(LinuxBot_token)
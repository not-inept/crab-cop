from crabigator.wanikani import WaniKani
import asyncio
import discord
import shelve
import yaml

registrants = shelve.open("registrants.shelf")
channels = shelve.open("channels.shelf")
users = shelve.open("users.shelf")

def totalVocab(srs):
    return srs.apprentice.vocabulary + srs.burned.vocabulary + srs.enlighten.vocabulary + srs.guru.vocabulary + srs.master.vocabulary

def loadChannels():
    client.get_channel
    client.get_user_info

def registerWithChannel(channel_id, user_id):
        channel = []
        if channel_id in channels:
            channel = channels[channel_id]
        if user_id not in channel:
            user = users[user_id]
            channel.append(user_id)
            channels[channel_id] = channel
            user["channels"].append(channel_id)
            users[user_id] = user

def registerUser(user_obj, token):
    user = {
        "mention": user_obj.mention,
        "token": token,
        "channels": [],
        "data": {}
    }
    users[user_obj.id] = user

config = yaml.load(open("config.yml"))

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.content.startswith("!wani"):
        response = ""
        if message.channel.id in channels:
            channel = channels[message.channel.id]
            for user_id in channel:
                user = users[user_id]
                wc = WaniKani(user["token"])
                info = wc.user_information
                prog = wc.level_progression
                stud = wc.study_queue
                srs = wc.srs_distribution
                response += "**%s** is level %d with:" % (user["mention"], info.level)
                response += "\n\t%d/%d radicals\t(%.1f)" % (prog.radicals_progress, prog.radicals_total, (prog.radicals_progress/prog.radicals_total)*100)
                response += "\n\t%d/%d kanji\t(%.1f)" % (prog.kanji_progress, prog.kanji_total, (prog.kanji_progress/prog.kanji_total)*100)
                response += "\n\t%d vocab words seen" % totalVocab(srs)
                response += "\n\tlessons available: %d" % stud.lessons_available
                response += "\n\treviews available: %d" % stud.reviews_available
            await client.send_message(message.channel, response)
    elif message.content.startswith("!register"):
        if message.author.id in users:
            registerWithChannel(message.channel.id, message.author.id)
            await client.send_message(message.channel, "You're now registered for this channel. Thanks!")
            await client.send_message(message.author, "You're able to update your token by messaging me with `!token <api v1 token>` again.")
        else:
            response = await client.send_message(message.channel, 
            "Please finish your registration by responding to the private message I'm about to send you.")
            registrants[message.author.id] = (message.author, message.channel, response)
            await client.send_message(message.author, "Please respond with `!token <api v1 token>` to add your WaniKani token to my list. You can your token at: https://www.wanikani.com/settings/account")
            await client.edit_message(response, "Please finish your registration by responding to the private message I just sent you.")
    elif message.content.startswith("!token") and message.channel.is_private:
        # validate argument exists (api token)
        split_content = message.content.split(" ")
        if len(split_content) != 2:
            await client.send_message(message.channel, "Make you sure you pass a token like: `!token <api v1 token>`")
            return
        token = split_content[1]

        if message.author.id in registrants:
            response = await client.send_message(message.channel, "Thanks, I'm storing your information...")
            registrant = registrants[message.author.id]
            registerUser(message.author, token)
            registerWithChannel(registrant[1].id, registrant[0].id)
            await client.edit_message(response, "You're all registered!")
            await client.edit_message(registrant[2], "Thanks for registering!")
            await client.send_message(message.author, "You're able to update your token by messaging me with `!token <api v1 token>` again.")
            del registrants[message.author.id]
        elif message.author.id in users:
            response = await client.send_message(message.channel, "Thanks, I'm updating your token...")
            user = users[message.author.id]
            user["token"] = token
            users[message.author.id] = user
            await client.edit_message(response, "Your token was updated!")

    # Add a thread that checks automatically and says nice things if stuff improves

client.run(config["token"])

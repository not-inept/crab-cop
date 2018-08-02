import discord
import asyncio
import yaml

registrants = {}
channels = {}


class Registrant:
    def Registrant(self, token):
        self.token = token

def totalVocab(srs):
    return srs.apprentice.vocabulary + srs.burned.vocabulary + srs.enlighten.vocabulary + srs.guru.vocabulary + srs.master.vocabulary

def loadChannels():
    client.get_channel
    client.get_user_info  

from crabigator.wanikani import WaniKani

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
        for user in config["users"]:
            wc = WaniKani(user["key"])
            info = wc.user_information
            prog = wc.level_progression
            stud = wc.study_queue
            srs = wc.srs_distribution
            response += "**%s** is level %d with:" % (user["name"], info.level)
            response += "\n\t%d/%d radicals\t(%.1f)" % (prog.radicals_progress, prog.radicals_total, (prog.radicals_progress/prog.radicals_total)*100)
            response += "\n\t%d/%d kanji\t(%.1f)" % (prog.kanji_progress, prog.kanji_total, (prog.kanji_progress/prog.kanji_total)*100)
            response += "\n\t%d vocab words seen" % totalVocab(srs)
            response += "\n\tlessons available: %d" % stud.lessons_available
            response += "\n\treviews available: %d" % stud.reviews_available
        await client.send_message(message.channel, response)
    elif message.content.startswith("!register"):
        response = await client.send_message(message.channel, 
        "Please finish your registration by responding to the private message I'm about to send you.")
        registrants[message.author.id] = (message.author, message.channel, response)
        await client.send_message(message.author, "Please respond with `!token <api v1 token>` to add your WaniKani token to my list. You can your token at: https://www.wanikani.com/settings/account")
        await client.edit_message(response, "Please finish your registration by responding to the private message I just sent you.")
    elif message.content.startswith("!token") and message.channel.is_private and message.author.id in registrants:
        # validate argument exists (api token)
        split_content = message.content.split(" ")
        if len(split_content) != 2:
            await client.send_message(message.channel, "Make you sure you pass a token like: `!token <api v1 token>`")
            return
        token = split_content[1]

        # validate api token works
        response = await client.send_message(message.channel, "Thanks, I'm storing your information...")
        registrant = registrants[message.author.id]
        channel = channels.setdefault(registrant[1].id, {})
        # save user data for later

        channel[registrant[0]] = (registrant[0], token)

        # add channel to global channels list?
        await client.edit_message(response, "You're all registered!")
        await client.edit_message(registrant[2], "Thanks for registering!")

    # Add register method-- add a user to the list of users to track, store:
    # -- unique discord ID
    # -- channel registered in
    # -- api token
    
    # Add a thread that checks automatically and says nice things if stuff improves

client.run(config["token"])

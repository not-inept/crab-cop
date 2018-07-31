import discord
import asyncio
import yaml

def totalVocab(srs):
    return srs.apprentice.vocabulary + srs.burned.vocabulary + srs.enlighten.vocabulary + srs.guru.vocabulary + srs.master.vocabulary
    

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
    if message.content.startswith('!test'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1

        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')
    elif message.content.startswith("!wani"):
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

client.run(config["token"])

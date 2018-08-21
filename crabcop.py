from datetime import datetime, timedelta
from wanikani import WaniKani
import asyncio
import discord
import logging
import shelve
import yaml

# Init logger
logger = logging.getLogger('crabcop')
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler('crabcop.log')
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s>\t%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Load shelves
registrants = shelve.open('registrants.shelf')
channels = shelve.open('channels.shelf')
users = shelve.open('users.shelf')

def rankKeyFunction(user):
    return (user['reviews_done_past_day'], user['current_level'])

def buildResponse(user, current_level, reviews_done_past_day, stats, lessons_available, reviews_available, reviews_available_next_day):
    logger.debug('Building response.')
    response = ''
    response += '**%s** is level %d:' % (user['mention'], current_level)
    response += '\n\tThey\'ve done %d reviews in the last day.' % reviews_done_past_day
    response += '\n\t%d/%d radicals\t(%.1f)' % (stats['radical']['passed'], stats['radical']['total'], (stats['radical']['passed']/stats['radical']['total'])*100)
    response += '\n\t%d/%d kanji\t(%.1f)' % (stats['kanji']['passed'], stats['kanji']['total'], (stats['kanji']['passed']/stats['kanji']['total'])*100)
    response += '\n\t%d/%d vocab\t(%.1f)' % (stats['vocabulary']['passed'], stats['vocabulary']['total'], (stats['vocabulary']['passed']/stats['vocabulary']['total'])*100)
    response += '\n\tlessons available: %d' % lessons_available
    response += '\n\treviews available: %d' % reviews_available
    response += '\n\treviews in the next day: %d' % reviews_available_next_day
    return response

def registerWithChannel(channel_id, user_id):
        channel = []
        if channel_id in channels:
            channel = channels[channel_id]
        if user_id not in channel:
            user = users[user_id]
            channel.append(user_id)
            channels[channel_id] = channel
            user['channels'].append(channel_id)
            users[user_id] = user

def registerUser(user_obj, token):
    user = {
        'mention': user_obj.mention,
        'token': token,
        'channels': [],
        'data': {}
    }
    users[str(user_obj.id)] = user

config = yaml.load(open('config.yml'))

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    author_id = str(message.author.id)
    channel_id = str(message.channel.id)
    if message.content.startswith('!wani'):
        if channel_id in channels:
            start_time = datetime.now()
            logger.debug('!wani starting at %s.' % start_time.isoformat())
            channel = channels[channel_id]
            one_day_ago = datetime.now() - timedelta(hours = 24)
            responses = []
            for user_id in channel:
                user = users[user_id]
                wk = WaniKani(user['token'])
                # Get user profile
                wk_user = wk.get_user()
                current_level = wk_user['data']['level']
                # Get progress summary
                summary = wk.get_summary()
                reviews_available = len(summary['data']['reviews'][0]['subject_ids'])
                reviews_available_next_day = 0
                for review in summary['data']['reviews']:
                    reviews_available_next_day += len(review['subject_ids'])
                lessons_available = len(summary['data']['lessons'][0]['subject_ids'])
                # Get review stats
                reviews = wk.get_reviews(filters={'updated_after':one_day_ago.isoformat()})
                reviews_done_past_day = reviews['total_count']
                # Get level assignment stats
                assignments = wk.get_assignments(filters={'levels': current_level})
                stats = {
                    'kanji' : {
                        'passed':0.0,
                        'total':0.0
                    },
                    'radical' : {
                        'passed':0.0,
                        'total':0.0
                    },
                    'vocabulary' : {
                        'passed':0.0,
                        'total': 0.0
                    }
                }
                for assignment in assignments['data']:
                    data = assignment['data']
                    if data['passed']:
                        stats[data['subject_type']]['passed'] += 1
                    stats[data['subject_type']]['total'] += 1

                responses.append({
                    'current_level': current_level,
                    'reviews_done_past_day': reviews_done_past_day,
                    'response': buildResponse(user, current_level, reviews_done_past_day, stats, lessons_available, reviews_available, reviews_available_next_day)
                })
            responses = sorted(responses, key=rankKeyFunction, reverse=True)
            await message.channel.send('\n' + '\n'.join([str(i+1) + '. ' + responses[i]['response'] for i in range(len(responses))]))
            end_time = datetime.now()
            logger.debug('!wani stopping at %s.' % end_time.isoformat())
            logger.debug('!wani took %s' % str(end_time - start_time))

    elif message.content.startswith('!register'):
        if author_id in users:
            registerWithChannel(channel_id, author_id)
            await message.channel.send('You\'re now registered for this channel. Thanks!')
            await message.author.send('You\'re able to update your token by messaging me with `!token <api v2 token>` again.')
        else:
            response = await message.channel.send(
            'Please finish your registration by responding to the private message I\'m about to send you.')
            registrants[author_id] = (author_id, channel_id, message.channel.id, response.id)
            await message.author.send('Please respond with `!token <api v2 token>` to add your WaniKani token to my list. You can your token at: https://www.wanikani.com/settings/account')
            await response.edit(content='Please finish your registration by responding to the private message I just sent you.')
    elif message.content.startswith('!token') and isinstance(message.channel, discord.abc.PrivateChannel):
        # validate argument exists (api token)
        split_content = message.content.split(' ')
        if len(split_content) != 2:
            await message.channel.send('Make you sure you pass a token like: `!token <api v2 token>`')
            return
        token = split_content[1]

        if author_id in registrants:
            response = await message.channel.send('Thanks, I\'m storing your information...')
            registrant = registrants[author_id]
            registerUser(message.author, token)
            registerWithChannel(registrant[1], registrant[0])
            await response.edit(content='You\'re all registered!')
            original_channel = client.get_channel(registrant[2])
            original_response = await original_channel.get_message(registrant[3])
            await original_response.edit(content='Thanks for registering!')
            await message.author.send('You\'re able to update your token by messaging me with `!token <api v2 token>` again.')
            del registrants[author_id]
        elif author_id in users:
            response = await message.channel.send('Thanks, I\'m updating your token...')
            user = users[author_id]
            user['token'] = token
            users[author_id] = user
            await response.edit(content='Your token was updated!')
    # Add a thread that checks automatically and says nice things if stuff improves

logger.info('Starting up :)')
client.run(config['token'])

import discord
import re
import unicodedata
from discord.ext import commands
from difflib import get_close_matches

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='-', intents=intents)

# Function to normalize text by removing accents and other diacritics
def normalize_text(text):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if unicodedata.category(c) != 'Mn'
    )

# Enhanced regular expression to match variations of the word "nigga" and similar words
censored_words = re.compile(r'\b(n[i1!]*g+[a@4]*|n[i1!]*g+g+[a@4]*|n[i1!]*g+g+[e3]*r[s]*|n[i1!]*g+g+[u@4]*[a@4]+|n[i1!]*g+g+[a@4]+h*)\w*\b', re.IGNORECASE)

# List of base words to check for close matches
base_words = ['nigga', 'nigger', 'niga']

# Function to check for close matches using difflib
def contains_close_match(text, word_list, cutoff=0.7):
    words = text.split()
    for word in words:
        matches = get_close_matches(word, word_list, n=1, cutoff=cutoff)
        if matches:
            return True
    return False

# Censor replacement text
censor_replacement = '[CENSORED]'

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Normalize the message content
    normalized_content = normalize_text(message.content)
    
    # Check if the message contains any censored words or close matches
    if censored_words.search(normalized_content) or contains_close_match(normalized_content, base_words):
        await message.delete()
        
        # Create a censored version of the message
        censored_message = censored_words.sub(censor_replacement, normalized_content)
        
        # Inform the user about the censorship
        warning_message = f"{message.author.mention}, your message was deleted bcause it contained a forbidden word."
        await message.channel.send(warning_message)
    
    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def add_censored_word(ctx, *, word):
    global censored_words, base_words
    
    # Escape special characters in the word and compile a new regex pattern
    escaped_word = re.escape(word)
    new_pattern = rf'|{escaped_word}'
    censored_words = re.compile(censored_words.pattern + new_pattern, re.IGNORECASE)
    
    # Add the word to the base words list
    base_words.append(word.lower())
    
    await ctx.send(f'Added "{word}" to the censored words list.')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def list_censored_words(ctx):
    words_list = censored_words.pattern.replace(r'\b(', '').replace(r')\b', '').replace('|', ', ')
    await ctx.send(f'Censored words list: {words_list}')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def remove_censored_word(ctx, *, word):
    global censored_words, base_words
    
    # Escape special characters in the word and compile a new regex pattern without the word
    escaped_word = re.escape(word)
    pattern = censored_words.pattern.replace(f'|{escaped_word}', '')
    censored_words = re.compile(pattern, re.IGNORECASE)
    
    # Remove the word from the base words list
    if word.lower() in base_words:
        base_words.remove(word.lower())
    
    await ctx.send(f'Removed "{word}" from the censored words list.')


# Replace 'TOKEN' with your bot's token
bot.run('Bot_Token')

import inspect
import functools
from collections import namedtuple

ArgSpec = namedtuple('ArgSpec', ['args', 'varargs', 'keywords', 'defaults'])

def getargspec(func):
    """Legacy wrapper for inspect.getfullargspec()."""
    spec = inspect.getfullargspec(func)
    return ArgSpec(
        args=spec.args,
        varargs=spec.varargs,
        keywords=spec.varkw,
        defaults=spec.defaults,
    )

inspect.getargspec = getargspec

import db
from telethon import TelegramClient
from itertools import product
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.types import PeerChannel
import pymorphy2


async def get_channel_info(channel_id_or_name, client, phone_number):
    await client.start(phone=phone_number)
    channel_id_or_name = str(channel_id_or_name)
    if channel_id_or_name.startswith("@"):
        try:
            channel = channel_id_or_name[1:]
            channel = await client.get_entity((channel_id_or_name))
            await client(JoinChannelRequest(channel))
            channel_id = f"-100{channel.id}"
            return channel_id
        except:
            return False
    else:
        try:
            channel_id_or_name = int(channel_id_or_name)
            channel = await client.get_entity(PeerChannel(channel_id_or_name))
            await client(JoinChannelRequest(channel))
            channel_username = f'@{channel.username}'
            return channel_username
        except:
            return False

async def leave_channel_listening(channel_id, client, phone_number):
    await client.start(phone=phone_number)
    
    channel_id = int(channel_id)
    channel = await client.get_entity(PeerChannel(channel_id))
    await client(LeaveChannelRequest(channel))


async def generate_all_case_forms(phrase):
    morph = pymorphy2.MorphAnalyzer()

    """Генерирует все возможные падежные формы фразы"""
    words = phrase.split()
    if not words:
        return []
    
    # Получаем все возможные варианты склонения для каждого слова
    word_variants = []
    for word in words:
        parsed = morph.parse(word)[0]  # берем первый вариант разбора
        if parsed.tag.POS in {'NOUN', 'ADJF', 'ADJS', 'PRTF', 'PRTS', 'NUMR'}:
            cases = ['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct']
            variants = []
            for case in cases:
                try:
                    inflected = parsed.inflect({case})
                    if inflected:
                        variants.append(inflected.word)
                except:
                    continue
            word_variants.append(variants if variants else [word])
        else:
            word_variants.append([word])  # для неизменяемых слов
    
    # Генерируем все возможные комбинации слов в разных падежах
    all_forms = []
    for combination in product(*word_variants):
        all_forms.append(' '.join(combination))
    
    return list(set(all_forms))  # убираем дубли
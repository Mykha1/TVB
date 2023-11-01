import os
import telebot
import speech_recognition
from pydub import AudioSegment
from telebot import TeleBot, types
from bs4 import BeautifulSoup
import requests
from parser import daily_weather

bot: TeleBot = telebot.TeleBot('6882568785:AAHBw7yRGNTa_7COC5xT4nrYbfepvfJwD_A')

user_language = {}

@bot.message_handler(commands=['start'])
def greeting(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('What can you do?', callback_data='my_skills'))
    greet_text = f"Hello, {message.from_user.first_name}! \nHow can I help you?"
    bot.send_message(message.chat.id, greet_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'my_skills')
def handle_skills(callback_query):
    text_frst = 'I can convert your voice messages into text.'
    text = 'In Prague today'
    bot.answer_callback_query(callback_query.id)
    bot.send_message(callback_query.message.chat.id, f'/trsc - <b>{text_frst}</b>. \n/weather - <b>{text}</b>', parse_mode="html")

@bot.message_handler(commands=['weather'])
def get_daily_weather(message):
    curr_weath = daily_weather()
    bot.send_message(message.chat.id, f' Today in Prague: {curr_weath}')

@bot.message_handler(commands=['trsc'])
def language_select(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('English', callback_data='en-US'))
    markup.add(types.InlineKeyboardButton('Ukrainian', callback_data='uk-UA'))
    markup.add(types.InlineKeyboardButton('Russian', callback_data='ru-RU'))
    markup.add(types.InlineKeyboardButton('Czech', callback_data='cs-CZ'))
    bot.send_message(message.chat.id, 'Please select a language', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ['en-US', 'uk-UA', 'ru-RU', 'cs-CZ'])
def language_choice(callback_query):
    selected_lng = callback_query.data
    user_language[callback_query.message.chat.id] = selected_lng
    bot.answer_callback_query(callback_query.id)
    bot.send_message(callback_query.message.chat.id, f'You have selected {selected_lng} as your language.')

@bot.message_handler(content_types=['voice'])
def transcript(message):
    user_id = message.chat.id
    if user_id in user_language:
        selected_lng = user_language[user_id]
    else:
        bot.send_message(user_id, "Please select a language. Use /trsc command.")
        return

    filename = download_file(bot, message.voice.file_id)
    text = recognize_speech(filename, selected_lng)
    bot.send_message(user_id, f'Transcription: {text}')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Change Language', callback_data='change_language'))
    bot.send_message(user_id, "Do you want to change the language?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'change_language')
def change_language(callback_query):
    user_id = callback_query.message.chat.id
    bot.send_message(user_id, "Please select a new language. Use /trsc command.")

def oga2wav(filename):
    new_filename = filename.replace('.oga', '.wav')
    audio = AudioSegment.from_file(filename)
    audio.export(new_filename, format='wav')
    return new_filename

def recognize_speech(oga_filename, selected_lng):
    wav_filename = oga2wav(oga_filename)
    recognizer = speech_recognition.Recognizer()

    with speech_recognition.AudioFile(wav_filename) as source:
        wav_audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(wav_audio, language=selected_lng)
    except speech_recognition.UnknownValueError:
        text = "Unable to recognize speech"
    except speech_recognition.RequestError:
        text = "Recognition request failed"

    if os.path.exists(oga_filename):
        os.remove(oga_filename)

    if os.path.exists(wav_filename):
        os.remove(wav_filename)

    return text

def download_file(bot, file_id):
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = file_id + file_info.file_path
    filename = filename.replace('/', '_')
    with open(filename, 'wb') as f:
        f.write(downloaded_file)
    return filename

if __name__ == "__main__":
    bot.polling()

from transformers import pipeline
import json
import telebot
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")
qa_pipeline = pipeline("question-answering")


def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def answer_question_with_photo(data, question):
    best_answer = None
    best_score = 0
    best_image = None

    for entry in data:
        context = entry['caption']
        result = qa_pipeline(question=question, context=context)
        if result['score'] > best_score:
            best_score = result['score']
            best_answer = result['answer']
            best_image = entry['image']

    if best_answer:
        return best_answer, best_image
    else:
        return "Нет соответствующего ответа."


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Этот бот связан с проектом умных очков. Вы можете отправить запрос, и бот обработает его.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    caption, photo_path = answer_question_with_photo(load_data('captions.json'), message.text)
    with open(photo_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo=photo, caption=caption)
    # bot.send_message(message.chat.id, answer_question_with_model(load_data('captions.json'), message.text))

if __name__ == "__main__":
    bot.polling(none_stop=True)

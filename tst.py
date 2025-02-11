from transformers import pipeline
import json

# Загрузка модели RoBERTa для ответов на вопросы
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

def answer_question_with_model(data, question):
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
        return f"Ответ: {best_answer}. Соответствующая фотография: {best_image}"
    else:
        return "Нет соответствующего ответа."

# Пример использования
data = [
    {
        "image": "C:\\Users\\lebed\\PycharmProjects\\AI glasses\\photos\\image_20250206_230549.jpg",
        "caption": "there is a laptop computer sitting on top of a desk next to a monitor"
    },
    {
        "image": "C:\\Users\\lebed\\PycharmProjects\\AI glasses\\photos\\image_20250206_230558.jpg",
        "caption": "there is a laptop computer sitting on top of a desk with a lot of text on the screen"
    },
    {
        "image": "C:\\Users\\lebed\\PycharmProjects\\AI glasses\\photos\\image_20250207_103947.jpg",
        "caption": "there is a blurry image of a dog and a cat in a kitchen"
    }
]

question = "What is on the desk?"
print(1)
print(answer_question_with_model(data, question))

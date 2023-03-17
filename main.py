
import os
import re
import csv
from google.cloud import vision_v1
import math
from config import GOOGLE_APPLICATION_CREDENTIALS
import urllib.parse
from tqdm import tqdm

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS


def extract_horizontal_text(response, threshold=40):
    """
    Extracts horizontal text from a Google Cloud Vision OCR response.
    :param response: Google Cloud Vision OCR response.
    :param threshold: Vertical gap threshold to determine new lines.
    :return: A string containing the extracted horizontal text.
    """
    horizontal_text = []

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                prev_word = None
                current_line = []
                for word in paragraph.words:
                    word_text = ''.join([symbol.text for symbol in word.symbols])

                    y_diff = word.bounding_box.vertices[3].y - word.bounding_box.vertices[0].y
                    x_diff = word.bounding_box.vertices[3].x - word.bounding_box.vertices[0].x

                    if x_diff == 0:
                        angle = 90
                    else:
                        angle = abs(math.degrees(math.atan(y_diff / x_diff)))

                    if 45 <= angle < 135:
                        if prev_word and word.bounding_box.vertices[0].y - prev_word.bounding_box.vertices[3].y > \
                                threshold:
                            horizontal_text.append(''.join(current_line).strip())
                            current_line = []

                        current_line.append(' ' + word_text)
                        prev_word = word

                if current_line:
                    horizontal_text.append(''.join(current_line).strip())
    return '\n'.join(horizontal_text)


def process_image(image_path, threshold=40):
    """
    Processes an image using Google Cloud Vision OCR and extracts horizontal text.
    :param image_path: Path to the image file.
    :param threshold: Vertical gap threshold to determine new lines.
    :return: A string containing the extracted horizontal text.
    """
    client = vision_v1.ImageAnnotatorClient()
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    image = vision_v1.Image(content=content)
    response = client.text_detection(image=image)
    text = extract_horizontal_text(response, threshold)
    return text


def split_questions(text):
    """
    Splits a block of text into separate lines.
    :param text: A block of text containing questions.
    :return: A list of questions.
    """
    questions = text.split('\n')
    questions = [question.strip() for question in questions if question.strip()]
    return questions


def clean_text(text):
    cleaned_text = text
    cleaned_text = re.sub(r'\d{3}\s*$', '', cleaned_text)  # Remove card number at the end of the text
    cleaned_text = cleaned_text.strip()
    return cleaned_text


def write_csv(category, qa_list):
    with open(f"trivial_pursuit_{category}.csv", mode="w", encoding="utf-8", newline="") as csv_file:
        fieldnames = ["question", "answer"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for question, answer in qa_list:
            search_keywords = f'{answer}'
            encoded_search_keywords = urllib.parse.quote(search_keywords)
            google_search_link = f'https://www.google.com/search?q={encoded_search_keywords}'

            # Combine answer and link as an HTML hyperlink
            answer_with_link = f"{answer} (<a href='{google_search_link}'>En savoir plus</a>)"

            writer.writerow({"question": question, "answer": answer_with_link})


def get_image_pairs(folder):
    """
    Get pairs of image files (question and answer) from a folder.
    :param folder: The folder containing the image files.
    :return: A list of tuples with pairs of image files.
    """
    image_files = [f for f in os.listdir(folder) if f.endswith(".jpeg") or f.endswith(".jpg") or f.endswith(".png")]
    image_files.sort()

    image_pairs = list(zip(image_files[::2], image_files[1::2]))

    return image_pairs


def main():
    folder = "Trivial_Pursuit"
    categories = [
        "Géographie", "Divertissement", "Histoire",
        "Arts_et_Littérature", "Science_et_Nature", "Sports_et_Loisirs"
    ]

    print("Récupération des paires d'images...")
    image_pairs = list(tqdm(get_image_pairs(folder)))

    print("Traitement des images...")

    qa_category = {category: [] for category in categories}

    for img_q, img_a in tqdm(image_pairs, desc="Traitement des images"):
        questions_text = process_image(os.path.join(folder, img_q))
        questions = split_questions(questions_text)

        answers_text = process_image(os.path.join(folder, img_a), threshold=60)
        answers = split_questions(answers_text)

        for i, question in enumerate(questions):
            question = clean_text(question)
            if i < len(answers):
                answer = clean_text(answers[i])
                category_index = i % len(categories)  # Utilisez le modulo par le nombre de catégories
                qa_category[categories[category_index]].append((question, answer))

    # Affiche le contenu du dictionnaire qa_category
    """for category, qa_list in qa_category.items():
        print(f"{category}:")
        for question, answer in qa_list:
            print(f"  Q: {question}")
            print(f"  A: {answer}")"""

    for category in categories:
        write_csv(category, qa_category[category])
    print("Terminé ! Les fichiers CSV ont été générés.")

if __name__ == "__main__":
    main()
# Trivial Pursuit OCR for Anki

This repository contains a Python script that utilizes Google Cloud Vision OCR to extract questions and answers from images of Trivial Pursuit cards. The script processes the images, identifies horizontal text, and extracts the questions and answers into a CSV file, specifically formatted for importing into Anki. The CSV file also includes a hyperlink to a Google search for each answer, providing users with an easy way to learn more about the topic within Anki.

## Features

- Extracts questions and answers from images of Trivial Pursuit cards
- Utilizes Google Cloud Vision OCR for image processing
- Outputs data in CSV format, ready for Anki import
- Includes a hyperlink to a Google search for each answer

## Prerequisites

1. Python 3
2. Google Cloud Vision API key
3. Install required Python packages by running: `pip install -r requirements.txt`

## Usage

1. Place your Trivial Pursuit card images in a folder, with questions and answers in separate images.
2. Set your Google Cloud Vision API key in the `config.py` file or as an environment variable.
3. Run the script using the following command:

`python main.py -d DIRECTORY`


Replace `DIRECTORY` with the path to the folder containing your Trivial Pursuit card images.

4. The script will process the images and generate a CSV file with the extracted questions, answers, and hyperlinks, ready for importing into Anki.

## Dependencies

- Python 3
- Google Cloud Vision API

Please refer to the [Google Cloud Vision API documentation](https://cloud.google.com/vision/docs/setup) for detailed setup and usage instructions.

## Note

This repository and script are designed for educational purposes and personal use only. The extracted Trivial Pursuit content is copyrighted and should not be used for commercial purposes without proper licensing.

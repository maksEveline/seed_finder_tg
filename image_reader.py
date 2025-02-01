import easyocr


def extract_text(image_path: str) -> str:
    """
    Извлекает текст из изображения с использованием EasyOCR.

    :param image_path: Путь к файлу изображения.
    :return: Распознанный текст.
    """
    reader = easyocr.Reader(["ru", "en"])
    results = reader.readtext(image_path, detail=0)
    return " ".join(results)


# if __name__ == "__main__":
#     text = extract_text("img1.jpg")
#     print(f"\n\ntext: {text}")

import requests


def extract_text(image_path: str) -> str:
    def extract_text_from_api(lst):
        return " ".join(item["text"] for item in lst)

    api_url = "https://api.api-ninjas.com/v1/imagetotext"
    image_file_descriptor = open(image_path, "rb")
    files = {"image": image_file_descriptor}
    r = requests.post(api_url, files=files, headers={"X-Api-Key": "YOUR_API_KEY"})
    return extract_text_from_api(r.json())


# if __name__ == "__main__":
#     print(extract_text("405.jpg"))

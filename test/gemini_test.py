import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from gemini import _describe_image, generate_rizz

def test_describe_image():
    url = "https://instagram.fphl1-1.fna.fbcdn.net/v/t51.2885-15/485067168_18512192929008508_1371499067344772488_n.jpg?stp=dst-jpg_e35_s1080x1080_sh0.08_tt6&_nc_ht=instagram.fphl1-1.fna.fbcdn.net&_nc_cat=1&_nc_oc=Q6cZ2QHfDdt2gmQXKGZWgsu0AM3kWkB7FR0i62UNg74Z7zHh3SujFP9XKgIVapHeOXzlLDA&_nc_ohc=k2Jj_uOWwRUQ7kNvgEkCb1E&_nc_gid=zfCi6Rj8DV2VcmDLBgC0sA&edm=ANTKIIoBAAAA&ccb=7-5&oh=00_AYH4ydwuNgQeQhH2fG5dVy45wKqdN0hNExkKc1MtSuTjgw&oe=67E4EE2E&_nc_sid=d885a2"
    response = _describe_image(url)
    print(response)

def test_generate_rizz():
    test_chat_history = [
        {"type": "text", "sender": "user", "content": "ayyy the new Avengers movie came out!"},
        {"type": "text", "sender": "clkr", "content": "omg ya I saw!"},
        {"type": "text", "sender": "clkr", "content": "I can't wait to watch it"}
    ]
    test_relationship = "crush"
    test_draft = "let's watch it together"

    response = generate_rizz(test_relationship, test_chat_history, "user", test_draft)
    print(response)

def test_generate_rizz_advanced():
    test_chat_history = [
        {"type": "text", "sender": "user", "content": "ayyy the new Avengers movie came out!"},
        {"type": "text", "sender": "clkr", "content": "omg ya I saw!"},
        {"type": "text", "sender": "clkr", "content": "I can't wait to watch it"},
        {"type": "text", "sender": "clkr", "content": "wdy think of this?"},
        {"type": "image", "sender": "clkr", "content": "https://media.discordapp.net/attachments/646750685928488990/1353182130452041759/image.png?ex=67e0b890&is=67df6710&hm=8c83542c27265e8451e56f9c6bc692cf95e1002d531ec5bc247347557dcccfa5&=&format=webp&quality=lossless&width=518&height=474"}
    ]
    test_relationship = "crush"

    response = generate_rizz(test_relationship, test_chat_history, "user")
    print(response)

if __name__ == "__main__":
    test_generate_rizz()
    test_describe_image()
    test_generate_rizz_advanced()
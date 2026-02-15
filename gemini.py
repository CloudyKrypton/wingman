from google import genai
from google.genai import types
import requests
from PIL import Image
from io import BytesIO
from sql import exists_context, get_context, update_context

with open("apikey.txt", "r") as file:
    GEMINI_API_KEY = file.read().strip()

DRAFT_INSTRUCT = """
    You are the AI browser extension 'Wingman' that is given the user's chat history, the user's
    relationship to the recipient, and the user's draft message. Generate an improved version of the
    draft message that is interesting, engaging, and thoughtful. The generated message should be is 
    appropriate for the user's relationship with the recipient and prioritize responding to or
    expanding upon relevant and recent messages. and imitate the user's texting conventions.

    Example Input 1:
    Relationship: girlfriend
    Chat History
    clkr: i'm at the library lol
    user: okay, I'll see you there
    user: yo
    clkr: hiiii
    Draft Message: how was your day?

    Example Output 1:
    hey, how was your day? i can't wait to see you later <3

    Example Input 2:
    Relationship: co-worker
    Chat History:
    user: Hi John, are you done with the implementing the new feature?
    john: I finished a few minutes ago! I'll send you the code now.
    Draft Message: Okay, thanks! I'll review it. Then we can get lunch

    Example Output 2:
    Great, thanks for the quick turnaround! After I review it, do you want to grab lunch?

    Example Input 3:
    Relationship: friend
    Chat History:
    friend: dude, did you see the trailer for Arcane?
    user: YO hold up
    user: I'm watching it rn 
    friend: Fortiche went crazy on the animation fr
    Draft Message: yeah, it looks so good

    Example Output 3:
    the Fortiche artstyle is so clean! I'm hoping the story will be just as good
    """
NO_DRAFT_INSTRUCT = """
    You are the AI browser extension 'Wingman' that is given the user's chat history, and the user's
    relationship to the recipient. Generate a message for the user that continues the conversation
    in a way that is appropriate for the user's relationship with the recipient. The message should
    prioritize responding to or expanding upon relevant and recent messages. Your message should 
    imitate the user's texting conventions.

    Example Input 1:
    Relationship: girlfriend
    Generate a message as: alex
    Chat History:
    alex: yo bb girl, wya?
    clkr: at the library lol
    clkr: why?
    alex: are you coming to the party tonight?

    Example Output 1:
    i was hoping to see you there :p

    Example Input 2:
    Relationship: co-worker
    Generate a message as: emily
    Chat History:
    emily: Hi John, did you finish writing the docstrings?
    john: No, not yet
    john: Sorry, I've been really swamped lately.
    john: I'm not sure if I'll be able to work on it before Sunday

    Example Output 2:
    No worries. Take your time and don't overwork yourself!
    """
DESCRIBE_IMG_INSTRUCT = """
    Given an image, generate a detailed description of the image. Format the in the following manner:
    "an image depicting [description of the image]."
    """
GENERATE_HIST_INSTRUCT = """
    You are given a small snippet of a conversation between two people with no prior context.
    Generate 1-3 points for the specified person, related to facts they shared (e.g., name, 
    preferences, hobbies). The goal is to eventually build persistent memory about this person in a string.

    Example Input 1:
    Generate memory for: Alex
    Chat history:
    Alex: Hey! Are you still up for hiking this weekend?
    Jordan: Hey! Yeah, definitely. Which trail were you thinking?
    Alex: I was thinking Eagle Rock. It’s a bit challenging but the view is worth it.
    Jordan: Sounds perfect. Should we meet at 8 am at the parking lot?
    Alex: 8 am works! I’ll bring some snacks for the trail.

    Example Output 1:
    Likes hiking,
    Open to moderately challenging trails,
    Plans and brings snacks for friends

    Example Input 2:
    Generate memory for: Riley
    Chat history:
    Sam: just saw a squirrel steal a chip lol
    Riley: No way! Where?
    Sam: downtown park, right under the fountain
    Riley: That’s wild. Did it run away with it?
    Sam: yep… like a tiny furry ninja

    Example Output 2:
    Curious and responsive,
    Engages with humor and asks follow-up questions
    """
UPDATE_HIST_INSTRUCT = """
    You are given a small snippet of a conversation between two people with some points of prior context.
    Update the prior context for the specified person (keeping it at 3 points maximum), related to facts they shared 
    (e.g., name, preferences, hobbies). Prioritize specific details, such as hobbies, over more abstract
    descriptions. The goal is to eventually build persistent memory about this person in a string.

    Example Input 1:
    Update memory for: Alex
    Previous context: Likes hiking,Open to moderately challenging trails,Plans and brings snacks for friends
    Chat history:
    Alex: Tried making homemade pasta tonight. Disaster
    Jordan: Haha! What happened?
    Alex: Dough stuck to everything… even the cat almost got some.
    Jordan: Yikes! At least you tried. Did it taste okay?
    Alex: Surprisingly, yes! Just… crunchy edges and flour everywhere.

    Example Output 1:
    Likes hiking,
    Open to moderately challenging trails,
    Has a cat

    Example Input 2:
    Generate memory for: Riley
    Previous context: Curious and responsive,Engages with humor and asks follow-up questions
    Riley: finally got my hands on that new lens!
    Sam: nice
    Sam: which one did u get?
    Riley: 50mm f/1.8 can’t wait to try some night shots.

    Example Output 2:
    Curious and responsive,
    Engages with humor and asks follow-up questions
    Enjoys photography
    """

def describe_image(url: str) -> str:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = requests.get(url)

        if response.status_code == 200:
            # Open the image from the response content
            image = Image.open(BytesIO(response.content))

            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=["Give a description of this image", image],
                config=types.GenerateContentConfig(
                    system_instruction=types.Part.from_text(text=DESCRIBE_IMG_INSTRUCT),
                    temperature=1,
                    max_output_tokens=500,
                    response_mime_type="text/plain",
                    top_p=0.95,
                    top_k=40
                )
            )
            return response.text
        else:
            print("Failed to retrieve the image. Status code:", response.status_code)
    
    except Exception as e:
        return str(e)

def update_description(chat_history, my_user, other_user):
    chat_history_string = process_chat_history(chat_history)
    old_hist_exists = exists_context(my_user, other_user)
    if not old_hist_exists:
        prompt = f"Generate memory for: {other_user}\nChat History:\n{chat_history_string}"
    else:
        old_hist = get_context(my_user, other_user)
        prompt = f"Generate memory for: {other_user}\nPrevious Context: {old_hist}\nChat History:\n{chat_history_string}"
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        model_id = "gemini-3-flash-preview"
        response = client.models.generate_content(
            model=model_id,
            contents=[types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )],
            config=types.GenerateContentConfig(
                system_instruction=types.Part.from_text(
                    text=UPDATE_HIST_INSTRUCT if exists_context else GENERATE_HIST_INSTRUCT
                ),
                temperature=1.5,
                max_output_tokens=600,
                response_mime_type="text/plain",
                top_p=0.95,
                top_k=40
            )
        )
    except Exception as e:
        print("Error:", e)
        return None
    print(response.text)
    update_context(my_user, other_user, response.text)

def generate_rizz(relationship, chat_history, my_user, draft=None) -> str:
    """
    Generate a message that continues the conversation in a way that is appropriate for the user's
    relationship with the recipient. The message should consider relevant information in the chat
    history and imitate the user's texting conventions. If a draft message is provided, the generated
    message should be an improved, more engaging version of the draft message.

    Parameters:
        chat_history (list of dictionaries):
            An ordered list of messages in the chat history. Each dictionary corresponds to a
            message and has the following keys:
            - "type": The type of message, which can be "text" or "image"
            - "sender": The sender of the message.
            - "content": The message content.
        relationship (str): The user's relationship to the recipient.
    """

    chat_history_string = process_chat_history(chat_history)

    if draft:
        prompt = f"Relationship: {relationship}\nGenerate a message as: {my_user}\nChat History:\n{chat_history_string}\nDraft Message: {draft}"
    else:
        prompt = f"Relationship: {relationship}\nGenerate a message as: {my_user}\nChat History:\n{chat_history_string}"
    
    # print(prompt)

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        model_id = "gemini-3-flash-preview"
        response = client.models.generate_content(
            model=model_id,
            contents=[types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )],
            config=types.GenerateContentConfig(
                system_instruction=types.Part.from_text(
                    text=DRAFT_INSTRUCT if draft else NO_DRAFT_INSTRUCT
                ),
                temperature=1.5,
                max_output_tokens=600,
                response_mime_type="text/plain",
                top_p=0.95,
                top_k=40
            )
        )
    except Exception as e:
        print("Error:", e)
        return None
    
    return response.text

def process_chat_history(chat_history):
    # Process messages in the chat history into a prompt
    processed_messages = []
    for message in chat_history:
        if message["type"] == "image":
            description = describe_image(message['content'])
            if description:  # Only add the description if it is not empty, else ignore the link
                processed_messages.append(f"{message['sender']}: {description}")
        elif message["type"] == "text":
            processed_messages.append(f"{message['sender']}: {message['content']}")
    return '\n'.join(processed_messages)

def test_describe_image():
    url = "https://instagram.fphl1-1.fna.fbcdn.net/v/t51.2885-15/485067168_18512192929008508_1371499067344772488_n.jpg?stp=dst-jpg_e35_s1080x1080_sh0.08_tt6&_nc_ht=instagram.fphl1-1.fna.fbcdn.net&_nc_cat=1&_nc_oc=Q6cZ2QHfDdt2gmQXKGZWgsu0AM3kWkB7FR0i62UNg74Z7zHh3SujFP9XKgIVapHeOXzlLDA&_nc_ohc=k2Jj_uOWwRUQ7kNvgEkCb1E&_nc_gid=zfCi6Rj8DV2VcmDLBgC0sA&edm=ANTKIIoBAAAA&ccb=7-5&oh=00_AYH4ydwuNgQeQhH2fG5dVy45wKqdN0hNExkKc1MtSuTjgw&oe=67E4EE2E&_nc_sid=d885a2"
    response = describe_image(url)
    print(response)

def test_generate_rizz():
    test_chat_history = [
        {"type": "text", "sender": "user", "content": "ayyy the new Avengers movie came out!"},
        {"type": "text", "sender": "clkr", "content": "omg ya I saw!"},
        {"type": "text", "sender": "clkr", "content": "I can't wait to watch it"}
    ]
    test_relationship = "crush"
    test_draft = "let's watch it together"

    response = generate_rizz(test_relationship, test_chat_history, test_draft)
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

    response = generate_rizz(test_relationship, test_chat_history)
    print(response)

if __name__ == "__main__":
    # test_generate_rizz()
    # test_describe_image()
    test_generate_rizz_advanced()

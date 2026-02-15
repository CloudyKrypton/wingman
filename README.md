# Wingman

Are YOU socially awkward? Do YOU wish you had more rizz texting and calling your friends, crushes, significant others, whomever? Or maybe YOU'RE just lazy and want someone to write your messages for you! We get it. All of the above apply to the devs of Wingman, which is why we were inspired to make this app -- to empower us and take our texting and calling aura to the next level. ;) 😗

### In all seriousness - What it does
Wingman is a browser extension that's compatible with Discord. It'll read your chat history with the person (or people) of your choice, and if you're stuck on what to say next, or want it to spruce up the response you're about to send, it'll provide a suggestion for you. More than that, it'll listen in on your calls _ live _ and generate on-the-spot responses to what the other(s) in the call might be saying. You'll never feel lost for words with your trusty Wingman on your side.

### How to run Wingman

#### Setup
1. Make sure all the required dependencies are installed.
2. Get a Gemini API key, and paste it into a file called `apikey.txt`. This will be saved onto your local device privately.
3. Initialize an online SQL database with [Supabase](https://supabase.com/).
  - Create a table called `relationships`, with attributes `user_id` (text) and `friend_id` (text) as the primary keys, and `friend_desc` (text).
  - Get the SQL URI for this database, and paste it into a file called `sqluri.txt`. This will be saved onto your local device privately.
4. In `chrome://extensions/`, upload the `frontend` folder in this repository under Load Unpacked.

#### Run the code
1. Run `sql.py` to initialize the database connection.
2. Run `main.py` to begin the Flask backend.

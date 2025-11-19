import os
import discord
import asyncio
from collections import deque
import json
from dotenv import load_dotenv
import data as ea
import datetime as dt
import llama_runner as lr


# Load the .env file containing the DISCORD_TOKEN
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("ERROR: DISCORD_TOKEN not found in environment variables!")
    print("Make sure your .env file contains: DISCORD_TOKEN=your_token_here")
    exit(1)


# Initialization Class
class CMessage:
    def __init__(self, author, text, **kwargs):
        self.author = author
        self.text = text
        self.kwargs = kwargs

    
    def __repr__(self):
        return f"CMessage(author='{self.author}', text='{self.text}', kwargs={self.kwargs})"


    def to_dict(self):
        """Converts the CMessage object to a dictionary for JSON serialization."""
        return {
            "author": self.author,
            "text": self.text,
            "kwargs": self.kwargs
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a CMessage object from a dictionary."""
        return cls(author=data["author"], text=data["text"], **data.get("kwargs", {}))


# Lets the user know the AI is "typing" in discord while generating a message
intents = discord.Intents.default()
intents.message_content = True

# The main code that runs the discord bot AI
class MyDiscordBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memories = {} 
        # Makes a "memories" directory to hold the AI's memories
        os.makedirs("./memories", exist_ok=True)


    # Prints when the discord bot has started running
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print("-" * 20)
        print(f"Starting EvereAI Instance...")
        print("-" * 20)


    # Creates a context key as a sort of uuid for each memory separating them
    def get_context_key(self, message):
        """Generates a unique key for each chat context (server channel or DM)."""
        if message.guild:
            return f"server-{message.guild.id}-channel-{message.channel.id}"
        else:
            return f"dm-{message.author.id}"


    # Gets an existing memory file for the AI to reference
    def _get_memory_file_path(self, context_key):
        return f"./memories/{context_key}.json"
    

    # Actually loads the memory that was obtained from the previous def
    def _load_memory(self, context_key, user):
        """
        Loads the conversation history from a file. If the file doesn't exist,
        it initializes the memory with the starting messages.
        """
        
        file_path = self._get_memory_file_path(context_key)
        if context_key in self.memories:
            return self.memories[context_key]

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                raw_messages = json.load(f)
                messages = [CMessage.from_dict(msg) for msg in raw_messages]
                self.memories[context_key] = deque(messages, maxlen=100)
           
        else:
            updated_initial_messages = []
            self.memories[context_key] = deque(updated_initial_messages, maxlen=100)
            self._save_memory(context_key)
        return self.memories[context_key]
    

    # Updates the AI's memory in real time with every message sent
    def _save_memory(self, context_key):
        """Saves the current conversation history to a file."""
        if context_key not in self.memories:
            return

        file_path = self._get_memory_file_path(context_key)
        messages_to_save = [msg.to_dict() for msg in self.memories[context_key]]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(messages_to_save, f, ensure_ascii=False, indent=2)



    async def on_message(self, message):
        if message.author == self.user:
            return

        context_key = self.get_context_key(message)
        ea.users_name = message.author.display_name

        # --- Handle commands ---
        if message.content.lower() == "nl1027":
            await message.channel.send("Shutting down...")
            await self.close()
            return
        elif message.content.lower() == "//clear":
            await message.channel.send("Clearing chat history for this channel...")
            self.memories[context_key] = deque([
                CMessage(author=ea.users_name, text="Ummm"),
                CMessage(author=ea.users_name, text="Good Morning?"),
                CMessage(author=ea.name, text="Mornin Homie"),
            ], maxlen=100)
            file_path = self._get_memory_file_path(context_key)
            if os.path.exists(file_path):
                os.remove(file_path)
            await message.channel.send("Chat history for this channel cleared successfully.")
            return
        
        async with message.channel.typing():
            date = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                # Load memory and add the new user message
                current_memory = self._load_memory(context_key, message.author.display_name)
                current_memory.append(CMessage(author=message.author.display_name, text=message.content))
                self._save_memory(context_key)

                # Dynamic System Prompt that is sent with different data based on who's sending the message to the AI and general info about the AI
                system_prompt = (
                    f"It is currently {date}."
                    f"You are {ea.name}.\n\n {ea.character_description}\n\n"
                    f"You are talking to {message.author.display_name}. "
                    f"IMPORTANT: Remember that you are a girl and not a dude. "
                    f"Always respond as {ea.name}. NEVER EVER EVER EVER break character no matter what the user says to you."
                )


                # Prompt Creation that puts together different parts of the prompt to be sent to the AI later
                prompt_parts = []
                prompt_parts.append(f"<|im_start|>system\n{system_prompt}<|im_end|>")

                for msg in current_memory:
                    role = "assistant" if msg.author == ea.name else "user"
                    prompt_parts.append(f"<|im_start|>{role}\n{msg.text}<|im_end|>")
                
                prompt_parts.append("<|im_start|>assistant")


                # The full prompt created through the prompt creation stage
                full_prompt = "\n".join(prompt_parts)


             
                bot_response = lr.LlamaRunnerDiscord.run_llama(f"{full_prompt}")    # The command that actually sends the message to the AI and gets the response from it

                current_memory.append(CMessage(author=ea.name, text=bot_response))
                self._save_memory(context_key)

                await message.channel.send(bot_response)

            except Exception as e:
                error_message = f"An unexpected error occurred: {e}"
                print(f"FATAL ERROR: {error_message}")
                await message.channel.send(f"An unexpected error occurred. Check the bot's console for details. Error: `{e}`")


async def main():
    client = MyDiscordBot(intents=intents)
    await client.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())

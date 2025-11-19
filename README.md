# Direct EvereAI Model Run Code
This is a simple program I made that runs the "llama-run" command from the llama.cpp folder to talk with a custom AI model through discord.


## How to Set Up
1. Run the following command to bring the project into a separate folder on your system to download the repository: `git clone https://github.com/KiloXiix/Direct_EvereAI_Model_Run.git`
2. Create a virtual environment using `python -m venv .venv` (optional)
3. Download the latest release of llama.cpp for you system from [here](https://github.com/ggml-org/llama.cpp/releases)
4. Extract the downloaded zip file to your project folder and rename the extracted folder to be "llama", or use a different name if you don't mind changing the program path in the code.
5. Run the command to command to install the dependencies needed: `pip install -r requirements.txt`
6. Create a "models" folder to place any gguf models you have in
7. Modify the "llama_runner.py" file to use your downloaded model
8. Modify the data.py with your own character data
9. Obtain a discord bot TOKEN and place it in a ".env" file like so: `DISCORD_TOKEN={place your token here}
10. Run the "EvereAI_Discord_Bot.py" file to start the discord bot

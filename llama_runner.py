import subprocess


class LlamaRunnerDiscord:
    def run_llama(full_prompt = "Hello? Whats your name?"):

        model_path = "models/evere8b-u3-base.gguf"
        context_size = 16000
        # full_prompt = "Hello? Whats your name?"


        # Subprocess command args to run the command to talk to the AI on your own computer
        command_args = [
            "llama/llama-run.exe",
            f"{model_path}", f"{full_prompt}",
            "-c", f"{context_size}"
        ]


        # Runs the command to send the message to the AI
        result = subprocess.run(command_args, capture_output=True, text=True, check=True)

        # Gets the output of the previous command and cleans it of trailing ANSI codes to be sent into discord without them
        raw_output = result.stdout
        cleaned_output = raw_output.strip().removesuffix('\u001b[0m')

        # Returns the final cleaned output of the AI
        return cleaned_output

        
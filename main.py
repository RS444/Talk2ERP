from voice import listen, speak
from agent import handle_command

def run_assistant():
    while True:
        command = listen()
        if command:
            response = handle_command(command)
            speak(response)

if __name__ == "__main__":
    run_assistant()


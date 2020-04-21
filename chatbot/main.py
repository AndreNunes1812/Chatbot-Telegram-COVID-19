from Controller.botController import*
from time import sleep
# Bot entra em loop
bot.message_loop({
    "chat": receive_message,
    "callback_query": on_callback_query
})

while True:
    sleep(2)
    pass

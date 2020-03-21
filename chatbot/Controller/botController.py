from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from pprint import pprint
import telepot
from time import sleep

bot = telepot.Bot('1144643679:AAG1InJQ0uYGGKemveL1eixUuR3DazLhPDQ')


def receive_message(msg):
    """ Recebe e trata a Mensagem """

    # Imprime a msg em JSON para feedback no terminal
    print(get_message_text(msg))
    if(get_message_text(msg).lower() == "/start"):
        menu_bot_chat(msg)
    else:
        pass


def get_chat_id(msg):
    """ Retorna o ID do Chat """

    return msg['chat']['id']


def get_message_text(msg):
    """ Retorna o texto da mensagem """

    return msg['text']


def get_user_name(msg):
    """ Retorna o nome do usuário """

    return msg['from']['first_name']


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(
        msg, flavor='callback_query')

    print("Callback Query: ", query_data)

    if(query_data == "COMEÇAR pressed"):
        # DADOS PESSOAIS
        idade_user(msg)
    elif((query_data == "SEXO_MASCULINO pressed")or(query_data == "SEXO_FEMININO pressed")):
        doencas_user(msg)
    elif((query_data == "DOENCAS_SIM pressed")or(query_data == "DOENCAS_NAO pressed")):
        sintomas_user(msg)
    elif((query_data == "SINTOMAS_SIM pressed")or(query_data == "SINTOMAS_NAO pressed")):
        historico01_user(msg)
    elif((query_data == "HISTORICO01_SIM pressed")or(query_data == "HISTORICO01_NAO pressed")):
        historico02_user(msg)
    elif((query_data == "HISTORICO02_SIM pressed")or(query_data == "HISTORICO02_NAO pressed")):
        bot.sendMessage(msg['message']['chat']['id'],
                        "Obrigado por responder! 🙂")


def menu_bot_chat(msg):
    """ Função de Menu do Bot """

    # Cria keyboard do menu do bot
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="COMEÇAR",
                              callback_data="COMEÇAR pressed")]
    ])

    # Realiza saudação e envia o menu
    bot.sendMessage(
        get_chat_id(msg),
        text="Olá *" + get_user_name(msg) +
        "* 😀, eu sou um Chatbot desenvolvido para ajudar a combater o *Coronavírus 🦠(COVID-19)*.\n" +
        "Vou realizar sua *Triagem Virtual* 👨‍⚕️, e para isso irei fazer uma *série de perguntas*.\n\n" +
        "Quando estiver pronto, aperte em *COMEÇAR* 😁",
        parse_mode="Markdown",
        reply_markup=keyboard)


def idade_user(msg):
    bot.sendMessage(msg['message']['chat']['id'],
                    "Qual é a sua idade em anos? 🤔")
    sleep(10)
    sexo_user(msg)


def sexo_user(msg):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="Masculino", callback_data="SEXO_MASCULINO pressed"),
        InlineKeyboardButton(text="Feminino", callback_data="SEXO_FEMININO pressed")]])

    bot.sendMessage(msg['message']['chat']['id'],
                    "Qual o seu sexo? 🤔", reply_markup=keyboard)


def doencas_user(msg):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="SIM", callback_data="DOENCAS_SIM pressed"),
         InlineKeyboardButton(text="NÃO", callback_data="DOENCAS_NAO pressed")]])
    bot.sendMessage(msg['message']['chat']['id'],
                    "Você possui alguma dessas doenças crônicas ou se encaixa nesses quesitos? 🤔")
    bot.sendMessage(
        msg['message']['chat']['id'],
        "\nDiabetes\n" +
        "Hipertensão\n" +
        "Insuficiência Cardíaca\n" +
        "Doença Pulmonar Obstrutiva\n" +
        "Asma Grave\n" +
        "HIV\n" +
        "Câncer\n" +
        "Transplantados de qualquer orgão\n" +
        "Usuários de medicação imunosupressora", reply_markup=keyboard
    )


def sintomas_user(msg):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="SIM", callback_data="SINTOMAS_SIM pressed"),
         InlineKeyboardButton(text="NÃO", callback_data="SINTOMAS_NAO pressed")]])
    bot.sendMessage(msg['message']['chat']['id'],
                    "Ultimamente você tem apresentado algum desses sintomas? 🤔")
    bot.sendMessage(
        msg['message']['chat']['id'],
        "\nCoriza\n" +
        "Dor de garganta\n" +
        "Tosse\n" +
        "Dor de cabeça\n" +
        "Febre\n" +
        "Mal Estar em Geral\n" +
        "Dificuldade para respirar\n" +
        "Diarreia", reply_markup=keyboard
    )


def historico01_user(msg):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="SIM", callback_data="HISTORICO01_SIM pressed"),
         InlineKeyboardButton(text="NÃO", callback_data="HISTORICO01_NAO pressed")]])
    bot.sendMessage(
        msg['message']['chat']['id'],
        "\nTeve contato próximo com caso suspeito de Coronavírus?", reply_markup=keyboard
    )


def historico02_user(msg):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="SIM", callback_data="HISTORICO02_SIM pressed"),
         InlineKeyboardButton(text="NÃO", callback_data="HISTORICO02_NAO pressed")]])
    bot.sendMessage(
        msg['message']['chat']['id'],
        "\nTeve contato próximo com caso confirmado de Coronavírus?", reply_markup=keyboard
    )

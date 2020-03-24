from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from haversine import haversine, Unit
from Model.unidades import ubs
from pprint import pprint
from time import sleep
import operator
import telepot
import re


bot = telepot.Bot('820651983:AAEjeM1axbVkn2DPu6kFf7WhvoK8fk_d5eE')
gravidade = 0


def get_chat_id(msg):
    """ Retorna o ID do Chat """

    return msg['chat']['id']


def get_message_text(msg):
    """ Retorna o texto da mensagem """

    return msg['text']


def get_user_name(msg):
    """ Retorna o nome do usuário """

    return msg['from']['first_name']


def receive_message(msg):
    global gravidade
    """ Recebe e trata a Mensagem """
    content_type, chat_type, chat_id = telepot.glance(msg)

    # Imprime a msg em JSON para feedback no terminal
    if((content_type == 'text') and (msg['text'].lower() == "/start")):
        menu_bot_chat(msg)
    if((content_type == 'location')and(gravidade >= 6)):
        location_user = (msg["location"]["latitude"],
                         msg["location"]["longitude"])
        print("Localizacao do user: ", location_user)
        result_distances = []

        for key in ubs:
            result_distances = {}
            for key in ubs:
                result_distances[key] = haversine((ubs[key]["latitude"], ubs[key]
                                                   ["longitude"]), location_user)

        result_distances = sorted(
            result_distances.items(), key=operator.itemgetter(1))
        bot.sendMessage(msg['chat']['id'], "A unidade mais perto de você é a\n🏥" +
                        " **" + str(result_distances[0][0]).upper() + "** ",
                        parse_mode="Markdown")
        bot.sendLocation(
            chat_id=msg['chat']['id'],
            latitude=ubs[result_distances[0][0]]["latitude"],
            longitude=ubs[result_distances[0][0]]['longitude']
        )
    if((content_type == 'text') and (msg['text'].lower() != "/start")):
        txt = msg["text"]
        x = re.findall("\d\d", txt)
        x = int(x[0])
        print("Idade do cara: ", x)
        if(x >= 50):
            gravidade += 2
    else:
        pass


def on_callback_query(msg):
    global gravidade
    query_id, from_id, query_data = telepot.glance(
        msg, flavor='callback_query')

    print("Callback Query: ", query_data)
    if(query_data == "COMEÇAR pressed"):
        bot.answerCallbackQuery(query_id, idade_user(msg))
    if((query_data == "SEXO_MASCULINO pressed")or(query_data == "SEXO_FEMININO pressed")):
        bot.answerCallbackQuery(query_id, doencas_user(msg))
    if((query_data == "DOENCAS_SIM pressed")or(query_data == "DOENCAS_NAO pressed")):
        if(query_data == "DOENCAS_SIM pressed"):
            gravidade += 2
        bot.answerCallbackQuery(query_id, sintomas_user(msg))
    if((query_data == "SINTOMAS_SIM pressed")or(query_data == "SINTOMAS_NAO pressed")):
        if(query_data == "SINTOMAS_SIM pressed"):
            gravidade += 2
        bot.answerCallbackQuery(query_id, historico01_user(msg))
    if((query_data == "HISTORICO01_SIM pressed")or(query_data == "HISTORICO01_NAO pressed")):
        if(query_data == "HISTORICO01_SIM pressed"):
            gravidade += 2
        bot.answerCallbackQuery(query_id, historico02_user(msg))
    if((query_data == "HISTORICO02_SIM pressed")or(query_data == "HISTORICO02_NAO pressed")):
        if((query_data == "HISTORICO02_SIM pressed")or(gravidade >= 6)):
            gravidade += 6
            bot.answerCallbackQuery(query_id, unidade_user(msg))
        else:
            bot.editMessageReplyMarkup(telepot.message_identifier(
                msg["message"]), reply_markup=None)
            bot.answerCallbackQuery(query_id, bot.sendMessage(msg['message']['chat']['id'],
                                                              "Obrigado por responder!\nPor favor fique de quarentena em sua casa 😁",
                                                              parse_mode="Markdown")
                                    )

    if(query_data == "UNIDADE MAIS PROXIMA pressed"):
        bot.editMessageReplyMarkup(telepot.message_identifier(
            msg["message"]), reply_markup=None)
        bot.answerCallbackQuery(query_id,
                                bot.sendMessage(msg['message']['chat']['id'],
                                                "Vá em *Anexo > Localização*, e envie-me sua *Localização Atual*. 😁",
                                                parse_mode="Markdown")
                                )

    else:
        pass


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
        text="Seja Bem-vindo *" + get_user_name(msg) + "*" +
        "\nEu sou 🤖*Covidbot* e vou realizar sua *Triagem Virtual*, e para isso irei fazer uma *série de perguntas* para você.\n\n" +
        "Quando estiver pronto, aperte em *COMEÇAR* 😁",
        parse_mode="Markdown",
        reply_markup=keyboard)

    gravidade = 0


def idade_user(msg):
    bot.editMessageReplyMarkup(telepot.message_identifier(
        msg["message"]), reply_markup=None)
    bot.sendMessage(msg['message']['chat']['id'],
                    "Poderia me informar sua idade em anos? 🤔")
    sleep(11)
    sexo_user(msg)


def sexo_user(msg):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="♂️ Masculino", callback_data="SEXO_MASCULINO pressed"),
        InlineKeyboardButton(text="♀️ Feminino", callback_data="SEXO_FEMININO pressed")]])

    bot.sendMessage(msg['message']['chat']['id'],
                    "Qual é o seu gênero? 🤔", reply_markup=keyboard)


def doencas_user(msg):
    bot.editMessageReplyMarkup(telepot.message_identifier(
        msg["message"]), reply_markup=None)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="SIM", callback_data="DOENCAS_SIM pressed"),
         InlineKeyboardButton(text="NÃO", callback_data="DOENCAS_NAO pressed")]])
    bot.sendMessage(msg['message']['chat']['id'],
                    "Você possui alguma dessas *Doenças crônicas* ou se encaixa nesses quesitos? 😐\n" +
                    "\n*Diabetes*\n" +
                    "*Hipertensão*\n" +
                    "*Insuficiência Cardíaca*\n" +
                    "*Doença Pulmonar Obstrutiva*\n" +
                    "*Asma Grave*\n" +
                    "*HIV*\n" +
                    "*Câncer*\n" +
                    "*Possui transplantados de qualquer orgão*\n" +
                    "*Usuário de medicação imunosupressora*",
                    parse_mode="Markdown", reply_markup=keyboard
                    )


def sintomas_user(msg):
    bot.editMessageReplyMarkup(telepot.message_identifier(
        msg["message"]), reply_markup=None)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="SIM", callback_data="SINTOMAS_SIM pressed"),
         InlineKeyboardButton(text="NÃO", callback_data="SINTOMAS_NAO pressed")]])
    bot.sendMessage(msg['message']['chat']['id'],
                    "Recentemente você tem apresentado algum desses sintomas? 😐\n" +
                    "\n*Coriza*\n" +
                    "*Dor de garganta*\n" +
                    "*Tosse*\n" +
                    "*Dor de cabeça*\n" +
                    "*Febre*\n" +
                    "*Mal Estar em Geral*\n" +
                    "*Dificuldade para respirar*\n" +
                    "*Diarreia*",
                    parse_mode="Markdown", reply_markup=keyboard
                    )


def historico01_user(msg):
    bot.editMessageReplyMarkup(telepot.message_identifier(
        msg["message"]), reply_markup=None)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="SIM", callback_data="HISTORICO01_SIM pressed"),
         InlineKeyboardButton(text="NÃO", callback_data="HISTORICO01_NAO pressed")]])
    bot.sendMessage(
        msg['message']['chat']['id'],
        "Teve contato próximo com *caso suspeito* de Coronavírus?🤨", parse_mode="Markdown", reply_markup=keyboard
    )


def historico02_user(msg):
    bot.editMessageReplyMarkup(telepot.message_identifier(
        msg["message"]), reply_markup=None)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="SIM", callback_data="HISTORICO02_SIM pressed"),
         InlineKeyboardButton(text="NÃO", callback_data="HISTORICO02_NAO pressed")]])
    bot.sendMessage(
        msg['message']['chat']['id'],
        "Teve contato próximo com *caso confirmado* de Coronavírus?🤨", parse_mode="Markdown", reply_markup=keyboard
    )


def unidade_user(msg):
    bot.editMessageReplyMarkup(telepot.message_identifier(
        msg["message"]), reply_markup=None)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="BUSCAR UNIDADE MAIS PRÓXIMA",
                              callback_data="UNIDADE MAIS PROXIMA pressed")]
    ])

    bot.sendMessage(msg['message']['chat']['id'],
                    "Obrigado por responder!\nAgora permita-me encontrar a unidade atendimento perto de você 😁",
                    reply_markup=keyboard)

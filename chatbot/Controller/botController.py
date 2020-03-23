from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from haversine import haversine, Unit
from Model.unidades import unidades
from pprint import pprint
from time import sleep
import operator
import telepot


bot = telepot.Bot('1144643679:AAG1InJQ0uYGGKemveL1eixUuR3DazLhPDQ')


def receive_message(msg):
    """ Recebe e trata a Mensagem """
    content_type, chat_type, chat_id = telepot.glance(msg)

    # Imprime a msg em JSON para feedback no terminal
    if((content_type == 'text') and (msg['text'].lower() == "/start")):
        menu_bot_chat(msg)
    elif(content_type == 'location'):
        location_user = (msg["location"]["latitude"],
                         msg["location"]["longitude"])
        print(location_user)
        result_distances = []

        for key in unidades:
            result_distances = {}
            for key in unidades:
                result_distances[key] = haversine((unidades[key]["latitude"], unidades[key]
                                                   ["longitude"]), location_user)

        result_distances = sorted(
            result_distances.items(), key=operator.itemgetter(1))
        bot.sendMessage(msg['chat']['id'], "A Unidade mais perto de você é a " +
                        str(str(result_distances[0][0])))
        bot.sendLocation(
            chat_id=msg['chat']['id'],
            latitude=unidades[result_distances[0][0]]["latitude"],
            longitude=unidades[result_distances[0][0]]['longitude']
        )
    else:
        print(content_type)
        pprint(msg)
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
        bot.answerCallbackQuery(query_id, idade_user(msg))
    if((query_data == "SEXO_MASCULINO pressed")or(query_data == "SEXO_FEMININO pressed")):
        bot.answerCallbackQuery(query_id, doencas_user(msg))
    if((query_data == "DOENCAS_SIM pressed")or(query_data == "DOENCAS_NAO pressed")):
        bot.answerCallbackQuery(query_id, sintomas_user(msg))
    if((query_data == "SINTOMAS_SIM pressed")or(query_data == "SINTOMAS_NAO pressed")):
        bot.answerCallbackQuery(query_id, historico01_user(msg))
    if((query_data == "HISTORICO01_SIM pressed")or(query_data == "HISTORICO01_NAO pressed")):
        bot.answerCallbackQuery(query_id, historico02_user(msg))
    if((query_data == "HISTORICO02_SIM pressed")or(query_data == "HISTORICO02_NAO pressed")):
        bot.answerCallbackQuery(query_id, unidade_user(msg))

    if(query_data == "UNIDADE MAIS PROXIMA pressed"):
        bot.answerCallbackQuery(query_id, bot.sendMessage(msg['message']['chat']['id'],
                                                          "Vá em *Anexo > Localização*, e envie-me sua *Localização Atual*! 😁",
                                                          parse_mode="Markdown",))

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
                    "Você possui alguma dessas *Doenças crônicas* ou se encaixa nesses quesitos? 🤔\n" +
                    "\n*Diabetes*\n" +
                    "*Hipertensão*\n" +
                    "*Insuficiência Cardíaca*\n" +
                    "*Doença Pulmonar Obstrutiva*\n" +
                    "*Asma Grave*\n" +
                    "*HIV*\n" +
                    "*Câncer*\n" +
                    "*Transplantados de qualquer orgão*\n" +
                    "*Usuários de medicação imunosupressora*",
                    parse_mode="Markdown", reply_markup=keyboard
                    )


def sintomas_user(msg):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="SIM", callback_data="SINTOMAS_SIM pressed"),
         InlineKeyboardButton(text="NÃO", callback_data="SINTOMAS_NAO pressed")]])
    bot.sendMessage(msg['message']['chat']['id'],
                    "Ultimamente você tem apresentado algum desses sintomas? 🤔\n" +
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
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="SIM", callback_data="HISTORICO01_SIM pressed"),
         InlineKeyboardButton(text="NÃO", callback_data="HISTORICO01_NAO pressed")]])
    bot.sendMessage(
        msg['message']['chat']['id'],
        "Teve contato próximo com caso suspeito de Coronavírus?", reply_markup=keyboard
    )


def historico02_user(msg):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="SIM", callback_data="HISTORICO02_SIM pressed"),
         InlineKeyboardButton(text="NÃO", callback_data="HISTORICO02_NAO pressed")]])
    bot.sendMessage(
        msg['message']['chat']['id'],
        "Teve contato próximo com caso confirmado de Coronavírus?", reply_markup=keyboard
    )


def unidade_user(msg):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="UNIDADE MAIS PROXIMA",
                              callback_data="UNIDADE MAIS PROXIMA pressed")]
    ])

    bot.sendMessage(msg['message']['chat']['id'],
                    "Obrigado por responder!, deixe-me encontrar a unidade atendimento mais próxima de você 😁",
                    reply_markup=keyboard)

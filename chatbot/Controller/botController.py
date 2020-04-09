from csv import DictWriter
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from haversine import haversine, Unit
from Model.unidades_atendimento import ubs, hospitais
from pprint import pprint
from time import sleep
import operator
import telepot
import csv
import re


bot = telepot.Bot('820651983:AAGw5xDAWJ1ILN2IgaP-jVaelhgO_jL6juM')
user = {}
gravidade = 0
fieldnames = ["nome", "idade", "genero",
              "sintomas", "grau", "latitude", "longitude"]


def append_dict_as_row(file_name, dict_of_elem, field_names):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        dict_writer = DictWriter(write_obj, fieldnames=field_names)
        # Add dictionary as wor in the csv
        dict_writer.writerow(dict_of_elem)
# {'nome': 'Erik', 'idade': 68, 'genero': 'F', 'sintomas': 'S', 'grau': 'ALTO', 'latitude': -3.041709, 'longitude': -59.99728}


def get_message_text(msg):
    """ Retorna o texto da mensagem """

    return msg['text']


def get_user_name(msg):
    """ Retorna o nome do usuário """

    return msg['from']['first_name']


def receive_message(msg):
    global gravidade
    global user
    global fieldnames
    """ Recebe e trata a Mensagem """
    content_type, chat_type, chat_id = telepot.glance(msg)

    if((content_type == 'text') and (msg['text'].lower() == "/start")):
        menu_bot_chat(msg)
    if((content_type == 'location')and(gravidade != 0)):
        if(gravidade <= 4):
            user["grau"] = "BAIXO"
        if((gravidade > 4) and (gravidade <= 5)):
            user["grau"] = "MEDIO"
            user["latitude"] = msg["location"]["latitude"]
            user["longitude"] = msg["location"]["longitude"]

            location_user = (msg["location"]["latitude"],
                             msg["location"]["longitude"])
            result_distances = []

            for key in ubs:
                result_distances = {}
                for key in ubs:
                    result_distances[key] = haversine((ubs[key]["latitude"], ubs[key]
                                                       ["longitude"]), location_user)

            result_distances = sorted(
                result_distances.items(), key=operator.itemgetter(1))
            bot.sendMessage(msg['chat']['id'],
                            "*Unidade de atendimento* mais perto de você:",
                            parse_mode="Markdown")

            bot.sendVenue(
                chat_id=msg['chat']['id'],
                latitude=ubs[result_distances[0][0]]["latitude"],
                longitude=ubs[result_distances[0][0]]['longitude'],
                title=str(result_distances[0][0]).upper(),
                address=str(ubs[result_distances[0][0]]["end"]),
                foursquare_id=None
            )
            bot.sendMessage(msg['chat']['id'],
                            "Caso tenha dúvidas sobre seu atendimento, consulte um 👨‍⚕️ Médico da UEA por meio do contato telegram abaixo.",
                            parse_mode="Markdown")
            bot.sendMessage(msg['chat']['id'],
                            "https://t.me/medicouea",
                            parse_mode="Markdown")
            append_dict_as_row('chatbotRelatorio.csv', user, fieldnames)
            gravidade = 0
        if(gravidade > 5):
            user["grau"] = "ALTO"
            user["latitude"] = msg["location"]["latitude"]
            user["longitude"] = msg["location"]["longitude"]

            location_user = (msg["location"]["latitude"],
                             msg["location"]["longitude"])
            result_distances = []

            for key in ubs:
                result_distances = {}
                for key in ubs:
                    result_distances[key] = haversine((ubs[key]["latitude"], ubs[key]
                                                       ["longitude"]), location_user)

            result_distances = sorted(
                result_distances.items(), key=operator.itemgetter(1))
            bot.sendMessage(msg['chat']['id'],
                            "*Unidade de atendimento* mais perto de você:",
                            parse_mode="Markdown")

            bot.sendVenue(
                chat_id=msg['chat']['id'],
                latitude=ubs[result_distances[0][0]]["latitude"],
                longitude=ubs[result_distances[0][0]]['longitude'],
                title=str(result_distances[0][0]).upper(),
                address=str(ubs[result_distances[0][0]]["end"]),
                foursquare_id=None
            )
            bot.sendMessage(msg['chat']['id'],
                            "Caso tenha dúvidas sobre seu atendimento, consulte um 👨‍⚕️ Médico da UEA por meio do contato telegram abaixo.",
                            parse_mode="Markdown")
            bot.sendMessage(msg['chat']['id'],
                            "https://t.me/medicouea",
                            parse_mode="Markdown")
            append_dict_as_row('chatbotRelatorio.csv', user, fieldnames)
            gravidade = 0

    else:
        pass


def on_callback_query(msg):
    global gravidade

    query_id, from_id, query_data = telepot.glance(
        msg, flavor='callback_query')

    print("Callback Query: ", query_data)
    if(query_data == "COMEÇAR pressed"):
        remove_buttons(msg)
        bot.sendMessage(msg['message']['chat']['id'], text="Qual seu tipo de triagem?",
                        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="CRIANÇA",
                                                  callback_data="CRIANÇA pressed")],
                            [InlineKeyboardButton(text="ADULTO",
                                                  callback_data="ADULTO pressed")]]))
    if(query_data == "CRIANÇA pressed"):
        bot.answerCallbackQuery(query_id, idade_user_crianca(msg))
    if(query_data == "SIM IDADE 5 pressed"):
        gravidade += 2
        bot.answerCallbackQuery(query_id, sintomas_user_crianca(msg))
    if(query_data == "NÃO IDADE 5 pressed"):
        indicacao_user_crianca(msg)
        send_contato(msg)
    if(query_data == "SIM SINTOMAS CRIANÇA pressed"):
        gravidade += 2
        bot.answerCallbackQuery(query_id, sensacao_user_crianca(msg))
    if(query_data == "NÃO SINTOMAS CRIANÇA pressed"):
        indicacao_user_crianca(msg)
        send_contato(msg)
    if(query_data == "SIM SENSAÇÃO CRIANÇA pressed"):
        gravidade += 2
        bot.answerCallbackQuery(query_id, unidade_user(msg))
        bot.sendMessage(
            msg['message']['chat']['id'], "Por favor procurar imediatamente a emergência na UBS mais próxima ou chamar *SAMU - 190*", parse_mode="Markdown")
    if(query_data == "NÃO SENSAÇÃO CRIANÇA pressed"):
        indicacao_user_crianca(msg)
        send_contato(msg)
    if(query_data == "ADULTO pressed"):
        bot.answerCallbackQuery(query_id, idade_user(msg))
    if((query_data == "IDADE ADULTO pressed")or(query_data == "MEIA IDADE pressed")or(query_data == "IDADE IDOSO pressed")):
        if(query_data == "IDADE ADULTO pressed"):
            user["idade"] = "adulto"
            gravidade += 1
        elif(query_data == "MEIA IDADE pressed"):
            user["idade"] = "meia-idade"
            gravidade += 1
        elif(query_data == "IDADE IDOSO pressed"):
            user["idade"] = "idoso"
            gravidade += 2
        bot.answerCallbackQuery(query_id, sexo_user(msg))

    if((query_data == "SEXO_MASCULINO pressed")or(query_data == "SEXO_FEMININO pressed")):
        if(query_data == "SEXO_MASCULINO pressed"):
            user["genero"] = "M"
        if(query_data == "SEXO_MASCULINO pressed"):
            user["genero"] = "F"
        bot.answerCallbackQuery(query_id, doencas_user(msg))
    if((query_data == "DOENCAS_SIM pressed")or(query_data == "DOENCAS_NÃO pressed")):
        if(query_data == "DOENCAS_SIM pressed"):
            gravidade += 1
        bot.answerCallbackQuery(query_id, sintomas_user(msg))
    if((query_data == "SINTOMAS_SIM pressed")or(query_data == "SINTOMAS_NÃO pressed")):
        if(query_data == "SINTOMAS_SIM pressed"):
            user["sintomas"] = "S"
            gravidade += 3
        else:
            user["sintomas"] = "N"
        bot.answerCallbackQuery(query_id, historico01_user(msg))
    if((query_data == "HISTORICO01_SIM pressed")or(query_data == "HISTORICO01_NÃO pressed")):
        if(query_data == "HISTORICO01_SIM pressed"):
            gravidade += 2
        bot.answerCallbackQuery(query_id, historico02_user(msg))
    if((query_data == "HISTORICO02_SIM pressed")or(query_data == "HISTORICO02_NÃO pressed")):
        if((query_data == "HISTORICO02_SIM pressed")and(gravidade >= 5)and((user["idade"] == "meia-idade")or(user["idade"] == "idoso"))):
            gravidade += 3
            bot.answerCallbackQuery(query_id, unidade_user(msg))
        elif(((user["idade"] == "meia-idade")or(user["idade"] == "idoso"))and(query_data == "HISTORICO02_SIM pressed")):
            remove_buttons(msg)
            bot.answerCallbackQuery(query_id, bot.sendMessage(msg['message']['chat']['id'],
                                                              "Obrigado por responder!😁\n" +
                                                              "Não esqueça de:\n\n" +
                                                              "*1.* Lave bem as mãos com água e sabão 🤲🧼🚰 (ou use álcool e gel 👏🧴)\n" +
                                                              "\n*2.* Cubra nariz e boca ao espirrar e tossir 🤧😣💦\n" +
                                                              "\n*3.* Evite aglomerações se estiver doente 🙂🤒🙂\n" +
                                                              "\n*4.* Mantenha os ambientes bem ventilados 🖼️🍃\n" +
                                                              "\n*5.* Não compartilhe objetos pessoais 🙂🍽️😀\n\n" +
                                                              "Sair de casa só quando necessário, respeite o período de quarentena por sua saúde e de seu próximo 😁",
                                                              parse_mode="Markdown"))

        elif((gravidade >= 5)and((user["idade"] == "meia-idade")or(user["idade"] == "idoso"))):
            bot.answerCallbackQuery(query_id, unidade_user(msg))
        else:
            remove_buttons(msg)
            bot.answerCallbackQuery(query_id, bot.sendMessage(msg['message']['chat']['id'],
                                                              "Obrigado por responder!😁\n" +
                                                              "Não esqueça de:\n\n" +
                                                              "*1.* Lave bem as mãos com água e sabão 🤲🧼🚰 (ou use álcool e gel 👏🧴)\n" +
                                                              "\n*2.* Cubra nariz e boca ao espirrar e tossir 🤧😣💦\n" +
                                                              "\n*3.* Evite aglomerações se estiver doente 🙂🤒🙂\n" +
                                                              "\n*4.* Mantenha os ambientes bem ventilados 🖼️🍃\n" +
                                                              "\n*5.* Não compartilhe objetos pessoais 🙂🍽️😀\n\n" +
                                                              "Sair de casa só quando necessário, respeite o período de quarentena por sua saúde e de seu próximo 😁",
                                                              parse_mode="Markdown"))
    if(query_data == "UNIDADE MAIS PROXIMA pressed"):
        remove_buttons(msg)
        bot.answerCallbackQuery(query_id,
                                bot.sendMessage(msg['message']['chat']['id'],
                                                "Vá em *Anexo > Localização*, e envie-me sua *Localização Atual*. 😁",
                                                parse_mode="Markdown")
                                )

    else:
        pass


def remove_buttons(msg):
    bot.editMessageReplyMarkup(telepot.message_identifier(
        msg["message"]), reply_markup=None)


def send_contato(msg):
    bot.sendMessage(msg['message']['chat']['id'],
                    "Caso tenha dúvidas sobre seu atendimento, consulte um 👨‍⚕️ Médico da UEA por meio do contato telegram abaixo.",
                    parse_mode="Markdown")
    bot.sendMessage(msg['message']['chat']['id'],
                    "https://t.me/medicouea",
                    parse_mode="Markdown")


def menu_bot_chat(msg):
    global user
    """ Função de Menu do Bot """

    bot.sendMessage(
        msg['chat']['id'],
        text="ATENÇÃO VERSÃO DE TESTES, NÃO OFICIAL!\n\nSeja Bem-vindo *" + get_user_name(msg) + "*" +
        "\nEu sou o *🤖CovidBot da UEA* e vou realizar a sua *Triagem Virtual.*\nPara isso irei fazer uma série de perguntas para você.\n" +
        "\nQuando estiver pronto, aperte em *COMEÇAR* 😁",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="COMEÇAR",
                                  callback_data="COMEÇAR pressed")]
        ]))

    user["nome"] = get_user_name(msg)
    gravidade = 0


def idade_user_crianca(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "A criança tem mais de *5 anos* de idade? 🤔", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="SIM", callback_data="SIM IDADE 5 pressed"),
                         InlineKeyboardButton(text="NÃO", callback_data="NÃO IDADE 5 pressed")]]))


def sintomas_user_crianca(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "A criança tem algum desses sintomas? 🤔" +
                    "\n\n*Febre*\n*Tosse*\n*Dor de garganta*\n*Dificuldade respiratória*\n", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="SIM", callback_data="SIM SINTOMAS CRIANÇA pressed"),
                         InlineKeyboardButton(text="NÃO", callback_data="NÃO SINTOMAS CRIANÇA pressed")]]))


def sensacao_user_crianca(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'], "A criança apresenta falta de ar, sensação de desmaio?", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="SIM", callback_data="SIM SENSAÇÃO CRIANÇA pressed"),
         InlineKeyboardButton(text="NÃO", callback_data="NÃO SENSAÇÃO CRIANÇA pressed")]]))


def indicacao_user_crianca(msg):
    bot.sendMessage(msg['message']['chat']['id'],
                    "Obrigado por responder!😁\n" +
                    "Fique de olho no que deve ser evitado:\n\n" +
                    "*1.* Não chamar coleguinha ou visitas para casa\n" +
                    "\n*2.* Não sair para parquinho, playground ou para qualquer outra atividade externa\n" +
                    "\n*3.* Manter distância dos idosos que estiverem em casa\n",
                    parse_mode="Markdown")


def idade_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "Qual seria sua faixa de idade em anos? 🤔", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Entre 20 a 39 anos",
                                              callback_data="IDADE ADULTO pressed")],
                        [InlineKeyboardButton(text="Entre 40 a 59 anos",
                                              callback_data="MEIA IDADE pressed")],
                        [InlineKeyboardButton(text="Mais de 60 anos",
                                              callback_data="IDADE IDOSO pressed")]
                    ]))


def sexo_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "Qual é o seu gênero? 🤔", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
                        text="♂️ Masculino", callback_data="SEXO_MASCULINO pressed"),
                        InlineKeyboardButton(text="♀️ Feminino", callback_data="SEXO_FEMININO pressed")]]))


def doencas_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "Você possui alguma dessas *Doenças crônicas* ou se encaixa nesses quesitos? 😕\n" +
                    "\n*Diabetes*\n" +
                    "*Hipertensão*\n" +
                    "*Insuficiência Cardíaca*\n" +
                    "*Doença Pulmonar Obstrutiva*\n" +
                    "*Asma Grave*\n" +
                    "*HIV*\n" +
                    "*Câncer*\n" +
                    "*Possui transplantados de qualquer orgão*\n" +
                    "*Usuário de medicação imunosupressora*",
                    parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="SIM", callback_data="DOENCAS_SIM pressed"),
                            InlineKeyboardButton(text="NÃO", callback_data="DOENCAS_NÃO pressed")]])
                    )


def sintomas_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "Recentemente você tem apresentado algum desses sintomas? 😯\n" +
                    "\n*Coriza*\n" +
                    "*Dor de garganta*\n" +
                    "*Tosse*\n" +
                    "*Dor de cabeça*\n" +
                    "*Febre*\n" +
                    "*Mal Estar em Geral*\n" +
                    "*Dificuldade para respirar*\n" +
                    "*Diarreia\n" +
                    "*Perda de Olfato\n" +
                    "*Perda de Paladar*",
                    parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="SIM", callback_data="SINTOMAS_SIM pressed"),
                            InlineKeyboardButton(text="NÃO", callback_data="SINTOMAS_NÃO pressed")]])
                    )


def historico01_user(msg):
    remove_buttons(msg)
    bot.sendMessage(
        msg['message']['chat']['id'],
        "Teve contato próximo com *caso suspeito* de Coronavírus?🤨", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="SIM", callback_data="HISTORICO01_SIM pressed"),
                InlineKeyboardButton(text="NÃO", callback_data="HISTORICO01_NÃO pressed")]])
    )


def historico02_user(msg):
    remove_buttons(msg)
    bot.sendMessage(
        msg['message']['chat']['id'],
        "Teve contato próximo com *caso confirmado* de Coronavírus?😯", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="SIM", callback_data="HISTORICO02_SIM pressed"),
                InlineKeyboardButton(text="NÃO", callback_data="HISTORICO02_NÃO pressed")]])
    )


def unidade_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "Obrigado por responder!\nAgora permita-me encontrar a unidade atendimento perto de você 😁",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="BUSCAR UNIDADE MAIS PRÓXIMA",
                                              callback_data="UNIDADE MAIS PROXIMA pressed")]]))

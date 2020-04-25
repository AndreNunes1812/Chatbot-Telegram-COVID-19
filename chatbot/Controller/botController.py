#   UNIVERSIDADE DO ESTADO AMAZONAS
#          Chatbot Saúde UEA
#
# Membros deste projeto:
#
#   Prof. Dr. Fábio Santos da Silva
#   Erik Atílio Silva Reys
#   Oscar de Menezes Neto
#   Ramayna Menezes
#   Jorge Procópio
#   Profa. Mariana Broker
#   Profa. Waldeyde Magalhães
#   Profa. Dra Elielza Guerreira
#   Prof. Dr. Darlisom Souza

from csv import DictWriter
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from haversine import haversine, Unit
from Model.base_unidades_atendimento import ubs, hospitais, maternidade
from pprint import pprint
from time import sleep
import operator
import telepot
import csv
import re


bot = telepot.Bot('820651983:AAGw5xDAWJ1ILN2IgaP-jVaelhgO_jL6juM')
#bot = telepot.Bot('1208891513:AAGuPrniWVW_MpEfWQt5-5HXuRhnsDPpb2Y')  # teste
user = {}
gravidade = 0
recomendar = False
fim_questionario = False
tipo_atendimento = ''
fieldnames = [
    "nome",
    "idade",
    "genero",
    "febre",
    "dor_de_cabeca",
    "coriza",
    "dor_na_garganta",
    "tosse_seca",
    "dificuldade_respiratoria",
    "dores_no_corpo",
    "diarreia",
    "dor_no_peito",
    "contato_suspeito",
    "contato_infectado",
    "grau", "latitude", "longitude"]


def get_message_text(msg):
    """ Retorna o texto da mensagem """

    return msg['text']


def get_user_name(msg):
    """ Retorna o nome do usuário """

    return msg['from']['first_name']


def recomendar_unidade(msg_id, location_user, base):
    for key in base:
        result_distances = {}
        for key in base:
            result_distances[key] = haversine((base[key]["latitude"], base[key]
                                               ["longitude"]), location_user)
    result_distances = sorted(
        result_distances.items(), key=operator.itemgetter(1))
    bot.sendMessage(msg_id,
                    "*Unidade de atendimento* mais perto de você:",
                    parse_mode="Markdown")

    bot.sendVenue(
        chat_id=msg_id,
        latitude=base[result_distances[0]
                      [0]]["latitude"],
        longitude=base[result_distances[0]
                       [0]]['longitude'],
        title=str(result_distances[0][0]).upper(),
        address=str(
            base[result_distances[0][0]]["end"]),
        foursquare_id=None
    )


def append_dict_as_row(file_name, dict_of_elem, field_names):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        dict_writer = DictWriter(write_obj, fieldnames=field_names)
        # Add dictionary as wor in the csv
        dict_writer.writerow(dict_of_elem)


def receive_message(msg):
    global gravidade
    global recomendar
    global user
    global fieldnames
    """ Recebe e trata a Mensagem """
    content_type, chat_type, chat_id = telepot.glance(msg)

    if((content_type == 'text') and (msg['text'].lower() == "/start")):
        menu_bot_chat(msg)
    if((content_type == 'location')and(recomendar == True)):
        if(user["grau"] == "BAIXO"):
            pass
        if(user["grau"] == "MEDIO"):
            user["latitude"] = msg["location"]["latitude"]
            user["longitude"] = msg["location"]["longitude"]
            location_user = (msg["location"]["latitude"],
                             msg["location"]["longitude"])
            result_distances = []

            if(user["idade"] == "idoso"):
                recomendar_unidade(msg['chat']['id'], location_user, hospitais)
            if(user["genero"] == "FG"):
                recomendar_unidade(msg['chat']['id'],
                                   location_user, maternidade)
            else:
                recomendar_unidade(msg['chat']['id'], location_user, ubs)
            recomendar = False
            fim_questionario = False
            append_dict_as_row('chatbotRelatorio.csv', user, fieldnames)
        if(user["grau"] == "ALTO"):
            user["grau"] = "ALTO"
            user["latitude"] = msg["location"]["latitude"]
            user["longitude"] = msg["location"]["longitude"]

            location_user = (msg["location"]["latitude"],
                             msg["location"]["longitude"])
            result_distances = []

            if(user["idade"] == "idoso"):
                recomendar_unidade(msg['chat']['id'], location_user, hospitais)
            if(user["genero"] == "FG"):
                recomendar_unidade(msg['chat']['id'],
                                   location_user, maternidade)
            else:
                recomendar_unidade(msg['chat']['id'], location_user, ubs)
            recomendar = False
            fim_questionario = False
            append_dict_as_row('chatbotRelatorio.csv', user, fieldnames)
    else:
        pass


def on_callback_query(msg):
    global gravidade
    global recomendar
    global fim_questionario
    global fieldnames
    global tipo_atendimento
    global user

    query_id, from_id, query_data = telepot.glance(
        msg, flavor='callback_query')

    print("Callback Query: ", query_data)
    if(query_data == "COMEÇAR pressed"):
        bot.answerCallbackQuery(query_id, sub_menu(msg))
    if(query_data == "CRÉDITOS pressed"):
        bot.answerCallbackQuery(query_id, creditos(msg))
    if(query_data == "EQUIPE DE SAÚDE pressed"):
        if(tipo_atendimento == 'clinica_geral'):
            bot.answerCallbackQuery(
                query_id, send_contatos_medicos_enfermeiros(msg))
            fim_questionario = True
        if((tipo_atendimento == 'pediatria')and((user['grau'] == 'MEDIO')or(user['grau'] == 'ALTO'))):
            bot.answerCallbackQuery(
                query_id, send_contatos_medicos_enfermeiros(msg))
            unidade_user(msg)
        if((tipo_atendimento == 'pediatria')and(user['grau'] == 'BAIXO')):
            bot.answerCallbackQuery(
                query_id, send_contatos_medicos_enfermeiros(msg))
    if(query_data == "PSICOLÓGOS pressed"):
        if(tipo_atendimento == 'clinica_geral'):
            bot.answerCallbackQuery(
                query_id, send_contatos_alunos_tutores(msg))
            fim_questionario = True
        if((tipo_atendimento == 'pediatria')and((user['grau'] == 'MEDIO')or(user['grau'] == 'ALTO'))):
            bot.answerCallbackQuery(
                query_id, send_contatos_alunos_tutores(msg))
            unidade_user(msg)
        if((tipo_atendimento == 'pediatria')and(user['grau'] == 'BAIXO')):
            bot.answerCallbackQuery(
                query_id, send_contatos_alunos_tutores(msg))
    if(query_data == "VOLTAR pressed"):
        remove_buttons(msg)
        bot.answerCallbackQuery(query_id, menu_bot_chat(msg['message']))
    if(query_data == "PSICOLOGIA pressed"):
        bot.answerCallbackQuery(query_id, psicologia(msg))
    if(query_data == "CRIANÇA pressed"):
        tipo_atendimento = 'pediatria'
        bot.answerCallbackQuery(query_id, idade_user_crianca(msg))
    if(query_data == "SIM IDADE 5 pressed"):
        gravidade += 2
        user["idade"] = "crianca"
        user["genero"] = ""
        bot.answerCallbackQuery(query_id, sintomas_user_crianca(msg))
    if(query_data == "NÃO IDADE 5 pressed"):
        user["idade"] = "crianca"
        user["genero"] = ""
        user["grau"] = "BAIXO"
        remove_buttons(msg)
        indicacao_user_crianca(msg['message']['chat']['id'])
    if(query_data == "SIM SINTOMAS CRIANÇA pressed"):
        gravidade += 2
        bot.answerCallbackQuery(query_id, sensacao_user_crianca(msg))
    if(query_data == "NÃO SINTOMAS CRIANÇA pressed"):
        user["grau"] = "BAIXO"
        remove_buttons(msg)
        indicacao_user_crianca(msg['message']['chat']['id'])
    if((query_data == "SIM SENSAÇÃO CRIANÇA pressed")or(query_data == "NÃO SENSAÇÃO CRIANÇA pressed")):
        if(query_data == "SIM SENSAÇÃO CRIANÇA pressed"):
            remove_buttons(msg)
            gravidade += 2
        if(gravidade == 4):
            user["grau"] = "MEDIO"
            recomendar = True

            bot.sendMessage(msg['message']['chat']['id'],
                            "Por favor *procurar imediatamente* a emergência em unidade de atendimento mais próxima ou chamar *SAMU - 192*",
                            parse_mode="Markdown")
            send_contato(msg['message']['chat']['id'])
        if(gravidade == 6):

            user["grau"] = "ALTO"
            recomendar = True

            bot.sendMessage(msg['message']['chat']['id'],
                            "Por favor *procurar imediatamente* a emergência em unidade de atendimento mais próxima ou chamar *SAMU - 192*",
                            parse_mode="Markdown")
            send_contato(msg['message']['chat']['id'])
        else:
            user["grau"] = "BAIXO"
            remove_buttons(msg)
            indicacao_user_crianca(msg['message']['chat']['id'])

# TRIAGEM CLINICA GERAL
    if(query_data == "ADULTO pressed"):
        tipo_atendimento = 'clinica_geral'
        bot.answerCallbackQuery(query_id, idade_user(msg))
    if((query_data == "IDADE ADULTO pressed")or(query_data == "MEIA IDADE pressed")or(query_data == "IDADE IDOSO pressed")):
        if(query_data == "IDADE ADULTO pressed"):
            user["idade"] = "adulto"
        elif(query_data == "MEIA IDADE pressed"):
            user["idade"] = "meia-idade"
        elif(query_data == "IDADE IDOSO pressed"):
            user["idade"] = "idoso"
        bot.answerCallbackQuery(query_id, sexo_user(msg))
    if((query_data == "SEXO_MASCULINO pressed")or(query_data == "SEXO_FEMININO pressed")):
        if(query_data == "SEXO_MASCULINO pressed"):
            user["genero"] = "M"
            bot.answerCallbackQuery(query_id, febre_user(msg))
        if(query_data == "SEXO_FEMININO pressed"):
            bot.answerCallbackQuery(query_id, gestante_user(msg))
    if((query_data == "SIM GESTANTE pressed") or (query_data == "NÃO GESTANTE pressed")):
        if(query_data == "SIM GESTANTE pressed"):
            user["genero"] = "FG"
            gravidade += 5
        if(query_data == "NÃO GESTANTE pressed"):
            user["genero"] = "F"
        bot.answerCallbackQuery(query_id, febre_user(msg))
    if((query_data == "SIM FEBRE pressed")or(query_data == "NÃO FEBRE pressed")):
        if(query_data == "SIM FEBRE pressed"):
            gravidade += 5
            user["febre"] = "sim"
        else:
            user["febre"] = "nao"
        bot.answerCallbackQuery(query_id, dor_cabeca_user(msg))
    if((query_data == "SIM DOR CABEÇA pressed")or(query_data == "NÃO DOR CABEÇA pressed")):
        if(query_data == "SIM DOR CABEÇA pressed"):
            gravidade += 1
            user["dor_de_cabeca"] = "sim"
        else:
            user["dor_de_cabeca"] = "nao"
        bot.answerCallbackQuery(query_id, coriza_user(msg))
    if((query_data == "SIM CORIZA pressed")or(query_data == "NÃO CORIZA pressed")):
        if(query_data == "SIM CORIZA pressed"):
            gravidade += 1
            user["coriza"] = "sim"
        else:
            user["coriza"] = "nao"
        bot.answerCallbackQuery(query_id, dor_garganta_user(msg))
    if((query_data == "SIM DOR NA GARGANTA pressed")or(query_data == "NÃO DOR NA GARGANTA pressed")):
        if(query_data == "SIM DOR NA GARGANTA pressed"):
            gravidade += 1
            user["dor_na_garganta"] = "sim"
        else:
            user["dor_na_garganta"] = "nao"
        bot.answerCallbackQuery(query_id, tosse_user(msg))
    if((query_data == "SIM TOSSE pressed")or(query_data == "NÃO TOSSE pressed")):
        if(query_data == "SIM TOSSE pressed"):
            gravidade += 3
            user["tosse_seca"] = "sim"
        else:
            user["tosse_seca"] = "nao"
        bot.answerCallbackQuery(query_id, dificuldade_respiratoria_user(msg))
    if((query_data == "SIM DIFICULDADE RESPIRATORIA pressed")or(query_data == "NÃO DIFICULDADE RESPIRATORIA pressed")):
        if(query_data == "SIM DIFICULDADE RESPIRATORIA pressed"):
            gravidade += 10
            user["dificuldade_respiratoria"] = "sim"
        else:
            user["dificuldade_respiratoria"] = "nao"
        bot.answerCallbackQuery(query_id, dor_no_corpo_user(msg))
    if((query_data == "SIM DOR NO CORPO pressed")or(query_data == "NÃO DOR NO CORPO pressed")):
        if(query_data == "SIM DOR NO CORPO pressed"):
            gravidade += 1
            user["dores_no_corpo"] = "sim"
        else:
            user["dores_no_corpo"] = "nao"
        bot.answerCallbackQuery(query_id, diarreia_user(msg))
    if((query_data == "SIM DIARREIA pressed")or(query_data == "NÃO DIARREIA pressed")):
        if(query_data == "SIM DIARREIA pressed"):
            gravidade += 1
            user["diarreia"] = "sim"
        else:
            user["diarreia"] = "nao"
        bot.answerCallbackQuery(query_id, peito_user(msg))
    if((query_data == "SIM DOR NO PEITO pressed")or(query_data == "NÃO DOR NO PEITO pressed")):
        if(query_data == "SIM DOR NO PEITO pressed"):
            gravidade += 3
            user["dor_no_peito"] = "sim"
        else:
            user["dor_no_peito"] = "nao"
        bot.answerCallbackQuery(query_id, historico_user(msg))
    if((query_data == "SIM HISTORICO pressed")or(query_data == "NÃO HISTORICO pressed")):
        if(query_data == "SIM HISTORICO pressed"):
            gravidade += 10
            user["contato_suspeito"] = "sim"
        else:
            user["contato_suspeito"] = "nao"
        bot.answerCallbackQuery(query_id, historico02_user(msg))
    if((query_data == "SIM HISTORICO02 pressed")or(query_data == "NÃO HISTORICO02 pressed")):
        if(query_data == "SIM HISTORICO02 pressed"):
            gravidade += 10
            remove_buttons(msg)
            user["contato_infectado"] = "sim"
        else:
            remove_buttons(msg)
            user["contato_infectado"] = "nao"
        send_contato(msg['message']['chat']['id'])
    if(query_data == "UNIDADE MAIS PROXIMA pressed"):
        remove_buttons(msg)
        bot.sendMessage(msg['message']['chat']['id'],
                        "Vá em *Anexo > Localização*, e envie-me sua *Localização Atual*. 😁",
                        parse_mode="Markdown")
    elif(fim_questionario == True):
        if(gravidade <= 9):
            user["grau"] = "BAIXO"
            send_medidas(msg['message']['chat']['id'])
        if((gravidade >= 10) and (gravidade <= 19)):
            user["grau"] = "MEDIO"
            recomendar = True
            unidade_user(msg)
        if((gravidade >= 20) and (gravidade <= 51)):
            user["grau"] = "ALTO"
            recomendar = True
            unidade_user(msg)
    else:
        pass


# FUNÇÕES DE CONTROLE
def remove_buttons(msg):
    """ Remove os inline buttons das mensagens do bot """

    bot.editMessageReplyMarkup(telepot.message_identifier(
        msg["message"]), reply_markup=None)


def send_contato(msg_id):
    """ Envia o contato do médico para tirar dúvidas"""

    bot.sendMessage(msg_id,
                    "Caso ainda tenha dúvidas, você pode entrar em contato com nosso time de atendimento 👨‍⚕️👩‍⚕️.\n\nPor meio dos contatos telegram abaixo.",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="EQUIPE DE SAÚDE", callback_data="EQUIPE DE SAÚDE pressed")],
                        [InlineKeyboardButton(text="PSICOLÓGOS", callback_data="PSICOLÓGOS pressed")]]))


def send_contatos_medicos_enfermeiros(msg):
    remove_buttons(msg)
    bot.sendMessage(
        msg['message']['chat']['id'], text="Lista de contatos de Médicos e Enfermeiros para lhe atender:" +
        "\n\n[ https://t.me/medicouea ]\n\n[ https://t.me/medicouea ]\n\n[ https://t.me/medicouea ]\n",
        parse_mode="Markdown")


def send_contatos_alunos_tutores(msg):
    remove_buttons(msg)
    bot.sendMessage(
        msg['message']['chat']['id'], text="Lista de contatos de Alunos e Tutores para lhe atender:" +
        "\n\n[ https://t.me/medicouea ]\n\n[ https://t.me/medicouea ]\n\n[ https://t.me/medicouea ]\n",
        parse_mode="Markdown")


def send_medidas(msg_id):
    bot.sendMessage(msg_id,
                    "Obrigado por responder!😁\n" +
                    "Não esqueça de:\n\n" +
                    "*1.* Lave bem as mãos com água e sabão 🤲🧼🚰 (ou use álcool e gel 👏🧴)\n" +
                    "\n*2.* Cubra nariz e boca ao espirrar e tossir 🤧😣💦\n" +
                    "\n*3.* Evite aglomerações se estiver doente 🙂🤒🙂\n" +
                    "\n*4.* Mantenha os ambientes bem ventilados 🖼️🍃\n" +
                    "\n*5.* Não compartilhe objetos pessoais 🙂🍽️😀\n\n" +
                    "Sair de casa só quando necessário e de máscara 😷, respeite o período de quarentena por sua saúde e de seu próximo 😉👍",
                    parse_mode="Markdown")


def menu_bot_chat(msg):
    global user
    global gravidade
    global recomendar
    global fim_questionario
    """ Função de Menu do Bot """

    bot.sendMessage(
        msg['chat']['id'],
        text="ATENÇÃO VERSÃO DE TESTES, NÃO OFICIAL!\n\nSeja Bem-vindo *" + get_user_name(msg) + "*\n" +
        "\nEu sou o *CovidBot da UEA 👉😁👈* e vou realizar a sua *Triagem Virtual.* Para isso irei fazer uma série de perguntas direcionadas.\n" +
        "\nQuando estiver pronto, aperte em *COMEÇAR* 😁👍",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="COMEÇAR",
                                  callback_data="COMEÇAR pressed")],
            [InlineKeyboardButton(text="CRÉDITOS",
                                  callback_data="CRÉDITOS pressed")]
        ]))

    user["nome"] = get_user_name(msg)
    gravidade = 0
    recomendar = False
    fim_questionario = False


def sub_menu(msg):
    remove_buttons(msg)
    bot.sendMessage(
        msg['message']['chat']['id'], text="Se você deseja obter informações sobre covid-19 acesse:\nhttps://coronavirus.saude.gov.br" +
        "\n\nSe deseja para triagem online e atendimento remoto clique em um dos botões abaixo 🙂:",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="PEDIATRIA",
                                  callback_data="CRIANÇA pressed")],
            [InlineKeyboardButton(text="CLÍNICO GERAL",
                                  callback_data="ADULTO pressed")],
            [InlineKeyboardButton(text="PSICOLOGIA",
                                  callback_data="PSICOLOGIA pressed")]]))


# FORMATAÇÃO DAS PERGUNTAS E MENSAGENS
def psicologia(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "A *UEA* oferece um *serviço de apoio emocional* por meio de uma equipe de psicólogos." +
                    "\nPara atendimento acesso *click no link abaixo* que você será redirecionado para o *serviço de atendimento via Whatsapp*.\n\n o link vai estar aqui",
                    parse_mode="Markdown")


def creditos(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "Segue abaixo o nome das pessoas que participaram no meu desenvolvimento 😊\n\n" +
                    "Prof. Dr. Fábio Santos da Silva" +
                    "\nErik Atilio Silva Rey" +
                    "\nOscar de Menezes Neto" +
                    "\nRamayna Menezes" +
                    "\nJorge Procópio" +
                    "\nProfa. Mariana Broker" +
                    "\nProfa. Waldeyde Magalhães" +
                    "\nProfa. Dra Elielza Guerreiro Menezes" +
                    "\nProf. Dr. Darlisom Sousa Ferreira",
                    parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="⬅ VOLTAR", callback_data="VOLTAR pressed")]]))


def idade_user_crianca(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 1/3*\n\nA criança tem *menos de 5 anos* de idade? 🤔", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM IDADE 5 pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO IDADE 5 pressed")]]))


def sintomas_user_crianca(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 2/3*\n\nA criança tem algum desses sintomas? 🤔" +
                    "\n\n*Febre*\n*Tosse*\n*Dor de garganta*\n*Dificuldade respiratória*\n", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM SINTOMAS CRIANÇA pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO SINTOMAS CRIANÇA pressed")]]))


def sensacao_user_crianca(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 3/3*\n\nA criança apresenta falta de ar, sensação de desmaio?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM SENSAÇÃO CRIANÇA pressed"),
                            InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO SENSAÇÃO CRIANÇA pressed")]]))


def indicacao_user_crianca(msg_id):
    bot.sendMessage(msg_id,
                    "Obrigado por responder!😁\n" +
                    "Fique de olho no que deve ser evitado:\n\n" +
                    "*1.* Não chamar coleguinha ou visitas para casa\n" +
                    "\n*2.* Não sair para parquinho, playground ou para qualquer outra atividade externa\n" +
                    "\n*3.* Manter distância dos idosos que estiverem em casa\n",
                    parse_mode="Markdown")


def idade_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 1/13*\n\nQual seria sua faixa de idade em anos? 🤔", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Entre 18 a 39 anos 👨🏻",
                                              callback_data="IDADE ADULTO pressed")],
                        [InlineKeyboardButton(text="Entre 40 a 59 anos 👨🏻‍🦳",
                                              callback_data="MEIA IDADE pressed")],
                        [InlineKeyboardButton(text="Mais de 60 anos 👴🏻",
                                              callback_data="IDADE IDOSO pressed")]
                    ]))


def sexo_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 2/13*\n\nQual é o seu gênero? 🤔", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
                        text="♂️ Masculino", callback_data="SEXO_MASCULINO pressed"),
                        InlineKeyboardButton(text="♀️ Feminino", callback_data="SEXO_FEMININO pressed")]]))


def gestante_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta extra/13*\n\nVocê por acaso é *Gestante*? 🤰", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM GESTANTE pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO GESTANTE pressed")]]))


def febre_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 3/13*\n\nVocê está com *Febre*? 🤒", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM FEBRE pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO FEBRE pressed")]]))


def dor_cabeca_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 4/13*\n\nVocê está sentindo *Dor de Cabeça*? 😣", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM DOR CABEÇA pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO DOR CABEÇA pressed")]]))


def coriza_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 5/13*\n\nVocê está com algum desses sintomas? 🤔\n\n*Secreção Nasal*\n*Espirros*\n*Perda de Olfato e Paladar*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM CORIZA pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO CORIZA pressed")]]))


def dor_garganta_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 6/13*\n\nEstá sentindo *Dor ou Irritação na Garganta*? 🤨", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM DOR NA GARGANTA pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO DOR NA GARGANTA pressed")]]))


def tosse_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 7/13*\n\nVocê está com *Tosse Seca*? 🤔", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM TOSSE pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO TOSSE pressed")]]))


def dificuldade_respiratoria_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 8/13*\n\nApresenta *Dificuldade Respiratória*? 🤔", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM DIFICULDADE RESPIRATORIA pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO DIFICULDADE RESPIRATORIA pressed")]]))


def dor_no_corpo_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 9/13*\n\nVocê está sentindo *Dores no corpo*? 😖", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM DOR NO CORPO pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO DOR NO CORPO pressed")]]))


def diarreia_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 10/13*\n\nVocê está sentindo *Diarreia*? 🤔", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM DIARREIA pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO DIARREIA pressed")]]))


def peito_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 11/13*\n\nEstá se sentindo *Dor no peito*? 🤔", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM DOR NO PEITO pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO DOR NO PEITO pressed")]]))


def historico_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 12/13*\n\nEsteve em contato próximo de caso suspeito para o coronavírus (COVID-19), nos últimos 14 dias anteriores ao aparecimento dos sinais ou sintomas? 🙁", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM HISTORICO pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO HISTORICO pressed")]]))


def historico02_user(msg):
    remove_buttons(msg)
    bot.sendMessage(msg['message']['chat']['id'],
                    "*Pergunta 13/13*\n\nEsteve em contato próximo de caso confirmado de coronavírus (COVID-19) em laboratório, nos últimos 14 dias anteriores ao aparecimento dos sinais ou sintomas? 🙁", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="✅ SIM", callback_data="SIM HISTORICO02 pressed"),
                         InlineKeyboardButton(text="❌ NÃO", callback_data="NÃO HISTORICO02 pressed")]]))


def unidade_user(msg):
    bot.sendMessage(msg['message']['chat']['id'],
                    "Obrigado por responder!\nAgora permita-me encontrar a unidade atendimento perto de você 😁",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="BUSCAR UNIDADE MAIS PRÓXIMA",
                                              callback_data="UNIDADE MAIS PROXIMA pressed")]]))

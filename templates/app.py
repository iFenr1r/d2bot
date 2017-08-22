#!/usr/bin/env python
# -*- coding: utf-8 -*
from __future__ import print_function
import od_python
import time
import json
from flask import jsonify, Flask
import csv
import sys
from od_python.rest import ApiException
from pprint import pprint
from watson_developer_cloud import ConversationV1

app = Flask(__name__)
Playerapi = od_python.PlayersApi()
Heroapi = od_python.HeroesApi()
Herostats = od_python.HeroStatsApi()

@app.route('/')
def hello_world():
    return render_template('index.html')

def maisjogados(ID):
    try:
        print("Herois mais jogados:")
        api_stats = Playerapi.players_account_id_heroes_get(ID)
        api_heroi = Heroapi.heroes_get()
        api_hero_image = Herostats.hero_stats_get()
        m = 1
        for i in range(0,19):
            if api_stats[i].hero_id > 23:
                m = 2
            else:
                m =1
            nomehero = str(api_heroi[api_stats[i].hero_id - m].localized_name)
            icone = str(api_hero_image[api_stats[i].hero_id - m].icon)
            jogadas = str(api_stats[i].games)
            porcentagem = str(round(float(api_stats[i].win) / float(api_stats[i].games) * 100,1))

            print("Heroi: " + nomehero + " | Icone: " + icone + " | Partidas jogadas: "+ jogadas + " | % Vitoria: " + porcentagem)
    except ApiException as e:
        print("Exception when calling BenchmarksApi->benchmarks_get: %s\n" % e)
#PEGA MMR ESTIMADO
def perfil(ID):
    try:
        api_response = Playerapi.players_account_id_get(ID)
        print("NICKNAME: "+api_response.profile.personaname)
        print("MMR ESTIMADO: "+ str(api_response.mmr_estimate.estimate))
        print("MMR SOLO: "+str(api_response.solo_competitive_rank))
        maisjogados(ID)
    except ApiException as e:
        print("Exception when calling BenchmarksApi->benchmarks_get: %s\n" % e)

def herostats(id_heroi):
    try: 
        # GET /heroStats
        if id_heroi > 23:
            id_heroi = id_heroi-1
        api_response = Herostatsapi.heroes_get()
        print("Heroi: " +str(api_response[id_heroi-1].localized_name))
        print("ID: "  + str(int(api_response[id_heroi-1].id)))
    except ApiException as e:
        print("Exception when calling HeroStatsApi->hero_stats_get: %s\n" % e)
    
conversation = ConversationV1(
  username='a33eb2c9-d218-4e05-a8ff-a46b59c5c3b1',
  password='VATP3XEHsrPL',
  version='2017-05-26'
)

context = {}

workspace_id = '96cbce3b-2fd3-49b0-ad57-da62c33547ee'

while True:
    user = raw_input()
    response = conversation.message(
      workspace_id=workspace_id,
      message_input={'text': user},
      context=context
    )
    context = response['context']

    #se há intenções e dialogo
    if response['intents'] or response['entities']:

        if response['intents']:
            intent = (json.dumps(response['intents'][0]['intent'],indent = 2))
            intent = intent[1:-1]
        dialog = (json.dumps(response['output']['nodes_visited'][0],indent = 2))
        dialog = dialog[1:-1]

        #se há resesposta à intenção
        if response['output']['text']:
            resposta = json.dumps(response['output']['text'][0],sort_keys=True, indent=4)
            resposta = resposta[1:-1]
            resposta = resposta.encode('utf-8')
            print (resposta.decode('unicode-escape'))

        #se entrou no nó x,y,z
        if dialog == "perfil_e_id":
            ID = (json.dumps(response['entities'][0]['value'],indent = 2))
            ID = ID[1:-1]
            print ("ID : " + ID)
            perfil(ID)
            
        elif dialog == "perfil":
            ID = raw_input()
            print ("ID : " + ID)
            perfil(ID)
            
        elif dialog == "heroi":
            ID = (json.dumps(response['entities'][0]['value']))
            ID = ID[1:-1]
            herostats(int(ID))
            
        elif dialog == "counterheroi":
            ID = (json.dumps(response['entities'][0]['value']))
            ID = ID[1:-1]
            herostats(int(ID))

    else:
        response = json.dumps(response['output']['text'][0],sort_keys=True, indent=4)
        resposta = resposta[1:-1]
        response = response.encode('utf-8')
        print (response.decode('unicode-escape'))
     




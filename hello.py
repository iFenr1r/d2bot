#!/usr/bin/env python
# -*- coding: utf-8 -*
from __future__ import print_function
from cloudant import Cloudant
import atexit
import cf_deployment_tracker
import os
import od_python
import time
import json
from flask import jsonify, Flask, current_app, render_template, request, json
import csv
import sys
from od_python.rest import ApiException
from pprint import pprint
from flask_cors import CORS, cross_origin
from watson_developer_cloud import ConversationV1

# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
Playerapi = od_python.PlayersApi()
Heroapi = od_python.HeroesApi()
Herostats = od_python.HeroStatsApi()

db_name = 'mydb'
client = None
db = None

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

# On Bluemix, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

def maisjogados(ID):
    try:
        maisjogados = ("<div class='row'><div class='col-sm-12'><p class='text-center nomeplayer' id='nome'>Herois mais jogados:</p></div>")
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

            maisjogados = maisjogados + ("<div class='row'><div class='col-sm-12'><p class='text-center nomeplayer' id='hero'>Heroi: " + nomehero + " Icone: <img src='http://cdn.dota2.com" + icone + "'> Partidas jogadas: "+ jogadas + " % Vitoria: " + porcentagem+"</p></div>") 
        return maisjogados
    except ApiException as e:
        print("Exception when calling BenchmarksApi->benchmarks_get: %s\n" % e)

#PEGA MMR ESTIMADO
def perfil():
    return "OLA PORRA"
def perfill(id_player):
    try:
        api_response = Playerapi.players_account_id_get(id_player)
        resp = ("<div class='row'><div class='col-sm-4'><p class='text-center nomeplayer' id='nome'>NICKNAME: "+api_response.profile.personaname+"</p></div>")
        resp = resp + ("<div class='col-sm-4'><p class='text-center nomeplayer' id='nome'>MMR ESTIMADO: "+ str(api_response.mmr_estimate.estimate)+"</p></div>")
        resp = resp + ("<div class='col-sm-4'><p class='text-center nomeplayer' id='nome'>MMR SOLO: "+str(api_response.solo_competitive_rank)+"</p></div>")
        resp = resp + str(maisjogados(id_player))
        return resp
    except ApiException as e:
        print("Exception when calling BenchmarksApi->benchmarks_get: %s\n" % e)

def herostats(id_heroi):
    try: 
        # GET /heroStats
        if id_heroi > 23:
            id_heroi = id_heroi-1
        api_response = Heroapi.heroes_get()
        resp = ("Heroi: " + str(api_response[id_heroi-1].localized_name))
        resp = resp + ("\nID: "  + str(api_response[id_heroi-1].id))
        return resp
    except ApiException as e:
        print("Exception when calling HeroStatsApi->hero_stats_get: %s\n" % e)

        
@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/', methods=['POST', 'GET'])
@cross_origin()
def bot():
    texto = request.form['text']
    print(texto)
    conversation = ConversationV1(
      username='a33eb2c9-d218-4e05-a8ff-a46b59c5c3b1',
      password='VATP3XEHsrPL',
      version='2017-05-26'
    )

    context = {}

    workspace_id = '96cbce3b-2fd3-49b0-ad57-da62c33547ee'   

    user = texto
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
            resp = (resposta.decode('unicode-escape'))

        #se entrou no nó x,y,z
        if dialog == "perfil_e_id":
            ID = (json.dumps(response['entities'][0]['value'],indent = 2))
            ID = ID[1:-1]
            print (ID)
            resp = perfill(ID)
            
        elif dialog == "perfil":
            return resp
            ID = texto
            print ("Ikrl : " + ID)
            resp = perfil()
            
        elif dialog == "heroi":
            ID = (json.dumps(response['entities'][0]['value']))
            ID = ID[1:-1]
            resp = herostats(int(ID))
            return resp
            
        elif dialog == "counterheroi":
            ID = (json.dumps(response['entities'][0]['value']))
            ID = ID[1:-1]
            resp = herostats(int(ID))
            return resp

    else:
        resposta = json.dumps(response['output']['text'][0],sort_keys=True, indent=4)
        resposta = resposta[1:-1]
        resposta = resposta.encode('utf-8')
        resp = (resposta.decode('unicode-escape'))

    print (resp)
    return resp
    

if __name__ == "__main__":
    app.run()




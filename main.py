__author__='thiagocastroferreira'

from flask import Flask, jsonify, request
from mongoengine import *

connect('betinha', host='mongodb+srv://betinha:neblTwI1xbP5Ryp0@cluster0.pc12b.mongodb.net/<dbname>?retryWrites=true&w=majority')

app = Flask(__name__)

class User(Document):
    nome = StringField()
    sexo = StringField()
    idade = IntField()
    raca = StringField()
    peso = FloatField()
    altura = FloatField()
    abdomen = FloatField()
    historico = BooleanField()
    pressao = BooleanField()
    gestacional = BooleanField()
    ativo = BooleanField()
    status = StringField()

def diabetes_status(idade, ativo, raca, peso, altura, abdomen, historico, pressao, gestacional):
    status = 'sem_diabetes'

    if idade < 44:
        if abdomen > 97.5:
            if gestacional:
                status = 'diabetes'
            else:
                status = 'prediabetes'
    else:
        if abdomen > 97.5:
            status = 'diabetes'
        else:
            if idade < 57:
                if historico:
                    if raca == 'branca':
                        if pressao:
                            status = 'diabetes'
                        else:
                            status = 'prediabetes'
                    else:
                        status = 'diabetes'
            else:
                if peso <= 76:
                    if altura <= 160:
                        if historico:
                            status = 'diabetes'
                        else:
                            if pressao:
                                if ativo:
                                    status = 'prediabetes'
                                else:
                                    status = 'diabetes'
                            else:
                                status = 'prediabetes'
                    else:
                        status = 'diabetes'
                else:
                    status = 'prediabetes'
    return status

@app.route('/main', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)

    nome = ''
    contextos = data['queryResult']['outputContexts']
    for contexto in contextos:
        if 'nome' in contexto['parameters']:
            nome = contexto['parameters']['nome']['name']


    parametros = data['queryResult']['parameters']

    gestacional = True if parametros['gestacional'] == 'verdadeiro' else False
    historico = True if parametros['historico'] == 'verdadeiro' else False
    pressao = True if parametros['pressao'] == 'verdadeiro' else False
    peso = parametros['peso']
    altura = parametros['altura']
    abdomen = parametros['abdomen']
    raca = parametros['raca']
    idade = parametros['idade']
    sexo = parametros['sexo']
    ativo = parametros['ativo']

    status = diabetes_status(idade=idade,
                    ativo=ativo,
                    raca=raca,
                    peso=peso,
                    altura=altura,
                    abdomen=abdomen,
                    historico=historico,
                    pressao=pressao,
                    gestacional=gestacional,
                    status=status)

    usuario = User(nome=nome,
         sexo=sexo,
         idade=idade,
         raca=raca,
         peso=peso,
         altura=altura,
         abdomen=abdomen,
         historico=historico,
         pressao=pressao,
         gestacional=gestacional,
         ativo=ativo)
    usuario.save()

    if status == 'sem_diabetes':
        reply = 'Fique tranquilo. Você não tem risco de ter diabetes. Continue se cuidando.'
    elif status == 'prediabetes':
        reply = "Cuidado " + nome +  ". Você tem risco de estar numa condição pré-diabética. Procure ter hábitos mais saudáveis e procure um médico."
    else:
        reply = "Atenção " + nome +  "!!! Você tem risco de estar com diabetes. Procure um médico o mais rápido possível!"

    return jsonify({
        'fulfillmentText': reply
    })
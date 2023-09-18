from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect, jsonify, request
from urllib.parse import unquote
import requests
import json

from sqlalchemy.exc import IntegrityError

from models import Session, Medicamento, DosageUnits, Presentation
#from logger import logger
from schemas import *
from flask_cors import CORS
import datetime
import os

info = Info(title="API gestão Medicamentos", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
medicamento_tag = Tag(name="Medicamento", description="Adição, visualização e remoção de Medicamentos à base")

# definindo o host conforme o tipo de execução
if os.getenv("DOCKER_ENV") == "true":
    HOST = 'proc-cont'
else:
    HOST = '127.0.0.1'


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

@app.post('/medicamento',tags=[medicamento_tag],
          responses={"200":MedicamentoViewSchema,"400":ErrorSchema, "409":ErrorSchema})
def add_medicamento(form: MedicamentoSchema):
    """Adiciona um novo medicamento à base   
    """    
    
    try:
        medicamento = Medicamento(
            brand=form.marca,
            active_ingredient=form.principio_ativo,
            dosage=form.dosagem,
            dosage_unit=DosageUnits(form.unidade_dosagem),
            presentation=Presentation(form.apresentacao),
            quantity=form.quantidade
        )
    except:
        error_msg = "Valores inválidos de parametros para nova instância de Medicamento"
        return {"message": error_msg}, 400

    try:
        # criando conexão com a base
        session = Session()
        # adicionando instancia
        session.add(medicamento)
        # efetivando o camando de adição de instancia
        session.commit()
        return apresenta_medicamento(medicamento), 200

    except IntegrityError as e:
        error_msg = "Medicamento com mesmo id já salvo na base :/"
        return {"message": error_msg}, 409   
    
    
    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo Medicamento :/"
        return {"message": error_msg}, 400

@app.get('/medicamento', tags=[medicamento_tag],
         responses={"200":MedicamentoViewSchema,"400":ErrorSchema, "404":ErrorSchema})
def get_medicamento(query: MedicamentoBuscaIDSchema):
    """Retorna medicamento pelo seu id
    """
    try:
        # criando conexão com o banco
        session = Session()
        # buscando todas as instâncias ativas
        medicamento = session.query(Medicamento).filter(Medicamento.is_active == True, Medicamento.medicament_id == query.id).first()
        if not medicamento:
            error_msg = 'Nenhum medicamento encontrado com o id'
            return {"message": error_msg},404
        else:
            #retorna o medicamento
            return apresenta_medicamento(medicamento), 200
    except Exception as e:
        error_msg = "Não foi possível realizar a consulta de medicamento"
        return {"message": error_msg}, 400

@app.get('/all_medicamentos',tags=[medicamento_tag],
         responses={"200":MedicamentoListViewSchema,"400":ErrorSchema, "404":ErrorSchema})
def get_all_medicamentos():
    """Retorna todos os medicamentos cadastrados no banco
    """
    try:
        # criando conexão com o banco
        session = Session()
        # buscando todas as instâncias ativas
        medicamentos = session.query(Medicamento).filter(Medicamento.is_active == True).order_by(Medicamento.created_at.asc()).all()

        if not medicamentos:
            error_msg = 'Nenhum medicamento encontrado'
            return {"message": error_msg},404
        else:
            #retorna os medicamentos
            return apresenta_medicamentos(medicamentos), 200
    except Exception as e:
        error_msg = "Não foi possível realizar a consulta de medicamentos"
        return {"message": error_msg}, 400

def change_quantities(body: MedicamentoListConsomeRepoeQtdadeSchema,is_refilling: bool):
    try:        
        #pegando todos os ids
        list_ids = [obj.id for obj in body.medicamentos]
        # criando conexão com o banco
        session = Session()
        # buscando todas as instâncias ativas
        medicamentos = session.query(Medicamento).filter(Medicamento.is_active == True, Medicamento.medicament_id.in_(list_ids)).order_by(Medicamento.created_at.asc()).all()        

        if not medicamentos:
            error_msg = 'Nenhum medicamento encontrado com o id'
            return {"message": error_msg},404
        else:            
            # Criando um dicionário para mapear IDs de medicamentos para as instâncias correspondentes
            medicamentos_dict = {medicamento.medicament_id: medicamento for medicamento in medicamentos}
            
            if len(medicamentos_dict) != len(list_ids):
                # Nem todos os medicamentos foram encontrados
                missing_ids = set(list_ids) - set(medicamentos_dict.keys())
                error_msg = f'Medicamentos não encontrados para os IDs: {missing_ids}'
                return {"message": error_msg}, 404

            for el in body.medicamentos:
                # Recupera o medicamento com base no id
                medicamento = medicamentos_dict[el.id]
                # Aumenta ou diminui a quantidade de acordo com o formulário
                if is_refilling:
                    medicamento.quantity += el.consumed_refilled_quantity
                else:
                    if el.consumed_refilled_quantity > medicamento.quantity:
                        # Retorna erro se o consumo for maior que o estoque para qualquer um dos medicamentos
                        error_msg = f'Consumo do medicamento {el.id} maior que a quantidade em estoque. Nenhum consumo realizado, tente novamente'
                        return {"message": error_msg}, 400
                    else:
                        medicamento.quantity -= el.consumed_refilled_quantity
            session.commit()
            return apresenta_medicamentos(list(medicamentos_dict.values())), 200
    except Exception as e:
        error_msg = "Não foi possível realizar a reposicao/consumo de medicamento"
        return {"message": error_msg}, 400

@app.put('/consome_medicamentos',tags=[medicamento_tag],
         responses={"200":MedicamentoListViewSchema,"400":ErrorSchema, "404":ErrorSchema})
def consume_quantity(body: MedicamentoListConsomeRepoeQtdadeSchema):
    """Decrementa (consome) a quantidade de um ou mais medicamento
    """
    return change_quantities(body=body,is_refilling=False)    

@app.put('/repoe_medicamentos',tags=[medicamento_tag],
         responses={"200":MedicamentoListViewSchema,"400":ErrorSchema, "404":ErrorSchema})
def replace_quantities(body: MedicamentoListConsomeRepoeQtdadeSchema):
    """Aumenta (repoe) a quantidade de um ou mais medicamentos
    """
    return change_quantities(body=body,is_refilling=True)        

@app.delete('/delete_medicamento',tags=[medicamento_tag],
            responses={"200":MedicamentoViewSchema,"400":ErrorSchema, "404":ErrorSchema})
def delete_medicamento(form: MedicamentoBuscaIDSchema):
    """Deleta um medicamento pelo seu ID
    """
    try:
        # criando conexão com o banco
        session = Session()
        # buscando todas a instância ativas
        medicamento = session.query(Medicamento).filter(Medicamento.is_active == True, Medicamento.medicament_id == form.id).first()

        if not medicamento:
            error_msg = 'Nenhum medicamento encontrado com o id'
            return {"message": error_msg},404
        else:
            #busca as prescricoes associadas ao medicamento
            try:
                response = requests.get(f'http://{HOST}:5002/prescricao_medicamento?id={form.id}')
            except Exception as e:
                error_msg = "Serviço de consulta a prescrição inacessível"
                return {"message": error_msg}, 400

            if response.status_code == 404:
                #se não tem nenhuma prescrição associada, pode seguir com a deleção do medicamento
                medicamento.is_active = False

            elif response.status_code == 200:            
                prescricoes = response.json().get("prescricoes")

                #deleta as prescricoes associadas
                headers = {'Content-Type': 'application/json'}
                #monta o payload de delecao de prescricao
                payload = {'ids': [{'id': prescricao['id']} for prescricao in prescricoes]}
                
                try:
                    response = requests.delete(f'http://{HOST}:5002/delete_prescricoes',data=json.dumps(payload),headers=headers)
                except Exception as e:
                    error_msg = "Serviço de deleção de prescrição inacessível"
                    return {"message": error_msg}, 400
                
                if response.status_code != 200:
                    error_msg = "Não foi possível realizar a deleção do medicamento por causa das prescricoes associadas"
                    return {"message": error_msg}, 400
                else:
                    #se conseguiu deletar as prescricoes, deleta o medicamento
                    #desativa o medicamento (soft delete)
                    medicamento.is_active = False
            else:
                #Erro na consulta de prescricoes
                error_msg = "Não foi possível realizar a deleção do medicamento por causa das prescricoes associadas"
                return {"message": error_msg}, 400

        session.commit()
        return apresenta_medicamento(medicamento), 200
                
    
    except Exception as e:
        error_msg = "Não foi possível realizar a deleção do medicamento"
        return {"message": error_msg}, 400
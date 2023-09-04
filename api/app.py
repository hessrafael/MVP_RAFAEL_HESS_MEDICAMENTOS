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

info = Info(title="API gestão Medicamentos", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
medicamento_tag = Tag(name="Medicamento", description="Adição, visualização e remoção de Medicamentos à base")

@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

@app.post('/medicamento',tags=[medicamento_tag])
def add_medicamento(form: MedicamentoSchema):
    """Adiciona um novo medicamento à base   
    """    
    
    try:
        medicamento = Medicamento(
            brand=form.brand,
            active_ingredient=form.active_ingredient,
            dosage=form.dosage,
            dosage_unit=DosageUnits(form.dosage_unit),
            presentation=Presentation(form.presentation),
            quantity=form.quantity
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
        print(e.__str__())
        print(type(e))
        return {"message": error_msg}, 400

@app.get('/medicamento', tags=[medicamento_tag])
def get_medicamento(query: MedicamentoBuscaIDSchema):
    """Retorna medicamento pelo seu id
    """
    try:
        # criando conexão com o banco
        session = Session()
        # buscando todas as instâncias ativas
        medicamento = session.query(Medicamento).filter(Medicamento.is_active == True, Medicamento.medicament_id == query.id).first()
        print(query.id)
        if not medicamento:
            error_msg = 'Nenhum medicamento encontrado com o id'
            return {"message": error_msg},404
        else:
            #retorna o medicamento
            return apresenta_medicamento(medicamento), 200
    except Exception as e:
        error_msg = "Não foi possível realizar a consulta de medicamento"
        return {"message": error_msg}, 400

@app.get('/all_medicamentos',tags=[medicamento_tag])
def get_all_medicamentos():
    """Retorna todos os medicamentos cadastrados no banco
    """
    try:
        # criando conexão com o banco
        session = Session()
        # buscando todas as instâncias ativas
        medicamentos = session.query(Medicamento).filter(Medicamento.is_active == True).all()

        if not medicamentos:
            error_msg = 'Nenhum medicamento encontrado'
            return {"message": error_msg},404
        else:
            #retorna os medicamentos
            return apresenta_medicamentos(medicamentos), 200
    except Exception as e:
        error_msg = "Não foi possível realizar a consulta de medicamentos"
        print(e.__str__())
        return {"message": error_msg}, 400

def change_quantities(body: MedicamentoListConsomeRepoeQtdadeSchema,is_refilling: bool):
    try:
        #print(request.get_json())
        print(body)
        print(body.medicamentos)
        #pegando todos os ids
        list_ids = [obj.id for obj in body.medicamentos]
        print(list_ids)
        # criando conexão com o banco
        session = Session()
        # buscando todas as instâncias ativas
        medicamentos = session.query(Medicamento).filter(Medicamento.is_active == True, Medicamento.medicament_id.in_(list_ids)).all()        

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

            print('chegou aqui')
            for el in body.medicamentos:
                if el.id in medicamentos_dict:
                    print(el.id)
                    medicamento = medicamentos_dict[el.id]
                    # Aumenta ou diminui a quantidade de acordo com o formulário
                    if is_refilling:
                        medicamento.quantity += el.consumed_refilled_quantity
                    else:
                        medicamento.quantity -= el.consumed_refilled_quantity
            session.commit()
            return apresenta_medicamentos(list(medicamentos_dict.values())), 200
    except Exception as e:
        print(e.__str__())
        error_msg = "Não foi possível realizar a reposicao/consumo de medicamento"
        return {"message": error_msg}, 400

@app.put('/consome_medicamentos',tags=[medicamento_tag])
def consume_quantity(body: MedicamentoListConsomeRepoeQtdadeSchema):
    """Decrementa (consome) a quantidade de um ou mais medicamento
    """
    return change_quantities(body=body,is_refilling=False)
    # try:
    #     # criando conexão com o banco
    #     session = Session()
    #     # buscando todas as instâncias ativas
    #     medicamento = session.query(Medicamento).filter(Medicamento.is_active == True, Medicamento.medicament_id == form.id).first()

    #     if not medicamento:
    #         error_msg = 'Nenhum medicamento encontrado com o id'
    #         return {"message": error_msg},404
    #     else:
    #         if form.consumed_refilled_quantity > medicamento.quantity:
    #             error_msg = "Estoque insuficiente para consumo dessa quantidade de medicamento"
    #             return {"message": error_msg}, 400 
    #         else:
    #             #decrementa a quantidade e retorna
    #             medicamento.quantity-=form.consumed_refilled_quantity            
    #             session.commit()
    #             return apresenta_medicamento(medicamento), 200
    # except Exception as e:
    #     error_msg = "Não foi possível realizar o consumo de medicamento"
    #     return {"message": error_msg}, 400

# @app.put('/repoe_medicamento',tags=[medicamento_tag])
# def replace_quantity(form: MedicamentoConsomeRepoeQtdadeSchema):
#     """Aumenta (repoe) a quantidade de um dado medicamento
#     """
#     try:
#         # criando conexão com o banco
#         session = Session()
#         # buscando todas as instâncias ativas
#         medicamento = session.query(Medicamento).filter(Medicamento.is_active == True, Medicamento.medicament_id == form.id).first()

#         if not medicamento:
#             error_msg = 'Nenhum medicamento encontrado com o id'
#             return {"message": error_msg},404
#         else:            
#             #aumenta a quantidade e retorna
#             medicamento.quantity+=form.consumed_refilled_quantity            
#             session.commit()
#             return apresenta_medicamento(medicamento), 200
#     except Exception as e:
#         error_msg = "Não foi possível realizar a reposicao de medicamento"
#         return {"message": error_msg}, 400

@app.put('/repoe_medicamentos',tags=[medicamento_tag])
def replace_quantities(body: MedicamentoListConsomeRepoeQtdadeSchema):
    """Aumenta (repoe) a quantidade de um ou mais medicamentos
    """
    return change_quantities(body=body,is_refilling=True)
    # try:
    #     #print(request.get_json())
    #     print(body)
    #     print(body.medicamentos)
    #     #pegando todos os ids
    #     list_ids = [obj.id for obj in body.medicamentos]
    #     print(list_ids)
    #     # criando conexão com o banco
    #     session = Session()
    #     # buscando todas as instâncias ativas
    #     medicamentos = session.query(Medicamento).filter(Medicamento.is_active == True, Medicamento.medicament_id.in_(list_ids)).all()        

    #     if not medicamentos:
    #         error_msg = 'Nenhum medicamento encontrado com o id'
    #         return {"message": error_msg},404
    #     else:            
    #         # Criando um dicionário para mapear IDs de medicamentos para as instâncias correspondentes
    #         medicamentos_dict = {medicamento.medicament_id: medicamento for medicamento in medicamentos}
            
    #         if len(medicamentos_dict) != len(list_ids):
    #             # Nem todos os medicamentos foram encontrados
    #             missing_ids = set(list_ids) - set(medicamentos_dict.keys())
    #             error_msg = f'Medicamentos não encontrados para os IDs: {missing_ids}'
    #             return {"message": error_msg}, 404

    #         print('chegou aqui')
    #         for el in body.medicamentos:
    #             if el.id in medicamentos_dict:
    #                 print(el.id)
    #                 medicamento = medicamentos_dict[el.id]
    #                 # Aumenta a quantidade de acordo com o formulário
    #                 medicamento.quantity += el.consumed_refilled_quantity          
    #         session.commit()
    #         return apresenta_medicamentos(list(medicamentos_dict.values())), 200
    # except Exception as e:
    #     print(e.__str__())
    #     error_msg = "Não foi possível realizar a reposicao de medicamento"
    #     return {"message": error_msg}, 400
    

@app.delete('/delete_medicamento',tags=[medicamento_tag])
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
                response = requests.get(f'http://127.0.0.1:5002/prescricao_medicamento?id={form.id}')
            except Exception as e:
                error_msg = "Serviço de consulta a prescrição inacessível"
                return {"message": error_msg}, 400

            if response.status_code == 404:
                #se não tem nenhuma prescrição associada, pode seguir com a deleção do medicamento
                medicamento.is_active = False

            elif response.status_code == 200:            
                prescricoes = response.json().get("prescricoes")
                print(response.json())
                print(prescricoes)
                #deleta as prescricoes associadas
                headers = {'Content-Type': 'application/json'}
                #monta o payload de delecao de prescricao
                payload = {'ids': [{'id': prescricao['id']} for prescricao in prescricoes]}
                
                try:
                    response = requests.delete('http://127.0.0.1:5002/delete_prescricoes',data=json.dumps(payload),headers=headers)
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
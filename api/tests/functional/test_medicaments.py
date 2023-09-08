import os
import json
from conftest import ValueStorage1, ValueStorage2

def test_home_page(test_client):  
    response = test_client.get('/')
    assert response.status_code == 302

def test_add_medicament_sucesso(test_client):
    response = test_client.post('/medicamento',data={
        "principio_ativo":"Paracetamol",
        "marca":"Tylenol",
        "unidade_dosagem":"mg",
        "apresentacao":"comprimido",
        "dosagem": 700,
        "quantidade": 20
    })
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))
    print(response_data)
    assert response_data["principio_ativo"] == "Paracetamol"
    assert response_data["marca"] == "Tylenol"
    assert response_data["unidade_dosagem"] == "mg"
    assert response_data["apresentacao"] == "comprimido"
    assert response_data["dosagem"] == 700
    assert response_data["quantidade"] == 20
    ValueStorage1.id = response_data["id"]

def test_get_medicament(test_client):
    response = test_client.get(f'/medicamento?id={ValueStorage1.id}')
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))
    assert response_data["principio_ativo"] == "Paracetamol"
    assert response_data["marca"] == "Tylenol"
    assert response_data["unidade_dosagem"] == "mg"
    assert response_data["apresentacao"] == "comprimido"
    assert response_data["dosagem"] == 700
    assert response_data["quantidade"] == 20

def test_add_medicament_same_medicament(test_client):
    response = test_client.post('/medicamento',data={
        "principio_ativo":"Paracetamol",
        "marca":"Tylenol",
        "unidade_dosagem":"mg",
        "apresentacao":"comprimido",
        "dosagem": 700,
        "quantidade": 2
    })
    assert response.status_code == 409
    response_data = json.loads(response.data.decode('utf-8'))
    print(response_data)
    assert response_data["message"] == "Medicamento com mesmo id já salvo na base :/"

def test_add_medicament_wrong_presentation(test_client):
    response = test_client.post('/medicamento',data={
        "principio_ativo":"Acido Ascorbico",
        "marca":"Cebion",
        "unidade_dosagem":"mg",
        "apresentacao":"charope",
        "dosagem": 700,
        "quantidade": 2
    })
    assert response.status_code == 400
    response_data = json.loads(response.data.decode('utf-8'))
    print(response_data)
    assert response_data["message"] == "Valores inválidos de parametros para nova instância de Medicamento"

def test_add_medicamento_wrong_dosage_unit(test_client):
    response = test_client.post('/medicamento',data={
        "principio_ativo":"Acido Salicilico",
        "marca":"Aspirina",
        "unidade_dosagem":"m",
        "apresentacao":"comprimido",
        "dosagem": 700,
        "quantidade": 2
    })
    assert response.status_code == 400
    response_data = json.loads(response.data.decode('utf-8'))
    print(response_data)
    assert response_data["message"] == "Valores inválidos de parametros para nova instância de Medicamento"

def test_consume_medicament(test_client):
    response = test_client.put('/consome_medicamentos',json={
        "medicamentos": [
            {
                "consumed_refilled_quantity": 3,
                "id": ValueStorage1.id
            }
        ]
    })
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))
    assert response_data["medicamentos"][0]["id"] == ValueStorage1.id
    assert response_data["medicamentos"][0]["quantidade"] == 17
    assert len(response_data["medicamentos"]) == 1

def test_refill_medicament(test_client):
    response = test_client.put('/repoe_medicamentos',json={
        "medicamentos": [
            {
                "consumed_refilled_quantity": 3,
                "id": ValueStorage1.id
            }
        ]
    })
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))
    assert response_data["medicamentos"][0]["id"] == ValueStorage1.id
    assert response_data["medicamentos"][0]["quantidade"] == 20
    assert len(response_data["medicamentos"]) == 1

def test_consume_more(test_client):
    response = test_client.put('/consome_medicamentos',json={
        "medicamentos": [
            {
                "consumed_refilled_quantity": 21,
                "id": ValueStorage1.id
            }
        ]
    })
    assert response.status_code == 400
    response_data = json.loads(response.data.decode('utf-8'))
    assert response_data["message"] == f'Consumo do medicamento {ValueStorage1.id} maior que a quantidade em estoque. Nenhum consumo realizado, tente novamente'
    

def test_consume_max(test_client):
    response = test_client.put('/consome_medicamentos',json={
        "medicamentos": [
            {
                "consumed_refilled_quantity": 20,
                "id": ValueStorage1.id
            }
        ]
    })
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))
    assert response_data["medicamentos"][0]["id"] == ValueStorage1.id
    assert response_data["medicamentos"][0]["quantidade"] == 0
    assert len(response_data["medicamentos"]) == 1

def test_add_second_medicament(test_client):
    response = test_client.post('/medicamento',data={
        "principio_ativo":"Minoxidil",
        "marca":"Rogaine",
        "unidade_dosagem":"ml",
        "apresentacao":"frasco",
        "dosagem": 500,
        "quantidade": 10
    })
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))
    print(response_data)
    assert response_data["principio_ativo"] == "Minoxidil"
    assert response_data["marca"] == "Rogaine"
    assert response_data["unidade_dosagem"] == "ml"
    assert response_data["apresentacao"] == "frasco"
    assert response_data["dosagem"] == 500
    assert response_data["quantidade"] == 10
    ValueStorage2.id = response_data["id"]

def test_refill_both_medicament(test_client):
    response = test_client.put('/repoe_medicamentos',json={
        "medicamentos": [
            {
                "consumed_refilled_quantity": 20,
                "id": ValueStorage1.id
            },
            {
                "consumed_refilled_quantity": 1,
                "id": ValueStorage2.id
            }
        ]
    })
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))
    assert response_data["medicamentos"][0]["id"] == ValueStorage1.id
    assert response_data["medicamentos"][0]["quantidade"] == 20
    assert response_data["medicamentos"][1]["id"] == ValueStorage2.id
    assert response_data["medicamentos"][1]["quantidade"] == 11
    assert len(response_data["medicamentos"]) == 2

def test_consume_both_medicament_one_more(test_client):
    response = test_client.put('/consome_medicamentos',json={
        "medicamentos": [
            {
                "consumed_refilled_quantity": 20,
                "id": ValueStorage1.id
            },
            {
                "consumed_refilled_quantity": 12,
                "id": ValueStorage2.id
            }
        ]
    })
    assert response.status_code == 400
    response_data = json.loads(response.data.decode('utf-8'))
    assert response_data["message"] == f'Consumo do medicamento {ValueStorage2.id} maior que a quantidade em estoque. Nenhum consumo realizado, tente novamente'

def test_consume_inexistent(test_client):
    response = test_client.put('/consome_medicamentos',json={
        "medicamentos": [
            {
                "consumed_refilled_quantity": 20,
                "id": 1
            },
            {
                "consumed_refilled_quantity": 20,
                "id": 2
            },
            {
                "consumed_refilled_quantity": 1,
                "id": ValueStorage2.id
            }
        ]
    })
    assert response.status_code == 404
    response_data = json.loads(response.data.decode('utf-8'))
    assert response_data["message"] == f"Medicamentos não encontrados para os IDs: {{'1', '2'}}"

def test_consume_both_medicament(test_client):
    response = test_client.put('/consome_medicamentos',json={
        "medicamentos": [
            {
                "consumed_refilled_quantity": 10,
                "id": ValueStorage1.id
            },
            {
                "consumed_refilled_quantity": 5,
                "id": ValueStorage2.id
            }
        ]
    })
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))
    print(ValueStorage1.id)
    print(ValueStorage2.id)
    print(response_data)
    assert response_data["medicamentos"][0]["id"] == ValueStorage1.id
    assert response_data["medicamentos"][0]["quantidade"] == 10
    assert response_data["medicamentos"][1]["id"] == ValueStorage2.id
    assert response_data["medicamentos"][1]["quantidade"] == 6
    assert len(response_data["medicamentos"]) == 2

  

def test_get_all_medicaments(test_client):
    response = test_client.get('/all_medicamentos')
    assert response.status_code == 200
    response_data = json.loads(response.data.decode('utf-8'))
    assert len(response_data["medicamentos"]) == 2
    assert response_data["medicamentos"][0]["principio_ativo"] == "Paracetamol"
    assert response_data["medicamentos"][0]["marca"] == "Tylenol"
    assert response_data["medicamentos"][0]["unidade_dosagem"] == "mg"
    assert response_data["medicamentos"][0]["apresentacao"] == "comprimido"
    assert response_data["medicamentos"][0]["dosagem"] == 700
    assert response_data["medicamentos"][0]["quantidade"] == 10
    assert response_data["medicamentos"][0]["id"] == ValueStorage1.id
    assert response_data["medicamentos"][1]["principio_ativo"] == "Minoxidil"
    assert response_data["medicamentos"][1]["marca"] == "Rogaine"
    assert response_data["medicamentos"][1]["unidade_dosagem"] == "ml"
    assert response_data["medicamentos"][1]["apresentacao"] == "frasco"
    assert response_data["medicamentos"][1]["dosagem"] == 500
    assert response_data["medicamentos"][1]["quantidade"] == 6
    assert response_data["medicamentos"][1]["id"] == ValueStorage2.id
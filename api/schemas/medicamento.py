from pydantic import BaseModel
from typing import List
from models.medicamento import Medicamento

class MedicamentoSchema(BaseModel):
    """ Define como um Medicamento novo deve ser adicionado
    """
    brand : str = 'Tylenol'
    active_ingredient : str = 'Paracetamol'
    dosage : int = 700
    dosage_unit : str = 'mg'
    presentation : str = 'comprimido'
    quantity : int = 10

class MedicamentoViewSchema(BaseModel):
    """ Define como um Medicamento deve ser retornado
    """
    id: str = '206b887e-5465-4e47-b239-17ccc6ebcefa'
    brand : str = 'Tylenol'
    active_ingredient : str = 'Paracetamol'
    dosage : int = 700
    dosage_unit : str = 'mg'
    presentation : str = 'comprimido'
    quantity : int = 10

class MedicamentoListViewSchema(BaseModel):
    """Define como uma Lista de Medicamento deve ser retornada
    """
    medicamentos: List[MedicamentoViewSchema]

class MedicamentoBuscaIDSchema(BaseModel):
    """Define como deve ser feita a busca pelo medicamento
    """
    id: str = '206b887e-5465-4e47-b239-17ccc6ebcefa'

class MedicamentoAlteraQtdadeSchema(BaseModel):
    """Define como uma alteração do valor absoluto do estoque do medicamento deve ser feito
    """
    id: str = '206b887e-5465-4e47-b239-17ccc6ebcefa'
    new_quantity: int = 10

class MedicamentoConsomeRepoeQtdadeSchema(BaseModel):
    """Define como um consumo ou reposição de medicamento deve ser feito
    """
    id: str = '206b887e-5465-4e47-b239-17ccc6ebcefa'
    consumed_refilled_quantity: int = 1

class MedicamentoListConsomeRepoeQtdadeSchema(BaseModel):
    """Define como um consumo ou reposição de mais de um medicamento deve ser feito
    """
    medicamentos: List[MedicamentoConsomeRepoeQtdadeSchema] = [MedicamentoConsomeRepoeQtdadeSchema(),MedicamentoConsomeRepoeQtdadeSchema()]

def apresenta_medicamento(medicamento: Medicamento):
    """Retorna uma visualização do medicamento conforme definido em MedicamentoViewSchema
    """
    return{
        "id": medicamento.medicament_id,
        "marca": medicamento.brand,
        "principio_ativo": medicamento.active_ingredient,
        "dosagem": medicamento.dosage,
        "unidade_dosagem": medicamento.dosage_unit.__str__(),
        "apresentacao": medicamento.presentation.__str__(),
        "quantidade": medicamento.quantity 
    }

def apresenta_medicamentos(medicamentos: List[Medicamento]):
    """Retorna uma visualização em lista conforme definido em MedicamentoListViewSchema
    """
    medicamento_lista = []
    for medicamento in medicamentos:
        medicamento_lista.append(apresenta_medicamento(medicamento))
    return {"medicamentos": medicamento_lista}

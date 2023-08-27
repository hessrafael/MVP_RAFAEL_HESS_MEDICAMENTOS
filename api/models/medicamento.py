from sqlalchemy import Column, String, DateTime, Boolean, Integer, UniqueConstraint, Enum
from datetime import datetime
import uuid
import enum

from  models import Base

class DosageUnits(enum.Enum):
    mg = 'mg'
    mg_per_ml = 'mg/ml'
    ml = 'ml'
    mcg = 'mcg'

    def __str__(self) -> str:
        return self.value

class Presentation(enum.Enum):
    comprimido = 'comprimido'
    capsula = 'capsula'
    frasco = 'frasco'
    tubo = 'tubo' 

    def __str__(self) -> str:
        return self.value

class Medicamento(Base):
    __tablename__ = 'medicament'

    medicament_id = Column(String(36), primary_key =True)
    brand = Column(String,nullable=False)
    active_ingredient = Column(String,nullable=False)
    dosage = Column(Integer,nullable=False)
    dosage_unit = Column(Enum(DosageUnits),nullable=False)
    presentation = Column(Enum(Presentation),nullable=False)
    quantity = Column(Integer,nullable=False)

    created_at = Column(DateTime, default=datetime.now())
    is_active = Column(Boolean, default=True)

    #adicionando a restrição de que não pode ter medicamentos repetidos
    __table_args__ = (UniqueConstraint('brand', 'active_ingredient','dosage','dosage_unit','presentation', name='uq_medicament'),
                      )

    def __init__(self,brand,active_ingredient,dosage,dosage_unit,presentation,quantity):
        self.medicament_id = uuid.uuid4().__str__()
        self.brand = brand
        self.active_ingredient = active_ingredient
        self.dosage = dosage
        self.dosage_unit = dosage_unit
        self.presentation = presentation
        self.quantity = quantity
        
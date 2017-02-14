from sqlalchemy import Column, Integer, String, Text
from base import Base

class GarmentType(Base):
    __tablename__ = 'garment_type'

    type_id = Column(Integer, primary_key=True)
    type_name = Column(String(200))
    type_description = Column(Text)
    use_in_combo_as = Column(Integer)

    def __init__(self, type_name, type_description='', use_in_combo_as=0):
        self.type_name = type_name
        self.type_description = type_description
        self.use_in_combo_as = use_in_combo_as

    def __repr__(self):
        return '<GarmentType(id={}, type_name={}, type_description={}, use_in_combo_as={})>'.format(
                self.type_id, self.type_name, self.type_description,
                self.use_in_combo_as
                )

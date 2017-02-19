from sqlalchemy import Column, String, Integer, Text
from base import Base


class UseInCombo(Base):
    __tablename__ = 'use_in_combo'

    use_in_combo_id = Column(Integer, primary_key=True)
    use_name = Column(String(50))
    use_description = Column(Text)
    field_in_db = Column(String(50))

    def __init__(self, use_name, use_description, field_in_db):
        self.use_name = use_name
        self.use_description = use_description
        self.field_in_db = field_in_db

    def __repr__(self):
        return "<UseInCombo(id='{}', use_name='{}', use_description='{}', field_in_db={})>".format(
                self.use_in_combo_id, self.use_name,
                self.use_description, self.field_in_db
                )

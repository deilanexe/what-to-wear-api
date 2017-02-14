from sqlalchemy import *
from base import Base


class Garment(Base):
    __tablename__ = 'garment'

    garment_id = Column(Integer, primary_key=True)
    garment_type_id = Column(Integer)
    garment_brand_id = Column(Integer)
    garment_color = Column(String(10))
    garment_secondary_color = Column(String(10))
    garment_image_url = Column(String(300))
    last_washed_on = Column(Date)
    purchased_on = Column(Date)
    size = Column(String(200))
    available = Column(Integer)
    retire_date = Column(Date)

    def __init__(self, garment_id, garment_type_id, garment_brand_id):
        self.garment_id = garment_id
        self.garment_type_id = garment_type_id
        self.garment_brand_id = garment_brand_id

    def __repr__(self):
        return "<Garment(id='%s', type id='%s', brand id='%s')>" % (
                self.name, self.fullname, self.password)

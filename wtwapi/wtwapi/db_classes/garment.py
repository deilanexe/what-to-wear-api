from sqlalchemy import Column, Integer, String, Date, ForeignKey
from base import Base


class Garment(Base):
    __tablename__ = 'garment'

    garment_id = Column(Integer, primary_key=True)
    garment_type_id = Column(Integer, ForeignKey("garment_type.type_id"))
    garment_brand_id = Column(Integer)
    garment_color = Column(String(10))
    garment_secondary_color = Column(String(10))
    garment_image_url = Column(String(300))
    last_washed_on = Column(Date)
    purchased_on = Column(Date)
    # size = Column(String(200))
    available = Column(Integer)
    retire_date = Column(Date)

    def __init__(
            self, garment_type_id, garment_color,
            garment_secondary_color, garment_image_url, last_washed_on,
            purchased_on, garment_brand_id=0
            ):
        self.garment_type_id = int(garment_type_id)
        self.garment_brand_id = int(garment_brand_id)
        self.garment_color = garment_color
        self.garment_secondary_color = garment_secondary_color
        self.garment_image_url = garment_image_url
        self.last_washed_on = last_washed_on
        self.purchased_on = purchased_on
        self.available = 1
        self.retire_date = None

    def __repr__(self):
        return "<Garment(id='%s', type id='%s', brand id='%s')>" % (
                self.garment_id, self.garment_type_id, self.garment_brand_id)

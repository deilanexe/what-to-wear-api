from sqlalchemy import *
from base import Base


class GarmentBrand(Base):
    __tablename__ = 'garment_brands'

    brand_id = Column(Integer, primary_key=True)
    brand_name = Column(String(200))
    wiki_article = Column(String(200))
    website_url = Column(String(200))

    def __init__(self, brand_name, wiki_article, website_url):
        self.brand_name = brand_name
        self.wiki_article = wiki_article
        self.website_url = website_url

    def __repr__(self):
        return '<Brand ID {}; Name: {}, In Wikipedia as {}, with website {}'.format(
                self.brand_id,
                self.brand_name,
                self.wiki_article,
                self.website_url
                )

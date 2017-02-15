from sqlalchemy import Column, Integer, Date
from base import Base

class Combo(Base):
    __tablename__ = 'garment_combo'

    g_combo_id = Column(Integer, primary_key=True)
    upper_ext_id = Column(Integer)
    upper_int_id = Column(Integer)
    upper_cov_id = Column(Integer)
    lower_ext_id = Column(Integer)
    lower_acc_id = Column(Integer)
    foot_ext_id = Column(Integer)
    foot_int_id = Column(Integer)
    head_id = Column(Integer)
    used_on = Column(Date)

    def __init__(
            self, used_on, head_id=0, upper_cov_id=0, upper_ext_id=0,
            upper_int_id=0, lower_ext_id=0, lower_acc_id=0,
            foot_ext_id=0, foot_int_id=0
            ):
        self.used_on = used_on
        self.head_id = head_id
        self.upper_cov_id = upper_cov_id
        self.upper_ext_id = upper_ext_id
        self.upper_int_id = upper_int_id
        self.lower_ext_id = lower_ext_id
        self.lower_acc_id = lower_acc_id
        self.foot_int_id = foot_int_id
        self.foot_ext_id = foot_ext_id

    def __repr__(self):
        return '<GarmentCombo(id={}, hid={}, ucid={}, ueid={}, uiid={}, leid={}, laid={}, fiid={}, feid={}; used_on={})>'.format(
                self.g_combo_id, self.head_id, self.upper_cov_id,
                self.upper_ext_id, self.upper_int_id, self.lower_ext_id,
                self.lower_acc_id, self.foot_int_id, self.foot_ext_id,
                self.used_on
                )

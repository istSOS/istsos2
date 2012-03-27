from istsostables import *
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()
session.query(ObservedProperty).all()


proc = session.query(Procedures).filter(name_prc="P_TRE").one()


session.query(Measure).filter(Measure.val_msr>100).first().val_msr

s=session.query(Procedure).first().foi
session.scalar(s.geom_foi.geometry_type)

s=session.query(Position).first().positions
session.scalar(s.geom_foi.geometry_type)

proc=session.query(Procedure).filter(Procedure.name_prc==u'A_GNO_GNO').one()
proc.name_prc


s=session.query(Measure).first()

s=session.query(EventTime).first()


proc = session.query(Procedure).filter(Procedure.name_prc==u'P_TRE').one()
obspr = session.query(ObservedProperty).filter(ObservedProperty.name_opr.ilike('%rainfall')).one()
session.query(Measure).first().event_time.time_eti

session.query(Measure).filter(and_(Measure.event_time.time_eti<'2011-11-01T12:00+01',Measure.event_time.time_eti>'2010-01-01T23:00+01')).limit(100)

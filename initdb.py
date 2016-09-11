from database import Base, User, Item
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///app.db')
Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
sessiondb = DBSession()

default_user = User('student','student','student@uczelnia.edu.pl')
sessiondb.add(default_user)

sessiondb.add(Item('Przedmiot 1','80'))
sessiondb.add(Item('Przedmiot 2','120'))
sessiondb.add(Item('Przedmiot 3','90'))
sessiondb.add(Item('Przedmiot 4','75'))
sessiondb.add(Item('Przedmiot 5','40'))

sessiondb.commit()







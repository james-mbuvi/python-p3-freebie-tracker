from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    founding_year = Column(Integer)

    def __repr__(self):
        return f"<Company(name='{self.name}', founding_year={self.founding_year})>"

    @property
    def freebies(self):
        return [freebie for dev in self.devs for freebie in dev.freebies]

    @property
    def devs(self):
        return [freebie.dev for freebie in self.freebies]

    def give_freebie(self, dev, item_name, value):
        new_freebie = Freebie(dev=dev, company=self, item_name=item_name, value=value)
        dev.freebies.append(new_freebie)


class Dev(Base):
    __tablename__ = 'devs'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return f"<Dev(name='{self.name}')>"

    @property
    def freebies(self):
        return [freebie for freebie in self.freebies_given + self.freebies_received]

    @property
    def freebies_given(self):
        return [freebie for freebie in self.freebies if freebie.dev != self]

    @property
    def freebies_received(self):
        return [freebie for freebie in self.freebies if freebie.dev == self]

    @property
    def companies(self):
        return [freebie.company for freebie in self.freebies]

    def received_one(self, item_name):
        return any(freebie.item_name == item_name for freebie in self.freebies)

    def give_away(self, dev, freebie):
        if freebie.dev == self:
            freebie.dev = dev


class Freebie(Base):
    __tablename__ = 'freebies'

    id = Column(Integer, primary_key=True)
    dev_id = Column(Integer, ForeignKey('devs.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    item_name = Column(String)
    value = Column(Integer)

    dev = relationship('Dev', backref='freebies_given', foreign_keys=[dev_id])
    company = relationship('Company', backref='freebies_given')

    def print_details(self):
        return f"{self.dev.name} owns a {self.item_name} from {self.company.name}"


# Assuming you have configured your database engine and session
engine = create_engine('sqlite:///example.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

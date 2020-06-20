from config import SQLALCHEMY_URI
from os import environ
from datetime import datetime
from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String,
                        create_engine, Float, DateTime, Table,
                        PrimaryKeyConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

# Many to Many Table the schedule football and the table User
assotiate_table = Table('team_favorite', Base.metadata,
                        Column('fav_user_id', Integer,
                               ForeignKey('user_data.id')),
                        Column('fav_team_id', Integer,
                               ForeignKey('champion_league.id')),
                        PrimaryKeyConstraint('fav_user_id', 'fav_team_id')
                        )

class TeamSchedule(Base):
    """The main responsibility of this for define the table of schedule football.
    If table changes the view component should changes.
    """

    __tablename__ = 'champion_league'

    id = Column(Integer, primary_key=True, nullable=False)

    round_number = Column(String)
    date_time = Column(DateTime(timezone=True))
    location = Column(String)
    home_team = Column(String)
    away_team = Column(String)
    group_team = Column(String)
    result_final = Column(String)
    user = relationship('UserData', secondary=lambda: assotiate_table,
                        backref='champion_league', cascade='all, delete',single_parent=True)

class UserData(Base):
    """The main responsibility of this for the table a user"""

    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True, nullable=False)

    username = Column(String)
    user_id = Column(Integer)
    chat_id = Column(Integer)
    contact = Column(String)
    name_contact = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    tzinfo = Column(String)
    signup_date = Column(DateTime, default=datetime.utcnow())
    signup_status = Column(Boolean)
    # Persistance PSQL
    job_context = Column(Boolean)

engine = create_engine(SQLALCHEMY_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
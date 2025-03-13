from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model):
    __tablename__ = 'heroes'

    serialize_rules=('-hero_powers',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)


    hero_powers=db.relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'super_name': self.super_name,
            'hero_powers': [hp.to_dict() for hp in self.hero_powers]

        }


    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    
    hero_powers=db.relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')


    @validates('description')
    def validate_description(self, key, description):
        if len(description) < 20:
            raise ValueError("Description must be at least 20 characters")
        return description






    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
    

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    hero_id=db.Column(db.Integer, db.ForeignKey("heroes.id"))
    power_id=db.Column(db.Integer, db.ForeignKey("powers.id"))

    
    hero=db.relationship('Hero', back_populates='hero_powers')
    power=db.relationship('Power', back_populates='hero_powers')




    @validates('strength')
    def validate_strength(self, key, strength):
        allowed_strengths = ['Strong', 'Weak', 'Average']
        if strength not in allowed_strengths:
            raise ValueError(f"Strength must be one of {allowed_strengths}") 
        return strength

    def to_dict(self):
        return {
            'id': self.id,
            'strength': self.strength,
            'hero_id': self.hero_id,
            'power_id': self.power_id,
            'hero': {
                'id': self.hero.id,
                'name': self.hero.name,
                'super_name': self.hero.super_name
            },
            'power': {
                'id': self.power.id,
                'name': self.power.name,
                'description': self.power.description
            }
        }

    def __repr__(self):
        return f'<HeroPower {self.id}>'

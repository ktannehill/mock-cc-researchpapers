from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# Add models here

class Research(db.Model, SerializerMixin):
    __tablename__ = 'researches'

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String)
    year = db.Column(db.Integer)
    page_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    research_authors = db.relationship("ResearchAuthors", back_populates="research", cascade="all, delete-orphan")
    authors = association_proxy("research_authors", "author")
    serialize_rules = ("-research_authors.research", "-created_at", "-updated_at")

    @validates('year')
    def validate_year(self, _, year):
        if len(str(year)) != 4:
            raise ValueError("Year must be four digits")
        return year



class Author(db.Model, SerializerMixin):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    research_authors = db.relationship("ResearchAuthors", back_populates="author", cascade="all, delete-orphan")
    researches = association_proxy("research_authors", "research")
    serialize_rules = ("-research_authors.author", "-created_at", "-updated_at")

    @validates('field_of_study')
    def validate_field(self, _, field):
        fields = ['AI', 'Robotics', 'Machine Learning', 'Vision', 'Cybersecurity']
        if field not in fields:
            raise ValueError(f"Field must be one of: {fields}")
        return field



class ResearchAuthors(db.Model, SerializerMixin):
    __tablename__ = 'research_authors'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    research_id = db.Column(db.Integer, db.ForeignKey('researches.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    author = db.relationship("Author", back_populates="research_authors")
    research = db.relationship("Research", back_populates="research_authors")

    serialize_rules = ("-author.research_authors", "-research.research_authors", "-created_at", "-updated_at")


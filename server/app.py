#!/usr/bin/env python3

from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Research, Author, ResearchAuthors

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class Researches(Resource):
    def get(self):
        all_research = [research.to_dict(rules=("-research_authors",)) for research in Research.query.all()]
        return all_research, 200
    
api.add_resource(Researches, '/research')

class ResearchById(Resource):
    def get(self, id):
        if research := db.session.get(Research, id):
            return research.to_dict(rules=("-research_authors", "authors", "-authors.research_authors")), 200
        return {'error': 'Research paper not found'}, 404
    
    def delete(self, id):
        research = Research.query.get_or_404(id,
            description=f"Research {id} not found")
        try:
            db.session.delete(research)
            db.session.commit()
            return {}, 204
        except:
            db.session.rollback()
            return {'error': 'Research paper not found'}, 400
        
api.add_resource(ResearchById, '/research/<int:id>')

class Authors(Resource):
    def get(self):
        authors = [author.to_dict(rules=("-research_authors",)) for author in Author.query.all()]
        return authors, 200
    
api.add_resource(Authors, "/authors")

class ResearchAuthorsRoute(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_ra = ResearchAuthors(**data)
            db.session.add(new_ra)
            db.session.commit()
            return new_ra.to_dict(only=("author",)), 201
        except:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400

api.add_resource(ResearchAuthorsRoute, "/research_author")


if __name__ == '__main__':
    app.run(port=5555, debug=True)

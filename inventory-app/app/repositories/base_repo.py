"""
PATRON REPOSITORY (base)
Centraliza el acceso a datos y desacopla los controladores
de SQLAlchemy. Los controladores no importan 'db' directamente;
solo usan metodos del repositorio correspondiente.
"""
from app.extensions import db


class BaseRepository:
    def __init__(self, model):
        self._model = model

    def get_by_id(self, record_id):
        return self._model.query.get(record_id)

    def get_all(self):
        return self._model.query.all()

    def save(self, instance):
        db.session.add(instance)
        db.session.commit()
        return instance

    def delete(self, instance):
        db.session.delete(instance)
        db.session.commit()

    def commit(self):
        db.session.commit()

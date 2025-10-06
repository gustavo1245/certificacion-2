#base/models/cita_model.py

#modelo de cita
#Encapsulamos la logica de las citas y favoritos en la base de datos

from base.config.mysqlconnection import connectToMySQL
from flask import flash

class Citas:
    @classmethod
    def obtener_por_autor(cls, autor_id):
        query = "SELECT * FROM citas WHERE autor_id = %(autor_id)s;"
        data = {'autor_id': autor_id}
        resultado = connectToMySQL(cls.db).query_db(query, data)
        return [cls(row) for row in resultado]
    db = "proyecto_crud"

    def __init__(self, data):
        self.id = data['id']
        self.cita = data.get('cita') or data.get('citas')
        self.autor_id = data['autor_id']
        self.creado_en = data['creado_en']
        self.actualizado_en = data['actualizado_en']

    @classmethod
    def guardar_cita(cls, data):
        query = "INSERT INTO citas(cita, autor_id) VALUES (%(cita)s, %(autor_id)s);"
        resultado = connectToMySQL(cls.db).query_db(query, data)
        return resultado

    @classmethod
    def obtener_por_id(cls, cita_id):
        query = "SELECT * FROM citas WHERE id = %(id)s;"
        data = {'id': cita_id}
        resultado = connectToMySQL(cls.db).query_db(query, data)
        if not resultado:
            return None
        return cls(resultado[0])

    @classmethod
    def obtener_todas(cls):
        query = "SELECT * FROM citas;"
        resultado = connectToMySQL(cls.db).query_db(query)
        citas = []
        for row in resultado:
            citas.append(cls(row))
        return citas

    @classmethod
    def actualizar_cita(cls, data):
        query = "UPDATE citas SET cita = %(cita)s WHERE id = %(id)s;"
        resultado = connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def eliminar_cita(cls, cita_id):
        query = "DELETE FROM citas WHERE id = %(id)s;"
        data = {'id': cita_id}
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def validar_cita(cls, cita):
        is_valid = True
        if len(cita['cita']) < 5:
            flash("Tu reflexión debe tener al menos 5 caracteres para ser significativa 💭", 'alerta')
            is_valid = False
        return is_valid

    # FAVORITOS
    @classmethod
    def agregar_favorito(cls, usuario_id, cita_id):
        query = "INSERT INTO favoritos (usuario_id, cita_id) VALUES (%(usuario_id)s, %(cita_id)s);"
        data = {'usuario_id': usuario_id, 'cita_id': cita_id}
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def quitar_favorito(cls, usuario_id, cita_id):
        query = "DELETE FROM favoritos WHERE usuario_id = %(usuario_id)s AND cita_id = %(cita_id)s;"
        data = {'usuario_id': usuario_id, 'cita_id': cita_id}
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def obtener_favoritas_usuario(cls, usuario_id):
        query = ("SELECT c.* FROM citas c "
                 "JOIN favoritos f ON c.id = f.cita_id "
                 "WHERE f.usuario_id = %(usuario_id)s;")
        data = {'usuario_id': usuario_id}
        resultado = connectToMySQL(cls.db).query_db(query, data)
        return [cls(row) for row in resultado]

    @classmethod
    def obtener_no_favoritas_usuario(cls, usuario_id):
        query = ("SELECT * FROM citas WHERE id NOT IN "
                 "(SELECT cita_id FROM favoritos WHERE usuario_id = %(usuario_id)s)")
        data = {'usuario_id': usuario_id}
        resultado = connectToMySQL(cls.db).query_db(query, data)
        return [cls(row) for row in resultado]
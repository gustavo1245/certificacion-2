#Modelo de Usuario

#Encapsula toda la logica relaciona con los usuarios en la base de datos.

from base.config.mysqlconnection import connectToMySQL
import re
from flask import flash, session
from bcrypt import hashpw, gensalt, checkpw
from datetime import datetime, date

#expresion regular para validar emails
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9]+\.[a-zA-Z]+$')

class Usuario:
    """
    Clase que representa a un usuario y sus operaciones en la base de datos.
    """
    db = "proyecto_crud"

    def __init__(self, data):
        """
        Constructor: inicializa los atributos del usuario
        """
        self.id= data['id']
        self.nombre = data['nombre'].capitalize()
        self.apellido = data['apellido'].capitalize()
        self.fecha_nacimiento = data.get('fecha_nacimiento', None)
        self.edad = data.get('edad', None)
        self.email = data['email']
        self.password = data['password']
        self.creado_en = data['creado_en']
        self.actualizado_en = data['actualizado_en']

    @classmethod
    def guardar_usuario(cls, data):
        """
        Guardar un nuevo usuario en la base de datos
        """
        data['nombre'] = data['nombre'].capitalize()
        data['apellido'] = data['apellido'].capitalize()
        query = "INSERT INTO usuarios (nombre, apellido, email, password) VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password)s);"
        resultado = connectToMySQL(cls.db).query_db(query, data)
        return resultado

    @classmethod
    def obtener_por_email(cls, data):
        """
        Buscar un usuario por su email.
        """
        query = "SELECT * FROM usuarios WHERE email =%(email)s;"
        resultado = connectToMySQL(cls.db).query_db(query, data)
        if not resultado:
            return None
        return cls(resultado[0])
   
    @classmethod
    def obtener_por_id(cls, usuario_id):
        """
        Buscar un usuario por su ID
        """
        query ="SELECT * FROM usuarios WHERE id = %(id)s;"
        data = {'id' : usuario_id}
        resultado = connectToMySQL(cls.db).query_db(query, data)
        if not resultado:
            return None
        return cls(resultado[0])
   
    @classmethod
    def obtener_todos_excepto(cls, usuario_id_excluir):
        """
        Obtener todos los usuarios excepto el especificado
        """
        query = "SELECT * FROM usuarios WHERE id != %(usuario_id)s ORDER BY nombre, apellido;"
        data = {'usuario_id': usuario_id_excluir}
        resultado = connectToMySQL(cls.db).query_db(query, data)
        if not resultado:
            return []
        return [cls(row) for row in resultado]
   
    @staticmethod
    def validar_registro(usuario):
        """
        Valida los datos del formulario de registro.
        Devuelve True si todo es válido, False se hay errores (y los muestra con flash).
        """
        is_valid = True
        query = "SELECT * FROM usuarios WHERE email = %(email)s;"
        resultado = connectToMySQL(Usuario.db).query_db(query,usuario)
        if resultado:
            flash("El email ya está registro.",'registro')
            is_valid = False
        if not EMAIL_REGEX.match(usuario['email']):
            flash("Formato de email es inválido.", 'registro')
            is_valid = False
        if len(usuario ['nombre'])<3:
            flash("El nombre debe tener al menos 3 caracteres.", 'registro')
            is_valid =False
        if len(usuario['apellido'])< 3:
            flash("El apellido debe tener al menos 3 caractaeres.", 'registro')
            is_valid = False
        if len(usuario['password'])<8:
            flash("La contraseña debe tener al menos 8 caracteres.", 'registro')
            is_valid = False
        if not re.search(r'[A-Z]', usuario['password']):
            flash("La contraseña debe contener al menos una letra mayúscula.", 'registro')
            is_valid = False
        if not re.search(r'\d', usuario['password']):
            flash("La contraseña debe contener al menos un número.", 'registro')
            is_valid = False
        if ' ' in usuario['password']:
            flash("La contraseña no puede contener espacios.", 'registro')
            is_valid = False
        if usuario['password'] != usuario['confirm_password']:
            flash("Las contraseña no coinciden.", 'registro')
            is_valid = False
        return is_valid

    @staticmethod
    def validar_login(usuario):
    # Validar los datos del formulario de inicio de sesión.
    # Devuelve True si el usuario existe y la contraseña es correcta.
    
        is_valid = True
        user_in_db = Usuario.obtener_por_email(usuario)
        if not user_in_db:
            flash("Email no registrado.", 'login')
            is_valid = False
        else:
            if not checkpw(usuario['password'].encode('utf-8'), user_in_db.password.encode('utf-8')):
                flash("Contraseña incorrecta.", 'login')
                is_valid = False
            return is_valid
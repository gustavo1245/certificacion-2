# base/models/travel_plan_model.py

# Modelo de Plan de Viaje
# NOTA: Este modelo usa la tabla 'citas' temporalmente hasta ejecutar la migración
# Una vez ejecutada la migración, usará la tabla 'travel_plans'

from base.config.mysqlconnection import connectToMySQL
from flask import flash
from datetime import datetime, timedelta

class TravelPlan:
    db = "proyecto_crud"

    def __init__(self, data):
        # Compatibilidad con ambas estructuras de tabla
        self.id = data['id']
        
        # Si viene de la tabla travel_plans (nueva estructura)
        if 'destination' in data:
            self.destination = data['destination']
            self.description = data.get('description', '')
            self.travel_start_date = data['travel_start_date']
            self.travel_end_date = data['travel_end_date']
            self.plan = data['plan']
            self.is_active = data.get('is_active', True)
        else:
            # Si viene de la tabla citas (estructura actual)
            # Simulamos los campos necesarios
            self.destination = f"Destino #{data['id']}"
            self.description = "Plan migrado desde reflexión"
            # Convertir fechas a strings para el template
            fecha_actual = datetime.now()
            self.travel_start_date = fecha_actual.strftime('%Y-%m-%d')
            self.travel_end_date = (fecha_actual + timedelta(days=7)).strftime('%Y-%m-%d')
            self.plan = data.get('cita', 'Plan de viaje')
            self.is_active = True
            
        self.autor_id = data['autor_id']
        self.creado_en = data['creado_en']
        self.actualizado_en = data['actualizado_en']
        
        # Para joins con usuarios
        self.autor_nombre = data.get('autor_nombre', '')
        self.autor_apellido = data.get('autor_apellido', '')
        
        # Asegurar que las fechas siempre sean strings para el template
        if hasattr(self.travel_start_date, 'strftime'):
            self.travel_start_date = self.travel_start_date.strftime('%Y-%m-%d')
        if hasattr(self.travel_end_date, 'strftime'):
            self.travel_end_date = self.travel_end_date.strftime('%Y-%m-%d')

    @classmethod
    def crear_plan_viaje(cls, data):
        """Crear un nuevo plan de viaje - usando tabla citas temporalmente"""
        query = """
            INSERT INTO citas (cita, autor_id) 
            VALUES (%(plan_description)s, %(autor_id)s);
        """
        # Crear una descripción combinada para la tabla citas
        plan_description = f"🌍 {data['destination']} | {data['travel_start_date']} a {data['travel_end_date']} | {data['plan']}"
        temp_data = {
            'plan_description': plan_description,
            'autor_id': data['autor_id']
        }
        resultado = connectToMySQL(cls.db).query_db(query, temp_data)
        return resultado

    @classmethod
    def obtener_por_id(cls, plan_id):
        """Obtener un plan por ID con información del autor"""
        # Intentar primero con la tabla travel_plans
        query = """
            SELECT tp.*, u.nombre as autor_nombre, u.apellido as autor_apellido
            FROM travel_plans tp
            JOIN usuarios u ON tp.autor_id = u.id
            WHERE tp.id = %(id)s;
        """
        data = {'id': plan_id}
        resultado = connectToMySQL(cls.db).query_db(query, data)
        
        if not resultado:
            # Si no existe en travel_plans, intentar con citas (tabla temporal)
            query = """
                SELECT c.*, u.nombre as autor_nombre, u.apellido as autor_apellido
                FROM citas c
                JOIN usuarios u ON c.autor_id = u.id
                WHERE c.id = %(id)s;
            """
            resultado = connectToMySQL(cls.db).query_db(query, data)
            
        if not resultado:
            return None
        return cls(resultado[0])

    @classmethod
    def obtener_por_autor(cls, autor_id):
        """Obtener planes de un autor con información del autor"""
        # Intentar primero con travel_plans
        query = """
            SELECT tp.*, u.nombre as autor_nombre, u.apellido as autor_apellido
            FROM travel_plans tp
            JOIN usuarios u ON tp.autor_id = u.id
            WHERE tp.autor_id = %(autor_id)s ORDER BY tp.creado_en DESC;
        """
        data = {'autor_id': autor_id}
        resultado = connectToMySQL(cls.db).query_db(query, data)
        
        if not resultado:
            # Si no hay en travel_plans, usar citas
            query = """
                SELECT c.*, u.nombre as autor_nombre, u.apellido as autor_apellido
                FROM citas c
                JOIN usuarios u ON c.autor_id = u.id
                WHERE c.autor_id = %(autor_id)s ORDER BY c.creado_en DESC;
            """
            resultado = connectToMySQL(cls.db).query_db(query, data)
            
        return [cls(row) for row in resultado]

    @classmethod
    def obtener_trip_schedules(cls, usuario_id):
        """Obtener trip schedules - incluye planes propios Y planes a los que se unió"""
        # Obtener planes propios (que el usuario creó)
        query_propios = """
            SELECT c.*, u.nombre as autor_nombre, u.apellido as autor_apellido
            FROM citas c
            JOIN usuarios u ON c.autor_id = u.id
            WHERE c.autor_id = %(usuario_id)s
            ORDER BY c.creado_en DESC;
        """
        
        # Obtener planes de otros usuarios a los que se unió (favoritos)
        query_unidos = """
            SELECT c.*, u.nombre as autor_nombre, u.apellido as autor_apellido
            FROM citas c
            JOIN favoritos f ON c.id = f.cita_id
            JOIN usuarios u ON c.autor_id = u.id
            WHERE f.usuario_id = %(usuario_id)s AND c.autor_id != %(usuario_id)s
            ORDER BY c.creado_en DESC;
        """
        
        data = {'usuario_id': usuario_id}
        
        # Obtener ambos conjuntos de datos
        planes_propios = connectToMySQL(cls.db).query_db(query_propios, data)
        planes_unidos = connectToMySQL(cls.db).query_db(query_unidos, data)
        
        # Combinar ambos resultados
        todos_los_planes = []
        
        # Añadir planes propios
        if planes_propios:
            for row in planes_propios:
                plan = cls(row)
                plan.joined_at = row.get('creado_en')
                plan.es_propio = True
                todos_los_planes.append(plan)
        
        # Añadir planes a los que se unió
        if planes_unidos:
            for row in planes_unidos:
                plan = cls(row)
                plan.joined_at = row.get('creado_en')
                plan.es_propio = False
                todos_los_planes.append(plan)
        
        # Ordenar por fecha de creación (más recientes primero)
        todos_los_planes.sort(key=lambda x: x.creado_en, reverse=True)
        
        return todos_los_planes

    @classmethod
    def obtener_planes_otros_usuarios(cls, usuario_id):
        """Obtener planes de otros usuarios - usando citas temporalmente"""
        query = """
            SELECT c.*, u.nombre as autor_nombre, u.apellido as autor_apellido
            FROM citas c
            JOIN usuarios u ON c.autor_id = u.id
            WHERE c.autor_id != %(usuario_id)s 
            AND c.id NOT IN (
                SELECT f.cita_id 
                FROM favoritos f 
                WHERE f.usuario_id = %(usuario_id)s
            )
            ORDER BY c.creado_en DESC
            LIMIT 10;
        """
        data = {'usuario_id': usuario_id}
        resultado = connectToMySQL(cls.db).query_db(query, data)
        return [cls(row) for row in resultado]

    @classmethod
    def obtener_usuarios_unidos_al_plan(cls, plan_id):
        """Obtener la lista de usuarios que se unieron a un plan específico"""
        query = """
            SELECT u.nombre, u.apellido, f.creado_en as fecha_union
            FROM favoritos f
            JOIN usuarios u ON f.usuario_id = u.id 
            JOIN citas c ON f.cita_id = c.id
            WHERE f.cita_id = %(plan_id)s AND u.id != c.autor_id
            ORDER BY f.creado_en ASC;
        """
        data = {'plan_id': plan_id}
        resultado = connectToMySQL(cls.db).query_db(query, data)
        return resultado if resultado else []

    @classmethod
    def unirse_a_plan(cls, usuario_id, plan_id):
        """Unirse a un plan - usando favoritos temporalmente"""
        query = "INSERT INTO favoritos (usuario_id, cita_id) VALUES (%(usuario_id)s, %(cita_id)s);"
        data = {'usuario_id': usuario_id, 'cita_id': plan_id}
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def cancelar_participacion(cls, usuario_id, plan_id):
        """Cancelar participación - usando favoritos temporalmente"""
        query = "DELETE FROM favoritos WHERE usuario_id = %(usuario_id)s AND cita_id = %(cita_id)s;"
        data = {'usuario_id': usuario_id, 'cita_id': plan_id}
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def cancelar_plan(cls, plan_id):
        """Marcar plan como cancelado - usando citas temporalmente"""
        query = "UPDATE citas SET cita = CONCAT('[CANCELADO] ', cita) WHERE id = %(id)s AND cita NOT LIKE '[CANCELADO]%';"
        data = {'id': plan_id}
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def eliminar_plan(cls, plan_id):
        """Eliminar plan completamente - usando citas temporalmente"""
        query = "DELETE FROM citas WHERE id = %(id)s;"
        data = {'id': plan_id}
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def actualizar_plan(cls, data):
        """Actualizar plan - usando citas temporalmente"""
        plan_description = f"🌍 {data['destination']} | {data['travel_start_date']} a {data['travel_end_date']} | {data['plan']}"
        query = "UPDATE citas SET cita = %(cita)s WHERE id = %(id)s;"
        temp_data = {
            'cita': plan_description,
            'id': data['id']
        }
        return connectToMySQL(cls.db).query_db(query, temp_data)

    @staticmethod
    def validar_plan_viaje(plan_data):
        """Validar datos del plan de viaje"""
        is_valid = True
        
        # Validar tema (destination)
        if not plan_data.get('destination') or len(plan_data['destination']) < 1:
            flash("Debes seleccionar un tema", 'error')
            is_valid = False
            
        # Validar notas (plan) - máximo 50 caracteres
        if not plan_data.get('plan'):
            flash("Las notas son obligatorias", 'error')
            is_valid = False
        elif len(plan_data['plan']) > 50:
            flash("Las notas no pueden tener más de 50 caracteres", 'error')
            is_valid = False
            
        # Validar duración en horas
        duracion = plan_data.get('duracion_horas', '')
        if duracion:
            try:
                duracion_num = int(duracion)
                if duracion_num < 1:
                    flash("La duración debe ser un número positivo", 'error')
                    is_valid = False
                elif len(str(duracion_num)) > 50:  # Validación de caracteres como número
                    flash("La duración no debe tener más de 50 caracteres", 'error')
                    is_valid = False
            except ValueError:
                flash("La duración debe ser un número válido", 'error')
                is_valid = False
            
        # Validación de fecha - no puede ser en el pasado
        try:
            fecha_seleccionada = datetime.strptime(plan_data['travel_start_date'], '%Y-%m-%d').date()
            fecha_actual = datetime.now().date()
            
            if fecha_seleccionada < fecha_actual:
                flash("No puedes seleccionar una fecha en el pasado", 'error')
                is_valid = False
                
        except ValueError:
            flash("Formato de fecha inválido", 'error')
            is_valid = False
            
        return is_valid

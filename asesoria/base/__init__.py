from flask import Flask, render_template
from datetime import datetime
from base.controllers import citas, usuarios


# importar controllers


#definir un filtro de jinja2 para formatear fechas
def format_date(value, format='%Y-%m-%d'):
    """Convierte una cadena de fecha en un objeto datetime y lo formatea."""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return value
    return value.strftime(format)

def format_travel_date(value):
    """Formatea fechas específicamente para el travel dashboard"""
    if not value:
        return 'N/A'
    
    # Si es string en formato YYYY-MM-DD
    if isinstance(value, str):
        try:
            date_obj = datetime.strptime(value, '%Y-%m-%d')
            return date_obj.strftime('%b %d %Y')
        except ValueError:
            return value
    
    # Si es un objeto datetime
    if hasattr(value, 'strftime'):
        return value.strftime('%b %d %Y')
    
    return str(value)


def create_app():
    app = Flask (__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DEBUG=True,
    )

    # Registrar los Blueprints
    app.register_blueprint(usuarios.bp)
    app.register_blueprint(citas.bp)

    # Registrar los filtros de fecha en la aplicacion
    app.add_template_filter(format_date, 'format_date')
    app.add_template_filter(format_travel_date, 'format_travel_date')


    @app.route('/')
    def index():
        return render_template('auth.html')

    return app
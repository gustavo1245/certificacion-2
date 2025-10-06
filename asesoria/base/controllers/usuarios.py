from flask import render_template, redirect, request, session, Blueprint, flash
from base.models.usuario_model import Usuario
from bcrypt import hashpw, gensalt


bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')


@bp.route('/procesar_registro', methods=['POST'])
def procesar_registro():
    if not Usuario.validar_registro(request.form):
        return redirect('/')
   
    password_hash = hashpw(request.form['password'].encode('utf-8'), gensalt())
    data ={
        **request.form,
        'password' : password_hash.decode('utf-8')
    }
   
    usuario_id = Usuario.guardar_usuario(data)
    session['usuario_id'] = usuario_id
    flash("¡Bienvenido a tu viaje de crecimiento personal! 🌟", 'exito')
    return redirect('/citas')

@bp.route('/procesar_login', methods=['POST'])
def procesar_login():
    if not Usuario.validar_login(request.form):
        return redirect('/')
   
    usuario_db = Usuario.obtener_por_email(request.form)
    session['usuario_id'] = usuario_db.id
    flash(f"¡Qué alegría verte de nuevo, {usuario_db.nombre}! Continúa tu viaje 🎒", 'exito')
    return redirect('/citas')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

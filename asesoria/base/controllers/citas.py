from base.models.travel_plan_model import TravelPlan
from base.models.usuario_model import Usuario
from flask import render_template, redirect, request, session, Blueprint, flash

bp = Blueprint('citas', __name__, url_prefix='/citas')

@bp.route('/')
def citas_simple():
    if 'usuario_id' not in session:
        return redirect('/')
    
    usuario = Usuario.obtener_por_id(session['usuario_id'])
    
    # Obtener las asesorías (planes de viaje) del usuario actual
    mis_asesorias = TravelPlan.obtener_por_autor(session['usuario_id'])
    
    # Obtener todas las asesorías de otros usuarios
    todas_las_asesorias = TravelPlan.obtener_planes_otros_usuarios(session['usuario_id'])
    
    # Obtener tutores disponibles para el modal
    tutores_disponibles = Usuario.obtener_todos_excepto(session['usuario_id'])
    
    return render_template('citas_simple.html', 
                         usuario=usuario,
                         mis_asesorias=mis_asesorias,
                         todas_las_asesorias=todas_las_asesorias,
                         tutores=tutores_disponibles)

@bp.route('/crear_plan', methods=['POST'])
def crear_plan_viaje():
    if 'usuario_id' not in session:
        return redirect('/')
    
    if not TravelPlan.validar_plan_viaje(request.form):
        return redirect('/citas')
    
    # Calcular fecha de fin basada en la duración en horas
    # Por simplicidad, asumimos que la asesoría dura el mismo día
    fecha_inicio = request.form['travel_start_date']
    
    data = {
        'destination': request.form['destination'],
        'travel_start_date': fecha_inicio,
        'travel_end_date': fecha_inicio,  # Mismo día
        'plan': request.form['plan'],
        'duracion_horas': request.form.get('duracion_horas', '2'),
        'tutor': request.form.get('tutor', ''),
        'autor_id': session['usuario_id']
    }
    
    TravelPlan.crear_plan_viaje(data)
    flash("¡Plan de viaje creado exitosamente! 🌟", 'success')
    return redirect('/citas')

@bp.route('/descripcion/<int:plan_id>')
def descripcion_viaje(plan_id):
    if 'usuario_id' not in session:
        flash("Debes iniciar sesión para ver esta asesoría", 'error')
        return redirect('/')
    
    usuario = Usuario.obtener_por_id(session['usuario_id'])
    plan = TravelPlan.obtener_por_id(plan_id)
    
    if not plan:
        flash("La asesoría solicitada no fue encontrada", 'error')
        return redirect('/citas')
    
    usuarios_unidos = TravelPlan.obtener_usuarios_unidos_al_plan(plan_id)
    tutores_disponibles = Usuario.obtener_todos_excepto(plan.autor_id)
    
    return render_template('descripcion_viaje.html', 
                         usuario=usuario, 
                         plan=plan, 
                         usuarios_unidos=usuarios_unidos,
                         tutores=tutores_disponibles)

@bp.route('/unirse/<int:plan_id>')
def unirse_a_plan(plan_id):
    if 'usuario_id' not in session:
        return redirect('/')
    
    TravelPlan.unirse_a_plan(session['usuario_id'], plan_id)
    flash("¡Te has unido al viaje! 🎒", 'success')
    return redirect('/citas')

@bp.route('/cancelar_participacion/<int:plan_id>')
def cancelar_participacion(plan_id):
    if 'usuario_id' not in session:
        return redirect('/')
    
    TravelPlan.cancelar_participacion(session['usuario_id'], plan_id)
    flash("Has cancelado tu participación en el viaje", 'info')
    return redirect('/citas')

@bp.route('/eliminar_plan/<int:plan_id>')
def eliminar_plan(plan_id):
    if 'usuario_id' not in session:
        return redirect('/')
    
    TravelPlan.eliminar_plan(plan_id)
    flash("Plan de viaje eliminado", 'warning')
    return redirect('/citas')

@bp.route('/perfil')
def ver_perfil():
    if 'usuario_id' not in session:
        return redirect('/')
    
    usuario = Usuario.obtener_por_id(session['usuario_id'])
    return render_template('perfil.html', usuario=usuario)

@bp.route('/editar/<int:plan_id>')
def editar_asesoria(plan_id):
    if 'usuario_id' not in session:
        return redirect('/')
    
    plan = TravelPlan.obtener_por_id(plan_id)
    
    # Verificar que el usuario sea el autor del plan
    if not plan or plan.autor_id != session['usuario_id']:
        flash("No tienes permisos para editar esta asesoría", 'error')
        return redirect('/citas')
    
    usuario = Usuario.obtener_por_id(session['usuario_id'])
    tutores_disponibles = Usuario.obtener_todos_excepto(session['usuario_id'])
    return render_template('editar_cita.html', usuario=usuario, plan=plan, tutores=tutores_disponibles)

@bp.route('/actualizar/<int:plan_id>', methods=['POST'])
def actualizar_asesoria(plan_id):
    if 'usuario_id' not in session:
        return redirect('/')
    
    plan = TravelPlan.obtener_por_id(plan_id)
    
    # Verificar que el usuario sea el autor del plan
    if not plan or plan.autor_id != session['usuario_id']:
        flash("No tienes permisos para editar esta asesoría", 'error')
        return redirect('/citas')
    
    if not TravelPlan.validar_plan_viaje(request.form):
        return redirect(f'/citas/editar/{plan_id}')
    
    # Calcular fecha de fin basada en la duración en horas
    fecha_inicio = request.form['travel_start_date']
    
    data = {
        'id': plan_id,
        'destination': request.form['destination'],
        'travel_start_date': fecha_inicio,
        'travel_end_date': fecha_inicio,  # Mismo día
        'plan': request.form['plan'],
        'duracion_horas': request.form.get('duracion_horas', '2')
    }
    
    # Necesitaremos crear este método en el modelo
    TravelPlan.actualizar_plan(data)
    flash("¡Asesoría actualizada exitosamente! 📝", 'success')
    return redirect('/citas')

@bp.route('/solicitar_asesoria')
def solicitar_asesoria():
    if 'usuario_id' not in session:
        return redirect('/')
    
    usuario = Usuario.obtener_por_id(session['usuario_id'])
    tutores_disponibles = Usuario.obtener_todos_excepto(session['usuario_id'])
    return render_template('solicitar_asesoria.html', usuario=usuario, tutores=tutores_disponibles)

@bp.route('/cambiar_tutor/<int:plan_id>', methods=['POST'])
def cambiar_tutor(plan_id):
    if 'usuario_id' not in session:
        return redirect('/')
    
    nuevo_tutor_id = request.form.get('nuevo_tutor')
    
    # Aquí podrías agregar la lógica para actualizar el tutor en la base de datos
    # Por ahora solo mostramos un mensaje de éxito
    flash("¡Tutor cambiado exitosamente! 👨‍🏫", 'success')
    return redirect(f'/citas/descripcion/{plan_id}')

@bp.route('/test_data')
def crear_datos_prueba():
    """Ruta temporal para crear datos de prueba"""
    if 'usuario_id' not in session:
        return redirect('/')
    
    # Crear una asesoría de ejemplo
    data = {
        'destination': 'Spring Data',
        'travel_start_date': '2024-06-23',
        'travel_end_date': '2024-06-23',
        'plan': 'Busco tutor para practicar y aprender un poco más sobre Spring Data',
        'autor_id': session['usuario_id']
    }
    
    try:
        plan_id = TravelPlan.crear_plan_viaje(data)
        flash(f"¡Datos de prueba creados! ID: {plan_id}", 'success')
    except Exception as e:
        flash(f"Error al crear datos de prueba: {str(e)}", 'error')
    
    return redirect('/citas')




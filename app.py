from flask import Flask, jsonify, request, send_from_directory
import logging
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Cambia el static_folder a 'dist' para servir el frontend
import os
# Configuración de logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder="dist")
# habilitar CORS para permitir solicitudes desde el frontend
CORS(app, origins=["http://localhost:5173"])
# configuración de la base de datos (SQLite en este caso)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///comunidad.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Definición del modelo de datos
class Trabajo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    materia = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    date = db.Column(db.String(50))


@app.route('/api/data', methods=['POST', 'GET'])
def get_data():
    try:
        data = None
        method = request.method
        if method == "POST":
            data = request.get_json()
            if not data:
                logging.warning("No se recibió JSON en la petición POST a /api/data")
                return jsonify({
                    "status": 400,
                    'message': 'No se recibió JSON',
                    'data': None
                }), 400
            # Validar campos requeridos
            required_fields = ['titulo', 'fecha_entrega', 'materia', 'description']
            for field in required_fields:
                if field not in data:
                    logging.warning(f"Falta el campo requerido: {field}")
                    return jsonify({
                        "status": 400,
                        'message': f'Falta el campo requerido: {field}',
                        'data': None
                    }), 400
            title = data['titulo']
            date = data['fecha_entrega']
            materia = data['materia']
            descripcion = data['description']
            logging.info(f"POST recibido: {title}, {date}, {materia}, {descripcion}")
            new_subject = Trabajo(title=title, date=date, materia=materia, descripcion=descripcion)
            db.session.add(new_subject)
            db.session.commit()
        else:
            data = "saludos compatriota anonimo"

        response = {
            "status": 200,
            'message': 'Data received successfully',
            'data': data
        }
        return jsonify(response)
    except Exception as e:
        logging.exception("Error en /api/data")
        return jsonify({
            "status": 500,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@app.route('/api/trabajos', methods=['GET'])
def get_trabajos():
    trabajos = Trabajo.query.all()
    trabajos_list = [
        {
            'id': trabajo.id,
            'title': trabajo.title,
            'materia': trabajo.materia,
            'descripcion': trabajo.descripcion,
            'date': trabajo.date
        } for trabajo in trabajos
    ]
    return jsonify(trabajos_list)

# Ruta para servir archivos estáticos del frontend (React)
@app.errorhandler(404)
def not_found(e):
    # Si la ruta es de la API, devolver JSON, no HTML
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found', 'path': request.path}), 404
    # Si no, dejar que el frontend maneje la ruta
    return send_from_directory(app.static_folder, 'index.html')

# Ruta para servir archivos estáticos del frontend (React)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Crear las tablas en la base de datos antes de la primera solicitud
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)
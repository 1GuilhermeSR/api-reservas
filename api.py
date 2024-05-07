from flask import Flask, jsonify, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

import mysql.connector

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
db = SQLAlchemy(app)
CORS(app, resources={r"/*": {"origins": "*"}})

SWAGGER_URL = f'/swagger/'
API_URL = '/static/swagger.json'
swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "API-Reserva"})
app.register_blueprint(swagger_ui_blueprint)


class ReservaModel(db.Model):
    __tablename__ = "reserva"
    id = db.Column(db.Integer, primary_key=True)
    idHotel = db.Column(db.Integer, nullable=False)
    idQuarto = db.Column(db.Integer, nullable=False)
    dataIni = db.Column(db.Date, nullable=False)
    dataFin = db.Column(db.Date, nullable=False)


def toDict(reserva):
    return {
        "id": reserva.id,
        "idHotel": reserva.idHotel,
        "idQuarto": reserva.idQuarto,
        "dataIni": reserva.dataIni,
        "dataFin": reserva.dataFin
    }


def createReserva(idhotel, idquarto, dataIni, dataFin):
    try:
        reserva = ReservaModel(idHotel=idhotel, idQuarto=idquarto, dataIni=dataIni, dataFin=dataFin)
        db.session.add(reserva)
        db.session.commit()

        return reserva
    except ValueError as err:
        print(f"Erro ao criar a reserva: {err}")
        # return jsonify({'error': f"Erro ao criar a reserva: {err}"}), 400
        return None


def consultar(idhotel, idquarto):
    try:
        reservas = ReservaModel.query.filter_by(idHotel=idhotel).filter_by(idQuarto=idquarto).all()
        return reservas
    except ValueError as err:
        print(f"Erro ao consultar a reserva: {err}")
        # return jsonify({'error': f"Erro ao consultar a reserva: {err}"}), 400
        return None


def verificaDisponibilidade(idhotel, idquarto, dataIni, dataFin):
    try:
        datas = (ReservaModel.query.filter_by(idHotel=idhotel).filter_by(idQuarto=idquarto)
                 .with_entities(ReservaModel.dataIni, ReservaModel.dataFin).all())
    except ValueError as err:
        print(err)
        return False

    for data in datas:
        if hasConflict(data, dataIni, dataFin):
            return False
    return True


def hasConflict(data, dataIni, dataFin):
    return ((data[0] < dataIni < data[1]) or
            (data[0] < dataFin < data[1]) or
            (dataIni < data[0] and dataFin > data[1]) or
            # (dataIni > data["dataIni"] and dataFin < data["dataFin"]) or
            (dataIni == data[0] or dataFin == data[1]))


def deleteReserva(idReserva):
    try:
        reserva = ReservaModel.query.filter_by(id=idReserva).first()
        if not reserva:
            return False
        db.session.delete(reserva)
        db.session.commit()
        return reserva
    except ValueError as err:
        print(f"Erro ao deletar a reserva: {err}")
        return False


@app.route('/reservar/<int:idhotel>/<int:idquarto>', methods=['GET'])
def consultarReserva(idhotel, idquarto):
    reservas = consultar(idhotel, idquarto)
    reservaDict = []
    for reserva in reservas:
        reservaDict.append(toDict(reserva))
    print(reservaDict)

    if reservas:
        return jsonify(reservaDict), 200
    else:
        return jsonify({'error': 'Reserva não encontrada'}), 404


@app.route('/reservar', methods=['POST'])
def reservar():
    try:
        data = request.json
        idhotel = data['idhotel']
        idquarto = data['idquarto']
        dataIni = data['dataIni']
        dataFin = data['dataFin']
        if not data:
            return jsonify({'error': 'Faltando body, nao foi possivel reservar'}), 400
        if not data['idhotel']:
            return jsonify({'error': 'Faltando idhotel, nao foi possivel reservar'}), 400
        elif not data['idquarto']:
            return jsonify({'error': 'Faltando idquarto, nao foi possivel reservar'}), 400
        elif not data['dataIni']:
            return jsonify({'error': 'Faltando dataIni, nao foi possivel reservar'}), 400
        elif not data['dataFin']:
            return jsonify({'error': 'Faltando dataFin, nao foi possivel reservar'}), 400
    except KeyError as err:
        return jsonify({'error': 'Faltando body ou parametros'}), 400

    try:
        dataInicio = datetime.strptime(dataIni, "%Y-%m-%d %H:%M:%S").date()
        dataFinal = datetime.strptime(dataFin, "%Y-%m-%d %H:%M:%S").date()
    except ValueError as err:
        return jsonify({'error': 'Formato de data invalida, deve ser "2000-12-25 23:59:59"'}), 400

    if not verificaDisponibilidade(idhotel, idquarto, dataInicio, dataFinal):
        return jsonify({'error': "Conflito de datas, nao foi possivel reservar"}), 409

    reserva = createReserva(idhotel, idquarto, dataInicio, dataFinal)
    if reserva:
        return jsonify(toDict(reserva)), 201
    return jsonify({'error': 'Nao foi possivel fazer a reserva'}), 400


@app.route('/reservar/<int:idreserva>', methods=['DELETE'])
def deleteReservaEndpoint(idreserva):
    deleted_reserva = deleteReserva(idreserva)
    if deleted_reserva:
        return jsonify(toDict(deleted_reserva)), 200
    else:
        return jsonify({'error': 'Reserva nao existe, nao foi possivel deletar'}), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True, port=5001)

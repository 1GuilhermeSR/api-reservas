from datetime import datetime

from flask import Flask, jsonify, request, abort
import mysql.connector

app = Flask(__name__)


def conectionDB():
    conection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='reservas')
    return conection


def createReserva(idhotel, idquarto, dataIni, dataFin):
    #    if verificaDisponibilidade(idhotel, idquarto, dataIni, dataFin):
    connection = conectionDB()
    cursor = connection.cursor(dictionary=True)
    sql = 'INSERT INTO reserva (idhotel, idquarto, dataIni, dataFin) VALUES (%s, %s, %s, %s)'
    values = (idhotel, idquarto, dataIni, dataFin)
    try:
        cursor.execute(sql, values)
        connection.commit()

        sql2 = 'SELECT * FROM reserva where id = %s'
        values2 = (cursor.lastrowid,)

        cursor.execute(sql2, values2)
        reserva = cursor.fetchone()

        return reserva
    except mysql.connector.Error as err:
        return err
    finally:
        cursor.close()
        connection.close()
    #    else:
    #        return None


def consultar(idhotel, idquarto):
    connection = conectionDB()
    cursor = connection.cursor(dictionary=True)
    sql = 'SELECT * FROM reserva WHERE idhotel = %s and idquarto = %s'
    values = (idhotel, idquarto,)
    try:
        cursor.execute(sql, values)
        data = cursor.fetchall()
        if data:
            return jsonify(data), 200
        else:
            return jsonify({'error': 'Reserva não encontrada'}), 404
    except mysql.connector.Error as err:
        print(f"Erro ao consultar a reserva: {err}")
        return jsonify({'error': f"Erro ao consultar a reserva: {err}"}), 400
    finally:
        cursor.close()
        connection.close()


def verificaDisponibilidade(idhotel, idquarto, dataIni, dataFin):
    connection = conectionDB()
    cursor = connection.cursor(dictionary=True)
    sql = 'SELECT dataIni, dataFin FROM reserva WHERE idhotel = %s AND idquarto = %s'
    values = (idhotel, idquarto)
    try:
        cursor.execute(sql, values)
        datas = cursor.fetchall()
    except mysql.connector.Error as err:
        print(err)
        return False

    for data in datas:
        if hasConflict(data, dataIni, dataFin):
            return False
    return True
    cursor.close()
    connection.close()


def hasConflict(data, dataIni, dataFin):
    return ((data["dataIni"] < dataIni < data["dataFin"]) or
            (data["dataIni"] < dataFin < data["dataFin"]) or
            (dataIni < data["dataIni"] and dataFin > data["dataFin"]) or
            #(dataIni > data["dataIni"] and dataFin < data["dataFin"]) or
            (dataIni == data["dataIni"] or dataFin == data["dataFin"]))


def deleteReserva(id):
    connection = conectionDB()
    cursor = connection.cursor(dictionary=True)
    sql = 'DELETE FROM reserva WHERE id = %s'
    sql2 = 'SELECT * FROM reserva where id = %s'
    values = (id,)
    try:
        cursor.execute(sql2, values)
        data = cursor.fetchone()
        if data:
            cursor.execute(sql, values)
            connection.commit()
            return data
        else:
            return False
    except mysql.connector.Error as err:
        print(f"Erro ao deletar a reserva: {err}")
        return False
    finally:
        cursor.close()
        connection.close()


@app.route('/reservar/<int:idhotel>/<int:idquarto>', methods=['GET'])
def consultarReserva(idhotel, idquarto):
    return consultar(idhotel, idquarto)


@app.route('/reservar', methods=['POST'])
def reservar():
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

    try:
        dataInicio = datetime.strptime(dataIni, "%Y-%m-%d %H:%M:%S").date()
        dataFinal = datetime.strptime(dataFin, "%Y-%m-%d %H:%M:%S").date()
    except ValueError as err:
        return jsonify({'error': 'Formato de data invalida, deve ser "2000-12-25 23:59:59"'}), 400

    if not verificaDisponibilidade(idhotel, idquarto, dataInicio, dataFinal):
        return jsonify({'error': "Conflito de datas, nao foi possivel reservar"}), 409

    reserva = createReserva(idhotel, idquarto, dataIni, dataFin)
    if reserva:
        return jsonify(reserva), 201
    else:
        return jsonify({'error': 'Nao foi possivel fazer a reserva'}), 409


@app.route('/reservar/<int:idreserva>', methods=['DELETE'])
def deleteReservaEndpoint(idreserva):
    deleted_reserva = deleteReserva(idreserva)
    if deleted_reserva:
        return jsonify(deleted_reserva), 200
    else:
        return jsonify({'error': f"Erro ao deletar a reserva com ID {idreserva}"}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5001)

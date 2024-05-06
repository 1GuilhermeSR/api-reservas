import sys

from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)


def createReserva(idhotel, idquarto, dataIni, dataFin):
    if verificaDisponibilidade(idhotel, idquarto, dataIni, dataFin):
        conection = conectionDB()
        cursor = conection.cursor()
        sql = 'INSERT INTO reserva (idhotel, idquarto, dataIni, dataFin) VALUES (%s, %s, %s, %s)'
        values = (idhotel, idquarto, dataIni, dataFin)
        try:
            cursor.execute(sql, values)
            conection.commit()
            print('Reserva feita com sucesso!')
            reserva_id = cursor.lastrowid
            reserva = {'id': reserva_id, 'idhotel': idhotel, 'idquarto': idquarto, 'dataIni': dataIni,
                       'dataFin': dataFin}
            return reserva
        except mysql.connector.Error as err:
            print(f"Erro ao fazer a reserva: {err}")
            return None
        finally:
            cursor.close()
            conection.close()
    else:
        return None


def consultar(idquarto, idhotel):
    conection = conectionDB()
    cursor = conection.cursor(dictionary=True)
    sql = 'SELECT * FROM reserva WHERE idquarto = %s and idhotel = %s'
    values = (idquarto, idhotel,)
    try:
        cursor.execute(sql, values)
        data = cursor.fetchone()
        if data:
            return jsonify(data)
        else:
            return jsonify({'error': 'Reserva não encontrada'}), 404
    except mysql.connector.Error as err:
        print(f"Erro ao consultar a reserva: {err}")
        return jsonify({'error': f"Erro ao consultar a reserva: {err}"}), 400
    finally:
        cursor.close()
        conection.close()


def verificaDisponibilidade(idhotel, idquarto, dataIni, dataFin):
    conection = conectionDB()
    cursor = conection.cursor(dictionary=True)
    # print(f"{dataIni}, {type(dataIni)}, ", file=sys.stderr)
    sql = 'SELECT * FROM reserva WHERE idquarto = %s AND idhotel = %s AND (dataIni <= %s AND dataFin >= %s)'
    values = (idquarto, idhotel, dataIni, dataFin)
    try:
        cursor.execute(sql, values)
        data = cursor.fetchone()
        if data:
            return False
        else:
            return True
    except mysql.connector.Error as err:
        return False
    finally:
        cursor.close()
        conection.close()


def conectionDB():
    conection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='reservas')
    return conection


@app.route('/reservar', methods=['POST'])
def reservar():
    data = request.json
    idhotel = data['idhotel']
    idquarto = data['idquarto']
    dataIni = data['dataIni']
    dataFin = data['dataFin']
    reserva = createReserva(idhotel, idquarto, dataIni, dataFin)
    if reserva:
        return jsonify(reserva), 200
    else:
        return jsonify({'error': 'Nao foi possivel fazer a reserva'}), 404


@app.route('/reservar/<int:id>', methods=['DELETE'])
def deleteReservaEndpoint(id):
    deleted_reserva = deleteReserva(id)
    if deleted_reserva is False:
        return jsonify({'error': f"Erro ao deletar a reserva com ID {id}"}), 400
    else:
        return jsonify(f"reserva deletada {deleted_reserva}"), 200


def deleteReserva(id):
    conection = conectionDB()
    cursor = conection.cursor()
    sql = 'DELETE FROM reserva WHERE id = %s'
    sql2 = 'SELECT * FROM reserva where id = %s'
    values = (id,)
    try:
        cursor.execute(sql2, values)
        data = cursor.fetchone()
        if data:
            cursor.execute(sql, values)
            conection.commit()
            return data
        else:
            return False
    except mysql.connector.Error as err:
        print(f"Erro ao deletar a reserva: {err}")
        return False
    finally:
        cursor.close()
        conection.close()


@app.route('/reservar/<int:idquarto>/<int:idhotel>', methods=['GET'])
def consultarReserva(idquarto, idhotel):
    return consultar(idquarto, idhotel)


def verificaDisponibilidadeEndPoint():
    data = request.json
    idhotel = data['idhotel']
    idquarto = data['idquarto']
    dataIni = data['dataIni']
    dataFin = data['dataFin']
    return jsonify(verificaDisponibilidade(idhotel, idquarto, dataIni, dataFin))


if __name__ == '__main__':
    app.run(debug=True, port=5010)

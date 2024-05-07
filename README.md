# api-reservas

## Documentação Swagger

+ /swagger

## Métodos

| Métodos  | Descrição                      |
|----------|--------------------------------|
| `GET`    | Retorna uma lista de reservas. |
| `POST`   | Cria uma nova reserva.         |
| `DELETE` | Deleta uma reserva.            |

## Status Codes

| Códigos | Descrição                               |
|---------|-----------------------------------------|
| `200`   | Request com sucesso contendo um body.   |
| `201`   | Request com sucesso, recurso criado.    |
| `400`   | Request foito com sintaxe invalida.     |
| `404`   | Informalção requisitada não encontrada. |
| `409`   | Conflito ao criar recurso requisitado.  |

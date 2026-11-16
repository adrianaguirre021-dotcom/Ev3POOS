import json
import sqlite3
from typing import Any
from config.database import Database


class ConsultaExternaDAO:
    """Guarda localmente consultas y respuestas de APIs para mantener trazabilidad."""

    @staticmethod
    def guardar(tipo: str, parametro: str, respuesta: dict[str, Any]) -> bool:
        conn = Database().get_connection()
        try:
            conn.execute(
                "INSERT INTO consulta_externa (tipo, parametro, respuesta_json) VALUES (?, ?, ?)",
                (tipo, parametro, json.dumps(respuesta, ensure_ascii=False))
            )
            conn.commit()
            return True
        except (sqlite3.Error, TypeError, ValueError):
            return False
        finally:
            conn.close()

    @staticmethod
    def listar(limite: int = 10) -> list[dict[str, Any]]:
        conn = Database().get_connection()
        try:
            filas = conn.execute(
                "SELECT tipo, parametro, respuesta_json, fecha_consulta "
                "FROM consulta_externa ORDER BY id_consulta DESC LIMIT ?", (limite,)
            ).fetchall()
            resultados = []
            for fila in filas:
                try:
                    respuesta = json.loads(fila["respuesta_json"])
                except (json.JSONDecodeError, TypeError):
                    respuesta = {}
                resultados.append({"tipo": fila["tipo"], "parametro": fila["parametro"],
                                   "respuesta": respuesta, "fecha": fila["fecha_consulta"]})
            return resultados
        except sqlite3.Error:
            return []
        finally:
            conn.close()

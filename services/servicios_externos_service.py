import re
from typing import Any
import requests
from config.settings import Settings


class ServiciosExternosService:
    """Consume Open-Meteo (clima) y Frankfurter (tipo de cambio), sin claves API."""
    MONEDAS_PERMITIDAS = {
        "ARS", "AUD", "BRL", "CAD", "CHF", "CLP", "CNY", "COP", "EUR",
        "GBP", "JPY", "MXN", "NZD", "PEN", "USD", "UYU", "ZAR"
    }
    CODIGOS_CLIMA = {
        0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado",
        3: "Nublado", 45: "Niebla", 48: "Niebla con escarcha",
        51: "Llovizna ligera", 53: "Llovizna moderada", 55: "Llovizna intensa",
        61: "Lluvia ligera", 63: "Lluvia moderada", 65: "Lluvia intensa",
        71: "Nevada ligera", 73: "Nevada moderada", 75: "Nevada intensa",
        80: "Chubascos ligeros", 81: "Chubascos moderados", 82: "Chubascos fuertes",
        95: "Tormenta", 96: "Tormenta con granizo ligero", 99: "Tormenta con granizo intenso"
    }

    @staticmethod
    def _validar_ciudad(ciudad: str) -> str:
        if not isinstance(ciudad, str):
            raise ValueError("La ciudad debe ser texto.")
        ciudad = ciudad.strip()
        if not 2 <= len(ciudad) <= 80 or not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü .'-]+", ciudad):
            raise ValueError("Ingrese una ciudad válida (2 a 80 letras).")
        return ciudad

    @classmethod
    def consultar_clima(cls, ciudad: str) -> dict[str, Any]:
        ciudad = cls._validar_ciudad(ciudad)
        try:
            geo = requests.get(Settings.OPEN_METEO_GEOCODING_URL,
                               params={"name": ciudad, "count": 1, "language": "es", "format": "json"},
                               timeout=Settings.REQUEST_TIMEOUT)
            if geo.status_code != 200:
                raise RuntimeError(f"El servicio de geolocalización respondió HTTP {geo.status_code}.")
            ubicaciones = geo.json().get("results", [])
            if not ubicaciones:
                raise ValueError("No se encontró la ciudad indicada.")
            lugar = ubicaciones[0]
            clima = requests.get(Settings.OPEN_METEO_FORECAST_URL,
                                 params={"latitude": lugar["latitude"], "longitude": lugar["longitude"],
                                         "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                                         "timezone": "auto"}, timeout=Settings.REQUEST_TIMEOUT)
            if clima.status_code != 200:
                raise RuntimeError(f"El servicio meteorológico respondió HTTP {clima.status_code}.")
            actual = clima.json().get("current", {})
            codigo = actual.get("weather_code")
            return {
                "ciudad": lugar.get("name", ciudad), "pais": lugar.get("country", "No informado"),
                "temperatura_c": actual.get("temperature_2m"),
                "humedad_porcentaje": actual.get("relative_humidity_2m"),
                "estado": cls.CODIGOS_CLIMA.get(codigo, "Condición no identificada"),
                "viento_kmh": actual.get("wind_speed_10m"),
                "fecha_hora": clima.json().get("current", {}).get("time"),
                "fuente": "Open-Meteo"
            }
        except requests.exceptions.Timeout as exc:
            raise RuntimeError("La consulta del clima superó el tiempo máximo de espera.") from exc
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError("No hay conexión con el servicio meteorológico.") from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError("No fue posible completar la consulta del clima.") from exc
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, ValueError) and str(exc) == "No se encontró la ciudad indicada.":
                raise
            raise RuntimeError("La respuesta del servicio meteorológico no tiene el formato esperado.") from exc

    @classmethod
    def consultar_tipo_cambio(cls, moneda_origen: str, moneda_destino: str, cantidad: float = 1.0) -> dict[str, Any]:
        origen = cls._validar_moneda(moneda_origen)
        destino = cls._validar_moneda(moneda_destino)
        if isinstance(cantidad, bool) or not isinstance(cantidad, (int, float)) or not 0 < cantidad <= 1_000_000_000:
            raise ValueError("La cantidad debe ser un número mayor que 0 y no superior a 1.000.000.000.")
        if origen == destino:
            tasa = 1.0
            fecha = "Misma moneda"
        else:
            try:
                resp = requests.get(Settings.FRANKFURTER_URL,
                                    params={"from": origen, "to": destino},
                                    timeout=Settings.REQUEST_TIMEOUT)
                if resp.status_code == 404:
                    raise ValueError("No existe información para ese par de monedas.")
                if resp.status_code != 200:
                    raise RuntimeError(f"El servicio de monedas respondió HTTP {resp.status_code}.")
                data = resp.json()
                tasa = data.get("rates", {}).get(destino)
                fecha = data.get("date", "No informada")
                if not isinstance(tasa, (int, float)):
                    raise RuntimeError("La API no entregó una tasa de cambio válida.")
            except requests.exceptions.Timeout as exc:
                raise RuntimeError("La consulta de tipo de cambio superó el tiempo máximo de espera.") from exc
            except requests.exceptions.ConnectionError as exc:
                raise RuntimeError("No hay conexión con el servicio de tipo de cambio.") from exc
            except requests.exceptions.RequestException as exc:
                raise RuntimeError("No fue posible completar la consulta de monedas.") from exc
        return {"moneda_origen": origen, "moneda_destino": destino, "cantidad": float(cantidad),
                "tasa": float(tasa), "resultado": round(float(cantidad) * float(tasa), 4),
                "fecha_tasa": fecha, "fuente": "Frankfurter"}

    @classmethod
    def _validar_moneda(cls, moneda: str) -> str:
        if not isinstance(moneda, str):
            raise ValueError("El código de moneda debe ser texto.")
        codigo = moneda.strip().upper()
        if not re.fullmatch(r"[A-Z]{3}", codigo) or codigo not in cls.MONEDAS_PERMITIDAS:
            raise ValueError("Código de moneda no permitido. Ejemplos: CLP, USD, EUR, BRL.")
        return codigo

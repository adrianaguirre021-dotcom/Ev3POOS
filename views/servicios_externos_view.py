from views.utils import leer_numero


class ServiciosExternosView:
    @staticmethod
    def mostrar_menu() -> int:
        print("\n" + "=" * 55)
        print("       CONSULTAS EXTERNAS - CLIMA Y MONEDAS")
        print("=" * 55)
        print("1.- Consultar clima de una ciudad")
        print("2.- Consultar tipo de cambio")
        print("3.- Ver últimas consultas guardadas")
        print("0.- Volver al menú principal")
        print("=" * 55)
        return leer_numero("Seleccione una opción: ")

    @staticmethod
    def pedir_ciudad() -> str:
        return input("Ingrese la ciudad: ").strip()

    @staticmethod
    def pedir_monedas() -> tuple[str, str, float]:
        origen = input("Moneda de origen (ej. USD): ").strip()
        destino = input("Moneda de destino (ej. CLP): ").strip()
        cantidad_txt = input("Cantidad a convertir: ").strip()
        try:
            cantidad = float(cantidad_txt.replace(",", "."))
        except ValueError:
            raise ValueError("La cantidad debe ser numérica.")
        return origen, destino, cantidad

    @staticmethod
    def mostrar_datos(datos: dict) -> None:
        print("\n--- Resultado ---")
        for clave, valor in datos.items():
            print(f"{clave.replace('_', ' ').capitalize()}: {valor}")

    @staticmethod
    def mostrar_historial(registros: list[dict]) -> None:
        print("\n--- Últimas consultas guardadas ---")
        if not registros:
            print("Todavía no hay consultas guardadas.")
            return
        for registro in registros:
            print(f"[{registro['fecha']}] {registro['tipo']} | {registro['parametro']}")
            print(f"  Resultado: {registro['respuesta']}")

    @staticmethod
    def mensaje(texto: str) -> None:
        print(f"\n[SERVICIOS EXTERNOS] {texto}")

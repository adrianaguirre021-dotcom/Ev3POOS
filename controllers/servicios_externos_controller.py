from services.servicios_externos_service import ServiciosExternosService
from models.consulta_externa_dao import ConsultaExternaDAO
from views.servicios_externos_view import ServiciosExternosView


class ServiciosExternosController:
    """Coordina consultas externas, validación y persistencia local."""
    def __init__(self):
        self.service = ServiciosExternosService()
        self.dao = ConsultaExternaDAO()
        self.view = ServiciosExternosView()

    def ejecutar(self) -> None:
        while True:
            opcion = self.view.mostrar_menu()
            try:
                if opcion == 1:
                    ciudad = self.view.pedir_ciudad()
                    datos = self.service.consultar_clima(ciudad)
                    self.dao.guardar("CLIMA", ciudad, datos)
                    self.view.mostrar_datos(datos)
                    self.view.mensaje("Consulta obtenida y guardada localmente.")
                elif opcion == 2:
                    origen, destino, cantidad = self.view.pedir_monedas()
                    datos = self.service.consultar_tipo_cambio(origen, destino, cantidad)
                    parametro = f"{cantidad} {origen.upper()} a {destino.upper()}"
                    self.dao.guardar("TIPO_CAMBIO", parametro, datos)
                    self.view.mostrar_datos(datos)
                    self.view.mensaje("Consulta obtenida y guardada localmente.")
                elif opcion == 3:
                    self.view.mostrar_historial(self.dao.listar())
                elif opcion == 0:
                    break
                else:
                    self.view.mensaje("Opción no válida.")
            except (ValueError, RuntimeError) as error:
                # Mensajes controlados: no se muestran trazas, URLs internas ni credenciales.
                self.view.mensaje(str(error))
            except Exception:
                self.view.mensaje("Ocurrió un error inesperado. La operación no pudo completarse.")

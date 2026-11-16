import unittest
from models.usuario import Usuario
from services.servicios_externos_service import ServiciosExternosService


class TestSeguridad(unittest.TestCase):
    def test_hash_pbkdf2_y_verificacion(self):
        password_hash = Usuario.encriptar_credencial("ClavePrueba2026!")
        usuario = Usuario("alumno", password_hash, "Alumno Prueba")
        self.assertTrue(password_hash.startswith("pbkdf2_sha256$"))
        self.assertTrue(usuario.verificar_credencial("ClavePrueba2026!"))
        self.assertFalse(usuario.verificar_credencial("ClaveIncorrecta2026"))

    def test_hash_usa_sal_distinta(self):
        hash_a = Usuario.encriptar_credencial("ClavePrueba2026!")
        hash_b = Usuario.encriptar_credencial("ClavePrueba2026!")
        self.assertNotEqual(hash_a, hash_b)

    def test_rechaza_contrasena_debil(self):
        with self.assertRaises(ValueError):
            Usuario.encriptar_credencial("1234")


class TestValidacionesAPI(unittest.TestCase):
    def test_ciudad_valida(self):
        self.assertEqual(ServiciosExternosService._validar_ciudad("Chillán"), "Chillán")

    def test_rechaza_ciudad_invalida(self):
        with self.assertRaises(ValueError):
            ServiciosExternosService._validar_ciudad("Santiago; DROP TABLE")

    def test_moneda_valida(self):
        self.assertEqual(ServiciosExternosService._validar_moneda("clp"), "CLP")

    def test_rechaza_moneda_invalida(self):
        with self.assertRaises(ValueError):
            ServiciosExternosService._validar_moneda("XXX")


if __name__ == "__main__":
    unittest.main()

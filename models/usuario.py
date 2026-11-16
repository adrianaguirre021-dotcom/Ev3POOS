import hashlib
import hmac
import re
import secrets


class Usuario:
    """Entidad de usuario con contraseñas protegidas mediante PBKDF2-HMAC-SHA256.

    También acepta hashes SHA-256 antiguos para permitir la migración gradual.
    Formato nuevo: pbkdf2_sha256$iteraciones$sal_hex$hash_hex.
    """
    ROLES = {"Administrador", "Medico", "Operador"}
    PBKDF2_ITERATIONS = 310_000

    def __init__(self, username: str, password_hash: str, nombre_completo: str,
                 rol: str = "Operador", id_usuario: int | None = None):
        self.id_usuario = id_usuario
        self.username = username
        self.password_hash = password_hash
        self.nombre_completo = nombre_completo
        self.rol = rol

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre de usuario no puede estar vacío.")
        limpio = valor.strip().lower()
        if len(limpio) < 3 or not re.fullmatch(r"[a-zA-Z0-9_.-]+", limpio):
            raise ValueError("El usuario debe tener al menos 3 caracteres y usar letras, números, punto, guion o guion bajo.")
        self._username = limpio

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @password_hash.setter
    def password_hash(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El hash de la contraseña no puede estar vacío.")
        valor = valor.strip()
        es_sha256_antiguo = bool(re.fullmatch(r"[a-fA-F0-9]{64}", valor))
        partes = valor.split("$")
        es_pbkdf2 = (len(partes) == 4 and partes[0] == "pbkdf2_sha256"
                     and partes[1].isdigit()
                     and re.fullmatch(r"[a-fA-F0-9]{32,128}", partes[2])
                     and re.fullmatch(r"[a-fA-F0-9]{64}", partes[3]))
        if not (es_sha256_antiguo or es_pbkdf2):
            raise ValueError("Formato de hash de contraseña no válido.")
        self._password_hash = valor.lower()

    @property
    def nombre_completo(self) -> str:
        return self._nombre_completo

    @nombre_completo.setter
    def nombre_completo(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ValueError("El nombre completo debe tener al menos 3 caracteres.")
        self._nombre_completo = valor.strip().title()

    @property
    def rol(self) -> str:
        return self._rol

    @rol.setter
    def rol(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El rol no puede estar vacío.")
        rol = valor.strip().capitalize()
        if rol not in self.ROLES:
            raise ValueError("Rol no permitido.")
        self._rol = rol

    @staticmethod
    def encriptar_credencial(clave_plana: str) -> str:
        if not isinstance(clave_plana, str) or len(clave_plana) < 10:
            raise ValueError("La contraseña debe tener al menos 10 caracteres.")
        if not re.search(r"[A-Za-z]", clave_plana) or not re.search(r"[0-9]", clave_plana):
            raise ValueError("La contraseña debe incluir letras y números.")
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", clave_plana.encode("utf-8"), salt,
                                     Usuario.PBKDF2_ITERATIONS)
        return f"pbkdf2_sha256${Usuario.PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"

    @staticmethod
    def validar_credenciales_ingreso(username: str, clave_plana: str) -> tuple[bool, str]:
        if not isinstance(username, str) or not username.strip():
            return False, "El campo usuario es obligatorio."
        if not isinstance(clave_plana, str) or not clave_plana:
            return False, "El campo contraseña es obligatorio."
        if len(username.strip()) < 3 or not re.fullmatch(r"[a-zA-Z0-9_.-]+", username.strip()):
            return False, "El nombre de usuario tiene un formato no válido."
        if len(clave_plana) < 4:
            return False, "La contraseña debe tener al menos 4 caracteres."
        return True, "Credenciales con formato válido."

    def verificar_credencial(self, clave_ingresada: str) -> bool:
        if not isinstance(clave_ingresada, str) or not clave_ingresada:
            return False
        try:
            if self.password_hash.startswith("pbkdf2_sha256$"):
                _, iterations, salt_hex, expected = self.password_hash.split("$")
                actual = hashlib.pbkdf2_hmac("sha256", clave_ingresada.encode("utf-8"),
                                             bytes.fromhex(salt_hex), int(iterations)).hex()
                return hmac.compare_digest(expected, actual)
            # Compatibilidad con cuentas creadas por la versión anterior SHA-256.
            legacy = hashlib.sha256(clave_ingresada.encode("utf-8")).hexdigest()
            return hmac.compare_digest(self.password_hash, legacy)
        except (ValueError, TypeError):
            return False

    def necesita_migracion_hash(self) -> bool:
        return not self.password_hash.startswith("pbkdf2_sha256$")

    def __str__(self) -> str:
        return f"Usuario [ID: {self.id_usuario or 'Nuevo'}] | Login: {self.username} | Nombre: {self.nombre_completo} | Rol: {self.rol} | Contraseña: protegida"

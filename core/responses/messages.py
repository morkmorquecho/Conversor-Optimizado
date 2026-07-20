class UserMessages:
    """Mensajes relacionados a usuarios"""

    # Success
    USER_CREATED = "Usuario creado. Revisa tu correo para verificar la cuenta."
    USER_VERIFIED = "Usuario verificado con éxito."
    USER_ACTIVATED = "Usuario {username} activado."
    USER_DEACTIVATED = "Usuario {username} desactivado."
    USER_UPDATED = "Usuario actualizado correctamente."
    USER_DELETED = "Usuario eliminado correctamente."

    # Email
    VERIFICATION_EMAIL_SENT = "Correo de verificación enviado."
    PASSWORD_RESET_EMAIL_SENT = "Se envió un correo para restablecer la contraseña."
    EMAIL_UPDATED = "El email se actualizó correctamente."

    # Info
    EMAIL_SENT_IF_EXISTS = "Si el correo existe, recibirás instrucciones."
    LOGIN_SUCCESS = "Inicio de sesión exitoso."
    LOGOUT_SUCCESS = "Sesión cerrada correctamente."

    # Errors
    USER_NOT_FOUND = "Usuario no encontrado."
    USER_ALREADY_VERIFIED = "El usuario ya fue verificado."
    EMAIL_REQUIRED = "El email es obligatorio."
    EMAIL_ALREADY_IN_USE = "El email ya está en uso."
    ACCOUNT_DISABLED = "La cuenta está desactivada."
    ACCOUNT_LOCKED = "Cuenta bloqueada temporalmente."


class AuthMessages:
    """Mensajes de autenticación"""

    # Success
    PASSWORD_RESET_SUCCESS = "Contraseña restablecida con éxito."
    PASSWORD_CHANGED_SUCCESS = "Tu contraseña ha sido actualizada correctamente."

    # Errors
    PASSWORD_REQUIRED = "El campo contraseña es obligatorio."
    PASSWORD_TOO_WEAK = "La contraseña no cumple con los requisitos de seguridad."
    PASSWORD_MISMATCH = "Las contraseñas no coinciden."
    PASSWORD_INCORRECT = "La contraseña actual es incorrecta."
    PERMISSION_DENIED = "No tienes permisos para realizar esta acción."

    EMAIL_OR_USERNAME_REQUIRED = "Debes proporcionar username o email."
    CREDENTIALS_INVALID = "Las Credenciales son incorrectas verificalas"

    ACCOUNT_CONFIRMATION_REQUIRED = "Debes confirmar tu cuenta antes de iniciar sesión."
    SESSION_EXPIRED = "Tu sesión ha expirado."
    LOGIN_REQUIRED = "Debes iniciar sesión para continuar."

    TOKEN_NOT_PROVIDED = "Token no proporcionado."
    TOKEN_INVALID_OR_EXPIRED = "Token inválido o expirado."
    VERIFICATION_EXPIRED = "El enlace de verificación ha expirado."
    PASSWORD_RESET_TOKEN_INVALID = "El token de recuperación es inválido o expiró."

    USE_PROVIDER_OR_SET_PASSWORD ="inicia sesión con google y establece una contraseña para poder iniciar sesión con correo y contraseña"

class ValidationMessages:
    """Mensajes de validación genéricos"""

    FIELD_REQUIRED = "Este campo es obligatorio."
    INVALID_FORMAT = "Formato inválido."
    INVALID_PARAMETERS = "Parámetros inválidos."
    MISSING_PARAMETERS = "Faltan parámetros requeridos."
    VALUE_TOO_LONG = "El valor es demasiado largo."
    VALUE_TOO_SHORT = "El valor es demasiado corto."


class SystemMessages:
    """Mensajes del sistema / generales"""

    DEFAULT_SUCCESS = "Operación exitosa."
    UNEXPECTED_ERROR = "Error inesperado. Revisa los logs."
    CONNECTION_ERROR = "Error de conexión."

    TOO_MANY_REQUESTS = "Demasiadas solicitudes. Intenta más tarde."
    SUSPICIOUS_ACTIVITY = "Actividad sospechosa detectada."

    SERVICE_TIMEOUT = "El servicio tardó demasiado. Intenta nuevamente."
    SERVICE_UNAVAILABLE = "Servicio no disponible. Intenta más tarde."
    EXTERNAL_API_ERROR = "Error comunicándose con servicio externo."

    EMAIL_SEND_FAILED = "No se pudo enviar el correo."
    EMAIL_NOTIFICATION_PENDING = "Operación completada (notificación pendiente)."


class DatabaseMessages:
    """Errores de base de datos"""

    RESOURCE_EXISTS = "El recurso ya existe."
    RESOURCE_NOT_FOUND = "Recurso no encontrado."
    RESOURCE_NOT_ACTIVE = "El recurso no está activo."

    DUPLICATE_ENTRY = "Ya existe un registro con estos datos."
    INVALID_REFERENCE = "Referencia inválida."
    FOREIGN_KEY_VIOLATION = "Referencia a recurso inexistente."
    CONSTRAINT_VIOLATION = "Violación de restricción de datos."
    DATA_INTEGRITY_ERROR = "Error de integridad de datos."
    DATABASE_ERROR = "Error del sistema. Intenta más tarde."


class ErrorMessages:
    """
    Mensajes globales para manejo de errores (Sentry, middleware, etc.)
    """

    # OAuth
    OAUTH_ERROR = "Error en autenticación con proveedor externo."

    # Alias reutilizando otras clases
    INVALID_DATA = ValidationMessages.INVALID_PARAMETERS

    RESOURCE_EXISTS = DatabaseMessages.RESOURCE_EXISTS
    INVALID_REFERENCE = DatabaseMessages.INVALID_REFERENCE
    DATA_INTEGRITY_ERROR = DatabaseMessages.DATA_INTEGRITY_ERROR
    DATABASE_ERROR = DatabaseMessages.DATABASE_ERROR

    SERVICE_TIMEOUT = SystemMessages.SERVICE_TIMEOUT
    SERVICE_UNAVAILABLE = SystemMessages.SERVICE_UNAVAILABLE
    EXTERNAL_API_ERROR = SystemMessages.EXTERNAL_API_ERROR

    UNEXPECTED_ERROR = SystemMessages.UNEXPECTED_ERROR
    DEFAULT_SUCCESS = SystemMessages.DEFAULT_SUCCESS
    CONNECTION_ERROR = SystemMessages.CONNECTION_ERROR
    EMAIL_NOTIFICATION_PENDING = SystemMessages.EMAIL_NOTIFICATION_PENDING

    class Authentication:
        OAUTH_FAILED = "No se pudo autenticar con el proveedor externo."
        TOKEN_EXPIRED = AuthMessages.TOKEN_INVALID_OR_EXPIRED

    class Database:
        DUPLICATE_ENTRY = DatabaseMessages.DUPLICATE_ENTRY
        FOREIGN_KEY_VIOLATION = DatabaseMessages.FOREIGN_KEY_VIOLATION
        CONSTRAINT_VIOLATION = DatabaseMessages.CONSTRAINT_VIOLATION

    class Network:
        CONNECTION_LOST = "Conexión perdida con el servidor."
        SSL_ERROR = "Error de certificado SSL."
        DNS_ERROR = "No se puede resolver el nombre del servidor."

    class FileSystem:
        UPLOAD_FAILED = "Error al subir el archivo."
        FILE_TOO_LARGE = "El archivo excede el tamaño permitido."
        INVALID_FILE_TYPE = "Tipo de archivo no permitido."

    class WishList:
        ALREADY_EXIST = "ya existe"








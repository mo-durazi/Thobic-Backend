import enum


class UserRole(enum.Enum):
    CLIENT = "client"
    ADMIN = "admin"
    PROVIDER = "provider"
    TAILOR = "tailor"

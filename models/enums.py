import enum


class UserRole(enum.Enum):
    CLIENT = "client"
    ADMIN = "admin"
    PROVIDER = "provider"
    TAILOR = "tailor"


class ProfileStatus(enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    BUSY = "busy"
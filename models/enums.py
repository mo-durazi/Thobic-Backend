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


class OrderStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    TAILOR_REJECTED = "tailor_rejected"
    CLIENT_REJECTED = "client_rejected"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    ON_THE_WAY = "on_the_way"
    DELIVERED = "delivered"
    CANCELED = "canceled"
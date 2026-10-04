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


class MaterialTexture(enum.Enum):
    SMOOTH = "smooth"
    ROUGH = "rough"


class MaterialPattern(enum.Enum):
    PLAIN = "plain"
    PATTERNED = "patterned"


class MaterialSeason(enum.Enum):
    SUMMER = "summer"
    WINTER = "winter"
    ALL_SEASONS = "all_seasons"
    SPRING = "spring"


class MaterialStand(enum.Enum):
    STAND = "stand"
    HALF_STAND = "half_stand"
    LOOSE = "loose"


class MaterialOrderStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ON_THE_WAY = "on_the_way"
    DELIVERED = "delivered"
import enum


class UserRole(enum.Enum):
    CLIENT = "client"
    ADMIN = "admin"
    PROVIDER = "provider"
    TAILOR = "tailor"


class ShopStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    BUSY = "busy"


class MaterialTexture(enum.Enum):
    ROUGH = "rough"
    SMOOTH = "smooth"


class MaterialPattern(enum.Enum):
    PATTERN = "pattern"
    PLAIN = "plain"


class MaterialSeason(enum.Enum):
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"


class MaterialStand(enum.Enum):
    STAND = "stand"
    HALF_STAND = "half-stand"
    LOOSE = "loose"
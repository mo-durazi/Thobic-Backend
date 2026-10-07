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


class ThoubNationality(str, enum.Enum):
    EMIRATI = "Emirati"
    SAUDI = "Saudi"
    BAHRAINI = "Bahraini"
    KUWAITI = "Kuwaiti"
    QATARI = "Qatari"


class ThoubCollar(str, enum.Enum):
    NORMAL = "Normal"
    CHINESE = "Chinese"
    V_SHAPE = "V-shape"
    V2_SHAPE = "V2-shape"
    STICKS_SHAPE = "sticks-shape"


class ThoubPlacket(str, enum.Enum):
    HIDDEN = "Hidden"
    HIDDEN_V = "hidden-v"
    NORMAL = "Normal"
    NORMAL_V = "Normal-v"
    ZIPPER = "zipper"


class ThoubChestPocket(str, enum.Enum):
    SHAPE1 = "shape1"
    SHAPE2 = "shape2"
    SHAPE3 = "shape3"
    SHAPE4 = "shape4"


class ThoubSidePocket(str, enum.Enum):
    DOUBLE = "Double"
    SIGLE = "sigle"


class ThoubSleeves(str, enum.Enum):
    NORMAL = "Normal"
    CUFF_WITH_BUTTONS = "Cuff with buttons"

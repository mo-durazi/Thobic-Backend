from models.user import UserModel
from models.enums import UserRole

# All demo accounts use the same password so they are easy to log in with.
DEMO_PASSWORD = "123"

# (username, email, role)
USERS = [
    # Admin
    ("admin", "admin@thobic.bh", UserRole.ADMIN),

    # Tailor shops
    ("alwasmi_tailors", "info@alwasmi.bh", UserRole.TAILOR),
    ("dar_alkhayat", "contact@daralkhayat.bh", UserRole.TAILOR),

    # Material providers
    ("gulf_textiles", "sales@gulftextiles.bh", UserRole.PROVIDER),
    ("japan_fabric_house", "orders@jfh.bh", UserRole.PROVIDER),

    # Clients
    ("arjun_dev", "arjun@devmail.in", UserRole.CLIENT),
    ("emma_johnson", "emma.johnson@email.com", UserRole.CLIENT),
    ("fatima_ali", "fatima.ali@mail.ae", UserRole.CLIENT),
    ("lucas_silva", "lucas.silva@correo.br", UserRole.CLIENT),
    ("elena_popov", "elena.popov@mail.ru", UserRole.CLIENT),
]


def create_test_users():
    users = []

    for username, email, role in USERS:
        user = UserModel(username=username, email=email, role=role)
        user.set_password(DEMO_PASSWORD)
        users.append(user)

    return users


user_list = create_test_users()
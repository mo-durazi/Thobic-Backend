from models.enums import ShopStatus

# Profiles are linked to users by username; seed.py swaps the username for the user's id.
# branch and status are only for tailor shops.
profile_list = [
    # Tailor shops
    {
        "username": "alwasmi_tailors",
        "display_name": "Al Wasmi Tailors",
        "road_no": 1705,
        "block_no": 317,
        "building_no": 42,
        "phone_number": "+973 1722 1100",
        "branch": "Manama",
        "status": ShopStatus.OPEN,
    },
    {
        "username": "dar_alkhayat",
        "display_name": "Dar Al Khayat",
        "road_no": 2810,
        "block_no": 928,
        "building_no": 15,
        "phone_number": "+973 1777 4520",
        "branch": "Riffa",
        "status": ShopStatus.BUSY,
    },

    # Material providers
    {
        "username": "gulf_textiles",
        "display_name": "Gulf Textiles",
        "road_no": 4012,
        "block_no": 640,
        "building_no": 108,
        "phone_number": "+973 1787 3300",
    },
    {
        "username": "japan_fabric_house",
        "display_name": "Japan Fabric House",
        "road_no": 3321,
        "block_no": 333,
        "building_no": 7,
        "phone_number": "+973 1729 6610",
    },

    # Clients
    {
        "username": "arjun_dev",
        "display_name": "Arjun",
        "road_no": 1205,
        "block_no": 712,
        "building_no": 220,
        "phone_number": "+973 3300 1001",
    },
    {
        "username": "fatima_ali",
        "display_name": "Fatima Ali",
        "road_no": 4407,
        "block_no": 1044,
        "building_no": 31,
        "phone_number": "+973 3300 1003",
    },
]
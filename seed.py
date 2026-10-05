# seed.py
#
# Fills the database with demo data. Run AFTER migrations:
#   pipenv run alembic upgrade head
#   pipenv run python seed.py
#
# WARNING: it deletes all existing rows first, so every run starts from the same demo state.

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.environment import DATABASE_URL

import models  # registers every model so relationships resolve
from models.user import UserModel
from models.profile import ProfileModel
from models.material import MaterialModel
from models.material_order import MaterialOrderModel
from models.thoub_order import ThoubOrderModel
from models.client_measurements import ClientMeasurementsModel

from data.user_data import user_list, DEMO_PASSWORD
from data.profile_data import profile_list
from data.material_data import material_list


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def clear_tables(db):
    # Children first, so no foreign key blocks a delete
    for model in (
        MaterialOrderModel,
        ThoubOrderModel,
        MaterialModel,
        ClientMeasurementsModel,
        ProfileModel,
        UserModel,
    ):
        db.query(model).delete()


def seed():
    db = SessionLocal()

    try:
        print("Clearing old data...")
        clear_tables(db)

        print("Seeding users...")
        db.add_all(user_list)
        db.flush()  # assigns ids without committing

        user_ids = {user.username: user.id for user in user_list}

        print("Seeding profiles...")
        for data in profile_list:
            data = dict(data)
            data["user_id"] = user_ids[data.pop("username")]
            db.add(ProfileModel(**data))

        print("Seeding materials...")
        for data in material_list:
            data = dict(data)
            data["source_id"] = user_ids[data.pop("owner")]
            data.setdefault("is_available", True)
            data.setdefault("is_deleted", False)
            db.add(MaterialModel(**data))

        print("Seeding client measurements...")
        db.add(ClientMeasurementsModel(
            client_id=user_ids["arjun_dev"],
            neck=40, chest=104, arm=62, shoulders=47,
            waist=90, wrist=18, length=146, hips=106,
        ))

        db.commit()

        print("\nDatabase seeding complete!")
        print(f"All demo accounts use the password: {DEMO_PASSWORD}")
        print("  admin              -> admin")
        print("  alwasmi_tailors    -> tailor")
        print("  dar_alkhayat       -> tailor")
        print("  gulf_textiles      -> provider")
        print("  japan_fabric_house -> provider")
        print("  arjun_dev          -> client (has measurements)")

    except Exception as e:
        db.rollback()
        print("An error occurred, nothing was saved:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed()
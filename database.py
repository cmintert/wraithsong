from sqlalchemy import create_engine, declarative_base
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, echo=True)

# Base class for models
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Function to initialize the database and create tables"""
    Base.metadata.create_all(bind=engine)


class SaveGame(Base):
    __tablename__ = "savegames"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    game_name = Column(String(100))
    game_data = Column(Text)

    def __init__(self, game_name, game_data):
        self.game_name = game_name
        self.game_data = game_data

    def __repr__(self):
        return f"<SaveGame(id={self.id}, timestamp={self.timestamp}, game_name={self.game_name})>"


class GameObject(Base):
    __tablename__ = "gameobjects"

    internal_id = Column(String, primary_key=True)
    object_id = Column(String)
    name = Column(String)
    object_type = Column(String(50))

    # Derived tables will populate this column to identify the subtype
    type = Column(String(50))

    __mapper_args__ = {"polymorphic_identity": "gameobject", "polymorphic_on": type}


class Terrain(GameObject):
    __tablename__ = "terrains"

    internal_id = Column(
        String, ForeignKey("gameobjects.internal_id"), primary_key=True
    )
    terrain_type = Column(String)
    elevation = Column(Integer)

    # Other dynamic attributes from the 'terrain.json' file can be added as needed.
    # For instance, if you have an attribute called 'humidity' in the json file:
    # humidity = Column(Integer)

    __mapper_args__ = {
        "polymorphic_identity": "terrain",
    }


class Structure(GameObject):
    __tablename__ = "structures"

    internal_id = Column(
        String, ForeignKey("gameobjects.internal_id"), primary_key=True
    )
    structure_type = Column(String)

    # Other dynamic attributes from the 'structure.json' file can be added as needed.
    # For example:
    # material = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": "structure",
    }


class DbSession:
    def __enter__(self):
        self.session = SessionLocal()
        return self.session

    def __exit__(self, type, value, traceback):
        self.session.close()


class DbInteraction:
    def __init__(self, session: Session):
        self.db = session

    def create_game_object(self, game_object: GameObject):
        self.db.add(game_object)
        self.db.commit()
        self.db.refresh(game_object)
        return game_object

    def get_game_object(self, internal_id: str):
        return (
            self.db.query(GameObject)
            .filter(GameObject.internal_id == internal_id)
            .first()
        )

    def get_game_objects(self, skip: int = 0, limit: int = 100):
        return self.db.query(GameObject).offset(skip).limit(limit).all()

    def update_game_object(self, game_object: GameObject):
        self.db.merge(game_object)
        self.db.commit()
        return game_object

    def delete_game_object(self, internal_id: str):
        obj = (
            self.db.query(GameObject)
            .filter(GameObject.internal_id == internal_id)
            .first()
        )
        self.db.delete(obj)
        self.db.commit()

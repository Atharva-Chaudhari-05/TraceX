from backend.app.auth.models import User, Role

def test_models_importable():
    """
    Ensure that the SQLAlchemy declarative mappings are valid and importable without errors.
    """
    assert User.__tablename__ == "users"
    assert Role.__tablename__ == "roles"

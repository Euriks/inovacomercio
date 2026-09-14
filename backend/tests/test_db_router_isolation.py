def test_db_router_instance():
    from app.core.db_router import DatabaseRouter
    engine = DatabaseRouter.get_engine("sqlite:///:memory:")
    assert engine is not None
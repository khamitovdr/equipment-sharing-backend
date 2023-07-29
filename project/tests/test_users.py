from app import main


def test_ping(test_app_with_db):
    # Given
    # test_app

    # When
    response = test_app_with_db.get("/users/")

    # Then
    assert response.status_code == 200
    assert response.json() == []

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_redirects_to_demo() -> None:
    response = client.get('/', follow_redirects=False)
    assert response.status_code in {307, 302}
    assert response.headers['location'] == '/demo/'


def test_demo_ui_serves_html() -> None:
    response = client.get('/demo/')
    assert response.status_code == 200
    assert 'OmniFlow Demo Console' in response.text

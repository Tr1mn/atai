from tests.conftest import _auth_headers


def _request_payload():
    return {
        "origin": "Бишкек",
        "days": "2-3",
        "companions": "friends",
        "interests": ["nature", "lakes", "photo"],
        "travel_format": "comfortable",
        "mood": "active",
        "difficulty": "easy",
        "budget": "middle",
        "season": "summer",
        "accommodation": "guesthouse",
        "transport": "minivan",
        "activities": ["horse", "hot_springs"],
        "preferred_places": ["Сон-Куль", "Иссык-Куль"],
        "distance": "5-8",
        "priority": "beautiful_views",
        "notes": "Хотим красивый маршрут без сложного треккинга",
    }


def _offer_payload():
    return {
        "title": "Сон-Куль с юртами и конной прогулкой",
        "description": "Комфортный маршрут для небольшой группы",
        "price_total": 480.0,
        "price_per_person": 160.0,
        "duration_days": 3,
        "included": "Трансфер, проживание в юрте, питание, гид",
        "message": "Можем адаптировать даты под вашу группу",
    }


def test_tourist_creates_travel_request(client, tourist):
    resp = client.post(
        "/api/travel-requests/",
        json=_request_payload(),
        headers=_auth_headers(tourist),
    )
    assert resp.status_code == 201, resp.json()
    data = resp.json()
    assert data["origin"] == "Бишкек"
    assert data["preferred_places"] == ["Сон-Куль", "Иссык-Куль"]
    assert data["status"] == "open"


def test_partner_can_see_open_requests_and_send_offer(client, tourist, partner_user, partner):
    created = client.post(
        "/api/travel-requests/",
        json=_request_payload(),
        headers=_auth_headers(tourist),
    )
    request_id = created.json()["id"]

    open_resp = client.get("/api/travel-requests/open", headers=_auth_headers(partner_user))
    assert open_resp.status_code == 200
    assert any(item["id"] == request_id for item in open_resp.json())

    offer_resp = client.post(
        f"/api/travel-requests/{request_id}/offers",
        json=_offer_payload(),
        headers=_auth_headers(partner_user),
    )
    assert offer_resp.status_code == 201, offer_resp.json()
    assert offer_resp.json()["partner_company"] == partner.company_name


def test_tourist_accepts_offer_and_request_becomes_matched(client, tourist, partner_user, partner):
    created = client.post(
        "/api/travel-requests/",
        json=_request_payload(),
        headers=_auth_headers(tourist),
    )
    request_id = created.json()["id"]
    offer = client.post(
        f"/api/travel-requests/{request_id}/offers",
        json=_offer_payload(),
        headers=_auth_headers(partner_user),
    )

    accepted = client.put(
        f"/api/travel-requests/offers/{offer.json()['id']}/accept",
        headers=_auth_headers(tourist),
    )
    assert accepted.status_code == 200, accepted.json()
    assert accepted.json()["status"] == "accepted"

    mine = client.get("/api/travel-requests/me", headers=_auth_headers(tourist))
    assert mine.json()[0]["status"] == "matched"


def test_other_tourist_cannot_accept_offer(client, tourist, tourist2, partner_user, partner):
    created = client.post(
        "/api/travel-requests/",
        json=_request_payload(),
        headers=_auth_headers(tourist),
    )
    request_id = created.json()["id"]
    offer = client.post(
        f"/api/travel-requests/{request_id}/offers",
        json=_offer_payload(),
        headers=_auth_headers(partner_user),
    )

    resp = client.put(
        f"/api/travel-requests/offers/{offer.json()['id']}/accept",
        headers=_auth_headers(tourist2),
    )
    assert resp.status_code == 403

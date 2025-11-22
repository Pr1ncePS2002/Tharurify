from app.auth.auth_utils import create_access_token, create_refresh_token, decode_token

def test_access_refresh_distinct_jti():
    access = create_access_token({"sub": "user"})
    refresh = create_refresh_token({"sub": "user"})
    a_payload = decode_token(access)
    r_payload = decode_token(refresh)
    assert a_payload["jti"] != r_payload["jti"]
    assert a_payload["token_type"] == "access"
    assert r_payload["token_type"] == "refresh"

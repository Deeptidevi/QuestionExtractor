from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password


def test_password_hashing_and_verification():
    raw = "MySecurePassword123!"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_generation_and_decoding():
    user_id = "test-uuid-1234"
    token = create_access_token(subject=user_id, extra_claims={"role": "admin"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["role"] == "admin"


def test_jwt_token_invalid_tampering():
    token = create_access_token(subject="user1")
    tampered = token[:-4] + "fake"
    payload = decode_access_token(tampered)
    assert payload is None

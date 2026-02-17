import hashlib
import time
from custom_components.relay_emulator_2n.http_server import DigestAuth, NONCE_EXPIRY_SECONDS


def extract_nonce_from_challenge(challenge: str) -> str:
    # naive parse: find nonce="..."
    token = 'nonce="'
    i = challenge.find(token)
    if i == -1:
        return ""
    i += len(token)
    j = challenge.find('"', i)
    return challenge[i:j]


def test_digest_verify_success():
    username = "admin"
    password = "2n"
    realm = "2N"

    da = DigestAuth(username, password)

    challenge = da.create_challenge()
    nonce = extract_nonce_from_challenge(challenge)
    assert nonce

    nc = "00000001"
    cnonce = "testcnonce"
    uri = "/2n-relay/api/relay/status"

    ha1 = hashlib.md5(f"{username}:{realm}:{password}".encode()).hexdigest()
    ha2 = hashlib.md5(f"GET:{uri}".encode()).hexdigest()
    response = hashlib.md5(f"{ha1}:{nonce}:{nc}:{cnonce}:auth:{ha2}".encode()).hexdigest()

    auth_header = (
        f'Digest username="{username}", realm="{realm}", nonce="{nonce}", '
        f'uri="{uri}", response="{response}", qop="auth", nc="{nc}", cnonce="{cnonce}"'
    )

    assert da.verify_response(auth_header, "GET", uri) is True


def test_digest_verify_invalid_response():
    da = DigestAuth("admin", "2n")
    challenge = da.create_challenge()
    nonce = extract_nonce_from_challenge(challenge)
    uri = "/2n-relay/api/relay/status"

    # incorrect response
    auth_header = (
        f'Digest username="admin", realm="2N", nonce="{nonce}", '
        f'uri="{uri}", response="deadbeef", qop="auth", nc="00000001", cnonce="x"'
    )

    assert da.verify_response(auth_header, "GET", uri) is False


def test_nonce_expiry():
    da = DigestAuth("admin", "2n")
    challenge = da.create_challenge()
    nonce = extract_nonce_from_challenge(challenge)
    assert nonce in da.nonce_cache

    # simulate expiry
    da.nonce_cache[nonce] = time.time() - (NONCE_EXPIRY_SECONDS + 10)

    nc = "00000001"
    cnonce = "cn"
    uri = "/2n-relay/api/relay/status"

    ha1 = hashlib.md5(f"admin:2N:2n".encode()).hexdigest()
    ha2 = hashlib.md5(f"GET:{uri}".encode()).hexdigest()
    response = hashlib.md5(f"{ha1}:{nonce}:{nc}:{cnonce}:auth:{ha2}".encode()).hexdigest()

    auth_header = (
        f'Digest username="admin", realm="2N", nonce="{nonce}", '
        f'uri="{uri}", response="{response}", qop="auth", nc="{nc}", cnonce="{cnonce}"'
    )

    # expired nonce should be rejected
    assert da.verify_response(auth_header, "GET", uri) is False
    assert nonce not in da.nonce_cache

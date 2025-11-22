from app.auth.auth_utils import _password_meets_policy

def test_password_policy_valid():
    assert _password_meets_policy("StrongPass1!") is True

def test_password_policy_invalid_short():
    assert _password_meets_policy("Ab1!") is False

def test_password_policy_missing_digit():
    assert _password_meets_policy("NoDigits!!AA") is False

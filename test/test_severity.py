from incidents.severity import get_severity


def test_healthy_returns_none():
    assert get_severity(50) is None
    assert get_severity(79) is None


def test_low_boundary():
    assert get_severity(80) == "LOW"
    assert get_severity(89) == "LOW"


def test_medium_boundary():
    assert get_severity(90) == "MEDIUM"
    assert get_severity(94) == "MEDIUM"


def test_high_boundary():
    assert get_severity(95) == "HIGH"
    assert get_severity(100) == "HIGH"


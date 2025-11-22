from app.services.resume_parser import parse_resume, parse_entire_resume

def test_resume_cache_basic():
    content = b"Sample Resume Skills: Python Java Email: test@example.com"
    r1 = parse_resume(content, "resume.txt")
    r2 = parse_resume(content, "resume.txt")
    assert r1 == r2
    assert r1.get("success") is True

def test_resume_cache_full():
    content = b"Full Resume Phone: +1 555-123-4567 Skills: Python"
    f1 = parse_entire_resume(content, "resume.txt")
    f2 = parse_entire_resume(content, "resume.txt")
    assert f1 == f2
    assert f1.get("success") is True

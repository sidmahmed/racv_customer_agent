from scripts.ingest import category_from_url, chunk


def test_category_from_url():
    assert (
        category_from_url("https://www.racv.com.au/help-and-support/car-insurance.html")
        == "car-insurance"
    )
    assert category_from_url("https://www.racv.com.au/help-and-support.html") == "help-and-support"


def test_chunk_merges_heading_and_body():
    html = (
        "<div id='main'><h1>Car insurance FAQs</h1>"
        "<h2>Premium and excess</h2>"
        "<h3>How do I update my policy?</h3>"
        "<p>You can update it online.</p></div>"
    )
    chunks = chunk(html)
    assert any("update it online" in c["content"] for c in chunks)
    assert any("Premium and excess" in c["heading_path"] for c in chunks)


def test_chunk_drops_bare_headings():
    html = (
        "<div id='main'><h1>Car insurance FAQs</h1>"
        "<h2>Looking for something else?</h2></div>"
    )
    chunks = chunk(html)
    assert chunks == []


def test_chunk_strips_feedback_widget_boilerplate():
    html = (
        "<div id='main'><h1>FAQs</h1>"
        "<h3>How do I update my policy?</h3>"
        "<p>You can update it online. Did this answer your question? Yes No "
        "Thank you for your feedback Thank you for your feedback</p></div>"
    )
    chunks = chunk(html)
    assert all("Did this answer" not in c["content"] for c in chunks)
    assert any("update it online" in c["content"] for c in chunks)

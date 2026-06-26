from app import tools


def test_search_help_center_formats_results(monkeypatch):
    class FakeResult:
        data = [
            {
                "source_url": "https://www.racv.com.au/help-and-support/car-insurance.html",
                "heading_path": "Car insurance FAQs > Premium and excess",
                "content": "You can update your policy online or by calling RACV.",
                "rrf_score": 0.05,
            }
        ]

    class FakeRPC:
        def execute(self):
            return FakeResult()

    class FakeSupabase:
        def rpc(self, name, params):
            assert name == "hybrid_search"
            assert "query_embedding" in params
            return FakeRPC()

    monkeypatch.setattr(tools, "_embed", lambda text: [0.0] * 1536)
    monkeypatch.setattr(tools, "get_supabase", lambda: FakeSupabase())

    result = tools.search_help_center.invoke(
        {"query": "how do I update my policy", "category": "car-insurance"}
    )

    assert "car-insurance.html" in result
    assert "update your policy" in result


def test_search_help_center_drops_uncorroborated_weak_matches(monkeypatch):
    # A score at or below 1/(rrf_k+1) means only one of full-text/semantic
    # search found it (e.g. ranked #1 there alone) -- not a real match.
    weak_score = 1.0 / (tools.settings.rrf_k + 1)

    class FakeResult:
        data = [
            {
                "source_url": "https://www.racv.com.au/help-and-support/holidays.html",
                "heading_path": "Hotels and holiday packages FAQs",
                "content": "Irrelevant content that just happens to rank #1 alone.",
                "rrf_score": weak_score,
            }
        ]

    class FakeRPC:
        def execute(self):
            return FakeResult()

    class FakeSupabase:
        def rpc(self, name, params):
            return FakeRPC()

    monkeypatch.setattr(tools, "_embed", lambda text: [0.0] * 1536)
    monkeypatch.setattr(tools, "get_supabase", lambda: FakeSupabase())

    result = tools.search_help_center.invoke({"query": "what's the weather today"})
    assert "No matching content found" in result


def test_search_help_center_no_results(monkeypatch):
    class FakeResult:
        data = []

    class FakeRPC:
        def execute(self):
            return FakeResult()

    class FakeSupabase:
        def rpc(self, name, params):
            return FakeRPC()

    monkeypatch.setattr(tools, "_embed", lambda text: [0.0] * 1536)
    monkeypatch.setattr(tools, "get_supabase", lambda: FakeSupabase())

    result = tools.search_help_center.invoke({"query": "nonexistent topic"})
    assert "No matching content" in result


def test_get_pricing_labels_as_illustrative(monkeypatch):
    class FakeQuery:
        def select(self, *a, **k):
            return self

        def ilike(self, *a, **k):
            return self

        def eq(self, *a, **k):
            return self

        def execute(self):
            class R:
                data = [
                    {
                        "product_name": "Roadside Assistance Basic",
                        "category": "emergency-roadside-assistance",
                        "price_description": "From $99/year (illustrative)",
                    }
                ]

            return R()

    class FakeTable:
        def select(self, *a, **k):
            return FakeQuery()

    class FakeSupabase:
        def table(self, name):
            return FakeTable()

    monkeypatch.setattr(tools, "get_supabase", lambda: FakeSupabase())

    result = tools.get_pricing.invoke({"product_query": "roadside"})
    assert "illustrative demo data" in result
    assert "Roadside Assistance Basic" in result


def test_get_pricing_no_results(monkeypatch):
    class FakeQuery:
        def select(self, *a, **k):
            return self

        def ilike(self, *a, **k):
            return self

        def eq(self, *a, **k):
            return self

        def execute(self):
            class R:
                data = []

            return R()

    class FakeTable:
        def select(self, *a, **k):
            return FakeQuery()

    class FakeSupabase:
        def table(self, name):
            return FakeTable()

    monkeypatch.setattr(tools, "get_supabase", lambda: FakeSupabase())

    result = tools.get_pricing.invoke({"product_query": "nonexistent product"})
    assert "No demo pricing data found" in result

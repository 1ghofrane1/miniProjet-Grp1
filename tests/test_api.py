import os
import tempfile
import unittest
from fastapi.testclient import TestClient
from app.main import app

SAMPLE = dict(nom_etudiant="Etudiant Demo", entreprise="Cloud Demo",
              intitule="API et Cloud", date_debut="2026-02-01", date_fin="2026-06-30")


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.previous = os.environ.get("DATABASE_PATH")
        os.environ["DATABASE_PATH"] = self.directory.name + "/test.db"
        self.client = TestClient(app).__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        if self.previous is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = self.previous
        self.directory.cleanup()

    def test_crud(self):
        self.assertEqual(self.client.get("/stages").json(), [])
        response = self.client.post("/stages", json=SAMPLE)
        self.assertEqual(response.status_code, 201)
        url = response.headers["location"]
        self.assertEqual(self.client.get(url).json()["nom_etudiant"], SAMPLE["nom_etudiant"])
        self.assertEqual(len(self.client.get("/stages").json()), 1)
        updated = {**SAMPLE, "entreprise": "Entreprise Demo 2"}
        self.assertEqual(self.client.put(url, json=updated).json()["entreprise"], updated["entreprise"])
        deleted = self.client.delete(url)
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(deleted.content, b"")
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_missing(self):
        for method, kwargs in [("get", {}), ("put", {"json": SAMPLE}), ("delete", {})]:
            self.assertEqual(getattr(self.client, method)("/stages/999", **kwargs).status_code, 404)

    def test_validation(self):
        for invalid in [{}, {**SAMPLE, "nom_etudiant": "   "},
                        {**SAMPLE, "date_fin": "2025-01-01"},
                        {**SAMPLE, "date_debut": "2026-02-30"},
                        {**SAMPLE, "date_debut": 123}, {**SAMPLE, "inconnu": 1}]:
            self.assertEqual(self.client.post("/stages", json=invalid).status_code, 422)
        self.assertEqual(self.client.get("/stages?limit=0").status_code, 422)
        self.assertEqual(self.client.get("/stages?offset=-1").status_code, 422)

    def test_persistence(self):
        created = self.client.post("/stages", json=SAMPLE).json()
        with TestClient(app) as second:
            self.assertEqual(second.get(f'/stages/{created["id"]}').json(), created)

    def test_docs_and_health(self):
        self.assertEqual(self.client.get("/health").json()["status"], "ok")
        self.assertEqual(self.client.get("/docs").status_code, 200)
        self.assertIn("/stages", self.client.get("/openapi.json").json()["paths"])

    def test_sql_text_and_pagination(self):
        payload = {**SAMPLE, "entreprise": "Demo'); DROP TABLE stages; --"}
        self.assertEqual(self.client.post("/stages", json=payload).status_code, 201)
        self.assertEqual(self.client.get("/stages").json()[0]["entreprise"], payload["entreprise"])
        self.assertEqual(self.client.get("/stages?offset=1&limit=1").json(), [])


if __name__ == "__main__":
    unittest.main()

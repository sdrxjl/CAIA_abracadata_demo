from __future__ import annotations

import csv
import io
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "patients.json"
HTML_FILE = ROOT / "caia_navigator_file_app.html"
CSV_TEMPLATE_HEADERS = [
    "id",
    "name",
    "age",
    "gender",
    "language",
    "payer",
    "cancerType",
    "stage",
    "daysSinceFinding",
    "primaryBarrier",
    "secondaryBarrier",
    "priority",
    "socialRisk",
    "missedVisits",
    "insuranceDelayDays",
    "referralComplete",
    "transportationRisk",
    "languageBarrier",
    "notes",
]


def default_patients() -> list[dict]:
    if DATA_FILE.exists():
        return read_patients()
    return [
        {
            "id": "PT-1001",
            "name": "Maria Alvarez",
            "age": 67,
            "gender": "Female",
            "language": "Spanish",
            "payer": "Medicaid",
            "cancerType": "Lung",
            "stage": "Referral Ordered",
            "daysSinceFinding": 78,
            "primaryBarrier": "Language / Communication",
            "secondaryBarrier": "Transportation Access",
            "priority": "Critical",
            "socialRisk": 5,
            "missedVisits": 2,
            "insuranceDelayDays": 0,
            "referralComplete": False,
            "transportationRisk": True,
            "languageBarrier": True,
            "notes": "Needs bilingual navigator and same-day referral escalation.",
        }
    ]


def read_patients() -> list[dict]:
    if not DATA_FILE.exists():
        patients = default_patients()
        write_patients(patients)
        return patients
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return [normalize_record(item) for item in data]


def write_patients(patients: list[dict]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as handle:
        json.dump(patients, handle, indent=2)


def normalize_bool(value) -> bool:
    return str(value).strip().lower() == "true" if not isinstance(value, bool) else value


def normalize_int(value, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def normalize_record(record: dict) -> dict:
    return {
        "id": str(record.get("id", "")).strip(),
        "name": str(record.get("name", "")).strip(),
        "age": normalize_int(record.get("age"), 0),
        "gender": str(record.get("gender", "Female")).strip() or "Female",
        "language": str(record.get("language", "English")).strip() or "English",
        "payer": str(record.get("payer", "Unknown")).strip() or "Unknown",
        "cancerType": str(record.get("cancerType", "Unknown")).strip() or "Unknown",
        "stage": str(record.get("stage", "Abnormal Finding")).strip() or "Abnormal Finding",
        "daysSinceFinding": normalize_int(record.get("daysSinceFinding"), 0),
        "primaryBarrier": str(record.get("primaryBarrier", "Scheduling Friction")).strip() or "Scheduling Friction",
        "secondaryBarrier": str(record.get("secondaryBarrier", "")).strip(),
        "priority": str(record.get("priority", "Routine")).strip() or "Routine",
        "socialRisk": normalize_int(record.get("socialRisk"), 0),
        "missedVisits": normalize_int(record.get("missedVisits"), 0),
        "insuranceDelayDays": normalize_int(record.get("insuranceDelayDays"), 0),
        "referralComplete": normalize_bool(record.get("referralComplete", False)),
        "transportationRisk": normalize_bool(record.get("transportationRisk", False)),
        "languageBarrier": normalize_bool(record.get("languageBarrier", False)),
        "notes": str(record.get("notes", "")).strip(),
    }


def same_patient_record(left: dict, right: dict) -> bool:
    return normalize_record(left) == normalize_record(right)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            self.serve_file(HTML_FILE, "text/html; charset=utf-8")
        elif path == "/api/patients":
            self.send_json(read_patients())
        elif path == "/api/template.csv":
            self.send_csv_template()
        elif path.endswith(".pdf"):
            target = ROOT / Path(path.lstrip("/")).name
            if target.exists():
                self.serve_file(target, "application/pdf")
            else:
                self.send_error(404, "File not found")
        else:
            self.send_error(404, "Not found")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/patients":
            payload = self.read_json()
            patients = [normalize_record(item) for item in payload.get("patients", []) if item.get("id")]
            write_patients(patients)
            self.send_json({"ok": True, "count": len(patients)})
        elif path == "/api/import-csv-preview":
            body = self.read_json()
            result = self.preview_import_csv(body.get("csv", ""))
            self.send_json(result)
        elif path == "/api/import-csv":
            body = self.read_json()
            result = self.import_csv(body.get("csv", ""), body.get("resolutions", {}))
            self.send_json(result)
        else:
            self.send_error(404, "Not found")

    def serve_file(self, path: Path, content_type: str) -> None:
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload: dict | list) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_csv_template(self) -> None:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=CSV_TEMPLATE_HEADERS)
        writer.writeheader()
        for row in read_patients()[:3]:
            writer.writerow(row)
        data = output.getvalue().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("Content-Disposition", 'attachment; filename="caia_navigator_template.csv"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def parse_import_rows(self, csv_text: str) -> tuple[list[dict], list[str]] | tuple[None, str]:
        rows = list(csv.DictReader(io.StringIO(csv_text)))
        if not rows:
            return None, "CSV must include a header row and at least one data row."
        missing = [header for header in ["id", "name", "age", "cancerType", "stage", "daysSinceFinding", "primaryBarrier"] if header not in rows[0]]
        if missing:
            return None, f"Missing required columns: {', '.join(missing)}"
        parsed = [normalize_record(row) for row in rows if normalize_record(row).get("id")]
        return parsed, []

    def next_patient_id(self, existing_ids: set[str]) -> str:
        max_num = 1000
        for patient_id in existing_ids:
            if patient_id.startswith("PT-") and patient_id[3:].isdigit():
                max_num = max(max_num, int(patient_id[3:]))
        return f"PT-{max_num + 1:04d}"

    def preview_import_csv(self, csv_text: str) -> dict:
        parsed_rows, error = self.parse_import_rows(csv_text)
        if parsed_rows is None:
            return {"ok": False, "message": error}
        current = {patient["id"]: patient for patient in read_patients()}
        conflicts = []
        skipped_duplicates = 0
        importable = 0
        for record in parsed_rows:
            existing = current.get(record["id"])
            if existing and same_patient_record(existing, record):
                skipped_duplicates += 1
                continue
            if existing:
                conflicts.append(
                    {
                        "id": record["id"],
                        "existing": existing,
                        "incoming": record,
                        "suggestedNewId": self.next_patient_id(set(current) | {item["id"] for item in parsed_rows}),
                    }
                )
                continue
            importable += 1
        return {
            "ok": True,
            "importableCount": importable,
            "skippedDuplicates": skipped_duplicates,
            "conflictCount": len(conflicts),
            "conflicts": conflicts,
        }

    def import_csv(self, csv_text: str, resolutions: dict | None = None) -> dict:
        parsed_rows, error = self.parse_import_rows(csv_text)
        if parsed_rows is None:
            return {"ok": False, "message": error}
        current = {patient["id"]: patient for patient in read_patients()}
        resolutions = resolutions or {}
        imported = []
        skipped_duplicates = 0
        skipped_conflicts = 0
        generated_ids = []
        for record in parsed_rows:
            existing = current.get(record["id"])
            if existing and same_patient_record(existing, record):
                skipped_duplicates += 1
                continue
            if existing:
                resolution = resolutions.get(record["id"], {})
                action = resolution.get("action", "skip")
                if action == "overwrite":
                    current[record["id"]] = record
                    imported.append(record)
                    continue
                if action == "generate_new":
                    new_id = str(resolution.get("newId", "")).strip()
                    if not new_id:
                        new_id = self.next_patient_id(set(current))
                    while new_id in current:
                        new_id = self.next_patient_id(set(current))
                    updated = normalize_record({**record, "id": new_id})
                    current[new_id] = updated
                    imported.append(updated)
                    generated_ids.append({"from": record["id"], "to": new_id})
                    continue
                skipped_conflicts += 1
                continue
            current[record["id"]] = record
            imported.append(record)
        write_patients(list(current.values()))
        return {
            "ok": True,
            "count": len(imported),
            "skippedDuplicates": skipped_duplicates,
            "skippedConflicts": skipped_conflicts,
            "generatedIds": generated_ids,
            "patients": list(current.values()),
        }

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))


def main() -> None:
    read_patients()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("CAIA Navigator server running at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()

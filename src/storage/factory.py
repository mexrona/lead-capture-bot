from src.config.settings import Settings
from src.storage.google_sheets.repository import GoogleSheetsRepository
from src.storage.interfaces.lead_repository import ILeadRepository


def create_lead_repository(settings: Settings) -> ILeadRepository:
    if settings.lead_storage_backend == "google_sheets":
        return GoogleSheetsRepository(
            credentials_path=settings.google_sheets_credentials_path,
            spreadsheet_id=settings.google_sheets_spreadsheet_id,
            worksheet_name=settings.google_sheets_worksheet_name,
        )
    raise ValueError(f"Unsupported lead storage backend: {settings.lead_storage_backend}")

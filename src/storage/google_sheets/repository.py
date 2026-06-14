import asyncio
import logging
from functools import partial
from uuid import uuid4

import gspread
from google.oauth2.service_account import Credentials

from src.config.constants import SHEETS_COLUMNS
from src.domain.entities.lead import Lead
from src.domain.enums.lead_status import LeadStatus
from src.domain.dto.lead_storage_row_dto import LeadStorageRowDTO
from src.storage.interfaces.lead_repository import ILeadRepository

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class GoogleSheetsRepository(ILeadRepository):
    """Google Sheets implementation of lead storage."""

    def __init__(
        self,
        credentials_path: str,
        spreadsheet_id: str,
        worksheet_name: str,
    ) -> None:
        self._credentials_path = credentials_path
        self._spreadsheet_id = spreadsheet_id
        self._worksheet_name = worksheet_name
        self._worksheet: gspread.Worksheet | None = None

    def _get_worksheet(self) -> gspread.Worksheet:
        if self._worksheet is not None:
            return self._worksheet

        credentials = Credentials.from_service_account_file(
            self._credentials_path,
            scopes=SCOPES,
        )
        client = gspread.authorize(credentials)
        spreadsheet = client.open_by_key(self._spreadsheet_id)
        try:
            worksheet = spreadsheet.worksheet(self._worksheet_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=self._worksheet_name,
                rows=1000,
                cols=len(SHEETS_COLUMNS),
            )
            worksheet.append_row(SHEETS_COLUMNS)

        self._ensure_headers(worksheet)
        self._worksheet = worksheet
        return worksheet

    def _ensure_headers(self, worksheet: gspread.Worksheet) -> None:
        first_row = worksheet.row_values(1)
        if not first_row:
            worksheet.append_row(SHEETS_COLUMNS)
        elif first_row != SHEETS_COLUMNS:
            logger.warning(
                "Worksheet headers differ from expected schema: %s",
                first_row,
            )

    async def save(self, lead: Lead) -> Lead:
        row_dto = LeadStorageRowDTO.from_lead(lead)
        row = row_dto.to_row(SHEETS_COLUMNS)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            partial(self._append_row_sync, row),
        )
        return lead

    def _append_row_sync(self, row: list[str]) -> None:
        worksheet = self._get_worksheet()
        worksheet.append_row(row, value_input_option="USER_ENTERED")

    async def update_status(self, lead_id: UUID, status: LeadStatus) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            partial(self._update_status_sync, str(lead_id), status.value),
        )

    def _update_status_sync(self, lead_id: str, status: str) -> None:
        worksheet = self._get_worksheet()
        id_column = SHEETS_COLUMNS.index("id") + 1
        status_column = SHEETS_COLUMNS.index("status") + 1
        cell = worksheet.find(lead_id, in_column=id_column)
        if cell is None:
            logger.warning("Lead %s not found in Google Sheets for status update", lead_id)
            return
        worksheet.update_cell(cell.row, status_column, status)

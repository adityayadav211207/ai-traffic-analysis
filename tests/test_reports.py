from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

from services.export_excel import generate_excel_report


def test_generate_excel_report_contains_executive_tabs(tmp_path):
    df = pd.DataFrame(
        [
            {
                "road": "Main Street",
                "city": "Downtown",
                "severity": "fatal",
                "injuries": 3,
                "vehicle": "car",
                "weather": "rain",
            },
            {
                "road": "Main Street",
                "city": "Downtown",
                "severity": "serious",
                "injuries": 1,
                "vehicle": "truck",
                "weather": "clear",
            },
            {
                "road": "Hill View",
                "city": "North",
                "severity": "minor",
                "injuries": 0,
                "vehicle": "motorcycle",
                "weather": "fog",
            },
        ]
    )

    output_path = tmp_path / "executive_report.xlsx"
    generate_excel_report(df, output_path=str(output_path))

    workbook = load_workbook(output_path)
    sheet_names = {sheet.title for sheet in workbook.worksheets}

    assert "Executive Summary" in sheet_names
    assert "Risk Corridor Rankings" in sheet_names
    assert "Operational Recommendations" in sheet_names
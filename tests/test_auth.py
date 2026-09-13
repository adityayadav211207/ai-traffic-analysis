from pathlib import Path


def test_dashboard_sidebar_requests_admin_navigation_and_login_icon_visibility():
    dashboard_sidebar = Path("templates/dashboard.html").read_text(encoding="utf-8")

    assert "Manage Users" in dashboard_sidebar
    assert "fa-right-from-bracket" in dashboard_sidebar
    assert "DATA & MANAGEMENT" in dashboard_sidebar

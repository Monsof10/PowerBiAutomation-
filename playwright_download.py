import time
import logging
from playwright.sync_api import sync_playwright
from playwright_auth import perform_login
from playwright_filters import reset_filters, set_dates, select_eff, select_facilities
from playwright_export import check_activations_and_export

def download_with_playwright(login_url, username, password, download_button_selector,
                             start_date_selector, end_date_selector, start_calendar_button,
                             end_calendar_button, start_date, end_date, headless,
                             output_path, ending_facilities, reset_all_selector, browser, group_num):
    """
    Main function to download PDF using Playwright.
    """
    page = browser.new_page()
    try:
        # Navigate to login page
        page.goto(login_url, timeout=60000)
        logging.info("Navigated to login page")

        # Perform login
        perform_login(page, username, password)

        # Reset filters if selector provided
        reset_filters(page, reset_all_selector)

        # Set dates
        set_dates(page, start_date_selector, end_date_selector, start_date, end_date)

        # Select EFF and handle special case for group 6
        blank_selected = select_eff(page, group_num)

        # Select facilities
        select_facilities(page, ending_facilities, blank_selected)

        # Check activations and export PDF
        has_activations, activation_count = check_activations_and_export(page, output_path, blank_selected)

        return output_path, has_activations, activation_count

    except Exception as e:
        logging.error(f"Error in download_with_playwright: {e}")
        raise
    finally:
        page.close()

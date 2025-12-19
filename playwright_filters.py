import time
import logging
from datetime import datetime, timedelta

def reset_filters(page, reset_all_selector):
    """
    Reset all filters before setting dates if selector provided.
    """
    if reset_all_selector:
        try:
            logging.info("Waiting for reset button to be available...")
            page.wait_for_selector(reset_all_selector, timeout=30000)  # Wait up to 30 seconds for reset button
            logging.info("Resetting all filters before setting dates...")
            page.click(reset_all_selector, timeout=10000)  # Increased timeout to 10 seconds
            time.sleep(3)  # Increased wait for dialog to open
            # Confirm reset in dialog
            page.click("button[data-testid='dailog-ok-btn']", timeout=10000)  # Increased timeout
            time.sleep(5)  # Increased wait for reset to complete
            logging.info("All filters reset")
        except Exception as e:
            logging.warning(f"Failed to reset all filters before dates: {e}")

def set_dates(page, start_date_selector, end_date_selector, start_date, end_date):
    """
    Set start and end dates on the page.
    """
    # Compute date for 1 months ago, first day of that month
    today = datetime.now()
    target_month = today.month - 1
    target_year = today.year
    if target_month <= 0:
        target_month += 12
        target_year -= 1
    start_date_calc = datetime(target_year, target_month, 1).date()
    date_str = start_date_calc.strftime('%m/%d/%Y')  # MM/DD/YYYY format
    logging.info(f"Setting start date to: {date_str}")

    # Compute end date (last day of the previous month)
    if target_month == 12:
        next_year = target_year + 1
        next_month = 1
    else:
        next_year = target_year
        next_month = target_month + 1

    last_day_of_month = (datetime(next_year, next_month, 1) - timedelta(days=1)).day

    # For February, force 28th day as specified
    if target_month == 2:
        last_day_of_month = 28

    end_date_calc = datetime(target_year, target_month, last_day_of_month).date()
    end_date_str = end_date_calc.strftime('%m/%d/%Y')  # MM/DD/YYYY format
    logging.info(f"Setting end date to: {end_date_str}")

    # Fill the start date input (delete existing and set new)
    if start_date_selector:
        try:
            page.wait_for_selector(start_date_selector, timeout=30000)  # Increased timeout
            # Clear existing value by selecting all and deleting
            page.click(start_date_selector, timeout=5000)
            page.keyboard.press('Control+a')  # Select all
            page.keyboard.press('Delete')  # Delete
            time.sleep(0.5)
            # Fill new value
            page.fill(start_date_selector, date_str, timeout=5000)
            logging.info(f"Set start date input {start_date_selector} to {date_str}")
            time.sleep(3)  # Increased wait time for date selection
        except Exception as e:
            logging.warning(f"Failed to set start date: {e}")
            # Try alternative selector if the first one fails
            try:
                alt_selector = "input[aria-description=\"Enter date in M/d/yyyy format\"]"
                page.wait_for_selector(alt_selector, timeout=5000)
                page.click(alt_selector, timeout=5000)
                page.keyboard.press('Control+a')
                page.keyboard.press('Delete')
                time.sleep(0.5)
                page.fill(alt_selector, date_str, timeout=5000)
                logging.info(f"Set start date input {alt_selector} to {date_str} (alternative)")
                time.sleep(3)  # Increased wait time for date selection
            except Exception as e2:
                logging.warning(f"Failed to set start date with alternative selector: {e2}")

    # Fill the end date input (delete existing and set new)
    if end_date_selector:
        try:
            page.wait_for_selector(end_date_selector, timeout=30000)  # Increased timeout
            # Clear existing value by selecting all and deleting
            page.click(end_date_selector, timeout=5000)
            page.keyboard.press('Control+a')  # Select all
            page.keyboard.press('Delete')  # Delete
            time.sleep(0.5)
            # Fill new value
            page.fill(end_date_selector, end_date_str, timeout=5000)
            logging.info(f"Set end date input {end_date_selector} to {end_date_str}")
            time.sleep(3)  # Increased wait time for date selection
        except Exception as e:
            logging.warning(f"Failed to set end date: {e}")
            # Try alternative selector if the first one fails
            try:
                alt_end_selector = "input[aria-description=\"Enter date in M/d/yyyy format\"]"
                page.wait_for_selector(alt_end_selector, timeout=5000)
                page.click(alt_end_selector, timeout=5000)
                page.keyboard.press('Control+a')
                page.keyboard.press('Delete')
                time.sleep(0.5)
                page.fill(alt_end_selector, end_date_str, timeout=5000)
                page.keyboard.press('Enter')  # Press Enter to confirm the date
                logging.info(f"Set end date input {alt_end_selector} to {end_date_str} (alternative)")
                time.sleep(3)
            except Exception as e2:
                logging.warning(f"Failed to set end date with alternative selector: {e2}")

def select_eff(page, group_num):
    """
    Select EFF and handle special case for group 6.
    Returns blank_selected (True if '(Blank)' was selected).
    """
    blank_selected = False
    try:
        logging.info("Clicking EFF (prefer index 58)...")
        CLICKABLE_SELECTOR_EFF = (
            "button, a[href], [role=\"button\"], [onclick], [tabindex],"
            " input[type=\"button\"], input[type=\"submit\"], *[ng-click], *[data-click],"
            " *[class*=\"button\"], *[class*=\"btn\"], *[class*=\"click\"], [aria-hidden=\"false\"][tabindex],"
            " tri-button, mat-button, [role=\"link\"], [role=\"menuitem\"], [aria-pressed]"
        )
        try:
            els_eff = page.query_selector_all(CLICKABLE_SELECTOR_EFF)
        except Exception:
            els_eff = []

        if len(els_eff) > 58:
            try:
                els_eff[58].scroll_into_view_if_needed()
                els_eff[58].click(force=True)
                logging.info("Clicked EFF via index 58")
            except Exception as e_idx58:
                logging.warning(f"Index 58 click failed: {e_idx58} — falling back to text click")
                try:
                    page.locator('.mat-mdc-list-item').get_by_text('EFF').first.click(timeout=10000)
                    logging.info("Clicked 'EFF' button (fallback by text)")
                except Exception as e_text:
                    logging.warning(f"Fallback EFF click failed: {e_text}")
        else:
            try:
                page.locator('.mat-mdc-list-item').get_by_text('EFF').first.click(timeout=10000)
                logging.info("Clicked 'EFF' button (text)")
            except Exception as e_text2:
                logging.warning(f"Failed to click 'EFF' button: {e_text2}")

        time.sleep(2)

        # Special case for group 6: click '(Blank)' button after EFF click
        if group_num == 6:
            try:
                logging.info("Group 6: Clicking '(Blank)' button after EFF click")
                # Try clicking button, span, or div with text "(Blank)"
                clicked = False
                selectors = [
                    'button:has-text("(Blank)")',
                    'span:has-text("(Blank)")',
                    'div:has-text("(Blank)")'
                ]
                for selector in selectors:
                    try:
                        locator = page.locator(selector).first
                        if locator.is_visible():
                            locator.click(timeout=10000)
                            logging.info(f"Clicked '(Blank)' button with selector: {selector}")
                            clicked = True
                            blank_selected = True
                            break
                    except Exception as e:
                        logging.warning(f"Failed to click '(Blank)' button with selector {selector}: {e}")
                if not clicked:
                    logging.warning("Could not find or click any '(Blank)' button elements - checking for presence of '(Blank)' text")
                    # Even if we couldn't click, check presence of any element containing the text "(Blank)" and treat as blank selected
                    try:
                        # Use a broad text search; if any element contains the text, treat as blank selected
                        if page.locator('text="(Blank)"').count() > 0:
                            logging.info("Found '(Blank)' text on page - treating as if '(Blank)' was selected")
                            blank_selected = True
                            clicked = True
                        else:
                            blank_selected = False
                    except Exception as te:
                        logging.debug(f"Error checking for '(Blank)' text: {te}")
                        blank_selected = False
                else:
                    # If clicked '(Blank)', also treat as no facilities selected
                    blank_selected = True
                time.sleep(3)  # Wait for action to complete
            except Exception as be:
                logging.warning(f"Failed to click '(Blank)' button: {be} - treating as no facilities selected")
                blank_selected = False

    except Exception as e:
        logging.warning(f"Failed to click 'EFF' button: {e}")

    return blank_selected

def select_facilities(page, ending_facilities, blank_selected):
    """
    Select ending facilities in Ending Facility Filter and Facility Filter.
    """
    if ending_facilities:
        facilities_list = [f.strip() for f in ending_facilities.split(',') if f.strip()]
        logging.info(f"Selecting {len(facilities_list)} ending facilities in Ending Facility Filter: {facilities_list}")
        for facility in facilities_list:
            try:
                logging.info(f"Looking for facility in Ending Facility Filter: {facility}")
                facility_selectors = [
                    f'[title="{facility}"]',
                    f'div[title="{facility}"]',
                    f'span[title="{facility}"]',
                    f'tr:has-text("{facility}") input[type="checkbox"]',
                    f'tr:has-text("{facility}") .mat-checkbox',
                    f'.facility-row:has-text("{facility}") input[type="checkbox"]',
                    f'div:has-text("{facility}") input[type="checkbox"]',
                    f'label:has-text("{facility}")',
                    f'text={facility}',
                    f'span:has-text("{facility}")'
                ]
                clicked = False
                for selector in facility_selectors:
                    try:
                        locator = page.locator(selector).first
                        if locator.is_visible():
                            bounding_box = locator.bounding_box()
                            logging.info(f"Found visible locator for {facility}: {selector}, position: {bounding_box}")
                            locator.click(timeout=5000)
                            logging.info(f"Selected facility: {facility} using selector: {selector}")
                            clicked = True
                            time.sleep(1)
                            break
                        else:
                            logging.debug(f"Selector {selector} not visible for {facility}")
                    except Exception as e:
                        logging.debug(f"Selector {selector} failed for {facility}: {e}")
                        continue

                if not clicked:
                    logging.warning(f"Could not select facility: {facility} - check debug logs and screenshot")
            except Exception as e:
                logging.warning(f"Error selecting facility {facility}: {e}")
        time.sleep(7)  # Increased wait time after facility selection before clicking Overview
    # After selecting facilities in Facility Filter, click Overview (best-effort)
    try:
        ov = page.get_by_text('Overview')
        if ov.count() > 0:
            ov.first.click(timeout=5000)
            logging.info("Clicked 'Overview' after selecting facilities")
            time.sleep(5)  # Increased wait time after Overview before proceeding to Facility Filter
    except Exception:
        logging.debug("Overview not found or click failed after selecting facilities")

    # If we selected '(Blank)' in the EFF step for group 6, skip the Facility Filter entirely
    if not blank_selected:
        try:
            logging.info("Clicking Facility Filter (prefer index 56)...")
            CLICKABLE_SELECTOR_FAC = (
                "button, a[href], [role=\"button\"], [onclick], [tabindex],"
                " input[type=\"button\"], input[type=\"submit\"], *[ng-click], *[data-click],"
                " *[class*=\"button\"], *[class*=\"btn\"], *[class*=\"click\"], [aria-hidden=\"false\"][tabindex],"
                " tri-button, mat-button, [role=\"link\"], [role=\"menuitem\"], [aria-pressed]"
            )
            try:
                els_fac = page.query_selector_all(CLICKABLE_SELECTOR_FAC)
            except Exception:
                els_fac = []

            if len(els_fac) > 56:
                try:
                    els_fac[56].scroll_into_view_if_needed()
                    els_fac[56].click(force=True)
                    logging.info("Clicked Facility Filter via index 56")
                    time.sleep(8)  # Increased wait time for facility list to appear
                except Exception as e_idx56:
                    logging.warning(f"Index 56 click failed: {e_idx56} — falling back to text click")
                    try:
                        page.locator('.mat-mdc-list-item').get_by_text('Facility Filter').first.click(timeout=10000)
                        logging.info("Clicked 'Facility Filter' list item (fallback)")
                        time.sleep(8)  # Increased wait time for facility list to appear
                    except Exception as e_text:
                        logging.warning(f"Fallback Facility Filter click failed: {e_text}")
            else:
                try:
                    page.locator('.mat-mdc-list-item').get_by_text('Facility Filter').first.click(timeout=10000)
                    logging.info("Clicked 'Facility Filter' list item (text)")
                    time.sleep(8)  # Increased wait time for facility list to appear
                except Exception as e_text2:
                    logging.warning(f"Failed to click 'Facility Filter' list item: {e_text2}")
        except Exception as e:
            logging.warning(f"Facility Filter click sequence failed: {e}")

        if ending_facilities:
            facilities_list = [f.strip() for f in ending_facilities.split(',') if f.strip()]
            logging.info(f"Selecting {len(facilities_list)} ending facilities in Facility Filter: {facilities_list}")
            for facility in facilities_list:
                try:
                    logging.info(f"Looking for facility in Facility Filter: {facility}")
                    facility_selectors = [
                        f'[title="{facility}"]',
                        f'div[title="{facility}"]',
                        f'span[title="{facility}"]',
                        f'tr:has-text("{facility}") input[type="checkbox"]',
                        f'tr:has-text("{facility}") .mat-checkbox',
                        f'.facility-row:has-text("{facility}") input[type="checkbox"]',
                        f'div:has-text("{facility}") input[type="checkbox"]',
                        f'label:has-text("{facility}")',
                        f'text={facility}',
                        f'span:has-text("{facility}")'
                    ]
                    clicked = False
                    for selector in facility_selectors:
                        try:
                            locators = page.locator(selector).all()
                            for loc in locators:
                                if loc.is_visible():
                                    loc.scroll_into_view_if_needed()
                                    time.sleep(0.5)
                                    bounding_box = loc.bounding_box()
                                    logging.info(f"Found visible locator for {facility}: {selector}, position: {bounding_box}")
                                    loc.click(timeout=5000)
                                    logging.info(f"Selected facility: {facility} using selector: {selector}")
                                    clicked = True
                                    time.sleep(1)
                                    break
                            if clicked:
                                break
                        except Exception as e:
                            logging.debug(f"Selector {selector} failed for {facility}: {e}")
                            continue

                    if not clicked:
                        logging.warning(f"Could not select facility: {facility} - check debug logs and screenshot")
                    else:
                        logging.info(f"Successfully selected facility: {facility}")
                except Exception as e:
                    logging.warning(f"Error selecting facility {facility}: {e}")
        time.sleep(3)

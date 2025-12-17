# playwright_download.py
from playwright.sync_api import sync_playwright
import time
import os
import logging

def download_with_playwright(login_url: str, username: str, password: str,
                             download_button_selector: str, output_path: str,
                             headless=True, start_date_selector: str = None, end_date_selector: str = None,
                             start_calendar_button: str = None, end_calendar_button: str = None,
                             start_date=None, end_date=None, ending_facilities: str = "", reset_all_selector: str = None, browser=None, group_num: int = None):
    """
    Downloads PDF and returns (output_path, has_activations, activation_count)
    has_activations: True if numeric values found, False otherwise
    activation_count: The total count found, or 0 if none
    """
    if browser is None:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
    else:
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto(login_url, wait_until="networkidle")
        # ======= CUSTOMIZE THESE SELECTORS =========
        # Microsoft login steps (adjust if needed)
        try:
            logging.info(f"Using username: {username}")
            # Wait for email field (try multiple selectors)
            email_selectors = ["#i0116", "input[name='loginfmt']", "input[type='email']", "input[placeholder*='email']"]
            for selector in email_selectors:
                try:
                    page.wait_for_selector(selector, timeout=3000)
                    page.fill(selector, username)
                    break
                except:
                    continue
            else:
                raise Exception("Email field not found")

            time.sleep(2)  # wait after filling email
            logging.info("Page title after email: %s", page.title())

            # Check if Submit button is present and click (using the provided selector: button#submitBtn)
            logging.info("Checking for Submit button...")
            submit_button = page.query_selector("button#submitBtn")
            if submit_button:
                disabled_attr = submit_button.get_attribute("disabled")
                logging.info(f"Submit button found, disabled attribute: {disabled_attr}")
                if disabled_attr is None or disabled_attr == "false":
                    logging.info("Submit button is enabled, clicking...")
                    page.click("button#submitBtn", timeout=5000)
                else:
                    raise Exception("Submit button is disabled - check if email is valid for Power BI login.")
            else:
                # Fallback selectors for the button (including Next if Submit fails)
                submit_selectors = ["input[value='Next']", "#idSIButton9", "input[type='submit']", "button.primary"]
                clicked = False
                for selector in submit_selectors:
                    try:
                        button = page.query_selector(selector)
                        if button and button.get_attribute("disabled") in [None, "false"]:
                            page.click(selector, timeout=5000)
                            logging.info(f"Clicked using fallback selector: {selector}")
                            clicked = True
                            break
                    except:
                        continue
                if not clicked:
                    raise Exception("Submit/Next button not found or disabled - check if email is valid for Power BI login.")

            # Wait for page to load after submit (use 'load' state, increase timeout)
            logging.info("Waiting for page load after submit...")
            page.wait_for_load_state("load", timeout=30000)
            logging.info("Page title after submit: %s", page.title())

            # Wait for password field
            passwd_selectors = ["#i0118", "input[name='passwd']", "input[type='password']"]
            for selector in passwd_selectors:
                try:
                    page.wait_for_selector(selector, timeout=10000)
                    page.fill(selector, password)
                    break
                except:
                    continue
            else:
                raise Exception("Password field not found")

            # Click Sign in
            signin_selectors = ["#idSIButton9", "input[value='Sign in']", "input[type='submit']"]
            for selector in signin_selectors:
                try:
                    page.click(selector, timeout=5000)
                    break
                except:
                    continue
            else:
                raise Exception("Sign in button not found")

            # Wait for page to load after sign in
            logging.info("Waiting for page load after sign in...")
            page.wait_for_load_state("load", timeout=30000)
            logging.info("Page title after sign in: %s", page.title())

            # Handle "Stay signed in?" if it appears
            logging.info("Checking for 'Stay signed in?' prompt...")
            stay_signed_in_selectors = [
                "input[value='Yes']",
                "#idSIButton9[value='Yes']",
                "button:has-text('Yes')",
                "input[type='submit'][value*='Yes']"
            ]
            yes_clicked = False
            for selector in stay_signed_in_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    page.click(selector)
                    logging.info(f"Clicked 'Stay signed in? Yes' using selector: {selector}")
                    yes_clicked = True
                    break
                except:
                    continue
            if not yes_clicked:
                logging.info("No 'Stay signed in?' prompt found or handled.")
            time.sleep(2)  # Brief pause after handling prompt
        except Exception as e:
            logging.warning(f"Login steps failed: {e}")
        # ===========================================
    # Wait for dashboard to load
    logging.info("Waiting for dashboard to load...")
    page.wait_for_load_state("load", timeout=30000)
    time.sleep(5)

    # Reset all filters before setting dates if selector provided
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

 # Compute date for 1 months ago, first day of that month
        from datetime import datetime, timedelta
        today = datetime.now()
        target_month = today.month - 1
        target_year = today.year
        if target_month <= 0:
            target_month += 12
            target_year -= 1
        start_date = datetime(target_year, target_month, 1).date()
        date_str = start_date.strftime('%d/%m/%Y')  # MM/DD/YYYY format
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
        
        end_date = datetime(target_year, target_month, last_day_of_month).date()
        end_date_str = end_date.strftime('%d/%m/%Y')  # MM/DD/YYYY format
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

        # Click EFF button (use element index 58 when available)
        # Track whether we selected a '(Blank)' option after EFF (default False)
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

                # Overview click will be performed after opening Facility Filter and selecting facilities


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
                                    has_activations = False
                                    activation_count = 0
                            except Exception as te:
                                logging.debug(f"Error checking for '(Blank)' text: {te}")
                                has_activations = False
                                activation_count = 0
                        else:
                            # If clicked '(Blank)', also treat as no facilities selected
                            has_activations = False
                            activation_count = 0
                        time.sleep(3)  # Wait for action to complete
                    except Exception as be:
                        logging.warning(f"Failed to click '(Blank)' button: {be} - treating as no facilities selected")
                        has_activations = False
                        activation_count = 0

        except Exception as e:
            logging.warning(f"Failed to click 'EFF' button: {e}")

        # Select ending facilities from ENDING_FACILITIES in Ending Facility Filter
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
            time.sleep(2)
# After selecting facilities in Facility Filter, click Overview (best-effort)
            try:
                ov = page.get_by_text('Overview')
                if ov.count() > 0:
                    ov.first.click(timeout=5000)
                    logging.info("Clicked 'Overview' after selecting facilities")
                    time.sleep(1)
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
                        time.sleep(2)
                    except Exception as e_idx56:
                        logging.warning(f"Index 56 click failed: {e_idx56} — falling back to text click")
                        try:
                            page.locator('.mat-mdc-list-item').get_by_text('Facility Filter').first.click(timeout=10000)
                            logging.info("Clicked 'Facility Filter' list item (fallback)")
                            time.sleep(3)
                        except Exception as e_text:
                            logging.warning(f"Fallback Facility Filter click failed: {e_text}")
                else:
                    try:
                        page.locator('.mat-mdc-list-item').get_by_text('Facility Filter').first.click(timeout=10000)
                        logging.info("Clicked 'Facility Filter' list item (text)")
                        time.sleep(3)
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


        # If '(Blank)' was selected (blank_selected = True), skip Activations report and export
        # because blank means 0 activations, so send no-activations email
        if blank_selected:
            logging.info("'(Blank)' was selected in EFF — returning early with has_activations=False to send no-activations email")
            context.close()
            return output_path, False, 0

        # Click Activations report101 button before export
        try:
            logging.info("Looking for 'Activations report' button...")
            page.locator('button:has-text("Activations report")').first.click(timeout=10000)
            logging.info("Clicked 'Activations report' button")
            time.sleep(5)  # Wait for page to load after clicking Activations report101

            # Look for the "Total count of activations" column header and click it
            try:
                logging.info("Looking for 'Total count of activations' column header...")
                column_selectors = [
                    'button:has-text("Total count of activations")',
                    'div:has-text("Total count of activations")',
                    'span:has-text("Total count of activations")',
                    'th:has-text("Total count of activations")',
                    '[role="columnheader"]:has-text("Total count of activations")',
                    'text="Total count of activations"'
                ]

                column_clicked = False
                for selector in column_selectors:
                    try:
                        locator = page.locator(selector).first
                        if locator.is_visible():
                            locator.click(timeout=5000)
                            logging.info(f"Clicked 'Total count of activations' column using selector: {selector}")
                            column_clicked = True
                            time.sleep(3)  # Wait for column sort/filter to apply
                            break
                    except Exception as e:
                        logging.debug(f"Selector {selector} failed: {e}")
                        continue

                if not column_clicked:
                    logging.warning("Could not find or click 'Total count of activations' column header")
                else:
                    # After clicking the column, extract the final value from that column
                    try:
                        logging.info("Extracting the final value from 'Total count of activations' column...")

                        # Method 1: Look for table cells in the Total count of activations column
                        # Assuming it's the last cell or a specific position in the column
                        table_cells = page.locator('td, div[role="gridcell"]').all()
                        column_values = []

                        for cell in table_cells[:50]:  # Check first 50 cells
                            text = cell.inner_text().strip()
                            if text.isdigit() and len(text) > 0:
                                column_values.append(int(text))

                        if column_values:
                            # The final/last value in the column should be the total
                            final_value = column_values[-1]  # Last value in the list
                            logging.info(f"Total count of activations (final value): {final_value}")
                            has_activations = True
                            activation_count = final_value
                        else:
                            logging.warning("No numeric values found in table cells")
                            has_activations = False
                            activation_count = 0

                        # Method 2: Alternative - look for any prominent number that might be the total
                        if not column_values:
                            try:
                                # Look for elements that might contain the total (often styled differently)
                                total_elements = page.locator('div, span, p').all()
                                for elem in total_elements[:100]:
                                    text = elem.inner_text().strip()
                                    # Look for numbers that are likely totals (maybe styled with bold or different color)
                                    if text.isdigit() and len(text) <= 3:  # Assuming reasonable total count
                                        logging.info(f"Potential total count: {text}")
                                        has_activations = True
                                        activation_count = int(text)
                                        break
                            except Exception as e:
                                logging.debug(f"Method 2 failed: {e}")
                                has_activations = False
                                activation_count = 0

                    except Exception as e:
                        logging.warning(f"Failed to extract final value from column: {e}")

            except Exception as e:
                logging.warning(f"Failed to find 'Total count of activations' column: {e}")

        except Exception as e:
            logging.warning(f"Failed to click 'Activations report101' button: {e}")

        try:
            page.wait_for_selector('span[localize="Export"]', timeout=60000)  # Wait for Export button to appear
            logging.info("Dashboard loaded, clicking Export button...")
            page.click('span[localize="Export"]')  # Click the Export span/button
            time.sleep(1)  # Wait for menu to open
            logging.info("Export menu opened, clicking PDF option...")
            page.click('span[localize="Pdf"]')  # Click the PDF span/button
            time.sleep(2)  # Wait for dialog to open
            logging.info("PDF dialog opened, clicking final Export button...")
            time.sleep(5)  # Extra wait for dialog to fully load
            
            with page.expect_download(timeout=300000) as download_info:  # Increased timeout to 5 minutes
                page.click('button#okButton')  # Click the final Export button in the dialog
            download = download_info.value
            download.save_as(output_path)
            logging.info("PDF downloaded successfully to %s", output_path)
        except Exception as e:
            logging.error(f"Export button not found: {e}")
            raise Exception("Export button not found - check if dashboard loaded correctly. ")
    context.close()
    return output_path, has_activations, activation_count
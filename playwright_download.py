# playwright_download.py
from playwright.sync_api import sync_playwright
import time
import os
import logging

def download_with_playwright(login_url: str, username: str, password: str,
                             download_button_selector: str, output_path: str,
                             headless=True, start_date_selector: str = None, end_date_selector: str = None,
                             start_calendar_button: str = None, end_calendar_button: str = None,
                             start_date=None, end_date=None, ending_facilities: str = ""):
    """
    Opens the login page, fills credentials (adapt selectors), clicks download, saves file.
    NOTE: You must edit the login steps to match the dashboard (selectors).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
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
            page.screenshot(path="after_email.png")

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
                    raise Exception("Submit button is disabled - check if email is valid for Power BI login. Screenshot: after_email.png")
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
                    raise Exception("Submit/Next button not found or disabled - check if email is valid for Power BI login. Screenshot: after_email.png")

            # Wait for page to load after submit (use 'load' state, increase timeout)
            logging.info("Waiting for page load after submit...")
            page.wait_for_load_state("load", timeout=30000)
            logging.info("Page title after submit: %s", page.title())
            page.screenshot(path="after_submit.png")

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
            page.screenshot(path="after_signin.png")

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
        # Wait for dashboard to load (adjust selector if needed, e.g., a common element like the report title)
        logging.info("Waiting for dashboard to load...")
        page.wait_for_load_state("load", timeout=30000)  # Ensure page is fully loaded
        time.sleep(5)  # Reduced wait time for dynamic content to fully load
        try:
            page.screenshot(path="after_dashboard_load.png")  # Debug screenshot
        except Exception as e:
            logging.warning(f"Could not take dashboard screenshot: {e}")

        # Compute date for 2 months ago, first day of that month
        from datetime import datetime, timedelta
        today = datetime.now()
        target_month = today.month - 2
        target_year = today.year
        if target_month <= 0:
            target_month += 12
            target_year -= 1
        start_date = datetime(target_year, target_month, 1).date()
        date_str = start_date.strftime('%m/%d/%Y')  # MM/DD/YYYY format
        logging.info(f"Setting start date to: {date_str}")

        # Compute end date (25th of the previous month)
        end_date = datetime(target_year, target_month, 25).date()
        end_date_str = end_date.strftime('%d/%m/%Y')  # DD/MM/YYYY format
        logging.info(f"Setting end date to: {end_date_str}")

        # Fill the start date input (delete existing and set new)
        if start_date_selector:
            try:
                page.screenshot(path="before_date_setting.png")  # Screenshot before setting date
                page.wait_for_selector(start_date_selector, timeout=30000)  # Increased timeout
                # Clear existing value by selecting all and deleting
                page.click(start_date_selector, timeout=5000)
                page.keyboard.press('Control+a')  # Select all
                page.keyboard.press('Delete')  # Delete
                time.sleep(0.5)
                # Fill new value
                page.fill(start_date_selector, date_str, timeout=5000)
                logging.info(f"Set start date input {start_date_selector} to {date_str}")
                page.screenshot(path="after_date_setting.png")  # Screenshot after setting date
                time.sleep(1)
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
                    page.screenshot(path="after_date_setting_alt.png")
                    time.sleep(1)
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
                page.screenshot(path="after_end_date_setting.png")  # Screenshot after setting end date
                time.sleep(1)
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
                    page.screenshot(path="after_end_date_setting_alt.png")
                    time.sleep(1)
                except Exception as e2:
                    logging.warning(f"Failed to set end date with alternative selector: {e2}")

        # Click on the Ending Facility dropdown chevron to open it
        try:
            ending_chevron_selector = 'div.slicer-dropdown-menu[aria-label="EndingLocation"] i.dropdown-chevron'
            page.wait_for_selector(ending_chevron_selector, timeout=30000)
            page.click(ending_chevron_selector)
            logging.info("Clicked on the Ending Facility dropdown chevron")
            time.sleep(2)  # Wait for dropdown to open

            # Get the specific popup ID for EndingLocation
            try:
                popup_id = page.get_attribute('div.slicer-dropdown-menu[aria-label="EndingLocation"]', 'aria-controls')
                specific_popup_selector = f'#{popup_id}'
                specific_item_base = f'#{popup_id}'
            except Exception as id_e:
                logging.warning(f"Failed to get popup ID: {id_e}")
                specific_popup_selector = 'div.slicer-dropdown-popup'
                specific_item_base = 'div.slicer-dropdown-popup'

            # Force specific popup visibility if needed (set display to block via JS)
            try:
                page.evaluate(f'''() => {{
                    const popup = document.querySelector('{specific_popup_selector}');
                    if (popup) {{
                        popup.style.display = 'block';
                        popup.style.visibility = 'visible';
                        popup.style.position = 'absolute';
                        popup.style.zIndex = '9999';
                    }}
                }}''')
                logging.info(f"Forced specific popup visibility via JavaScript for {specific_popup_selector}")
            except Exception as force_e:
                logging.warning(f"Failed to force specific popup visibility: {force_e}")

            # Deselect all by clicking "Select All"
            try:
                select_all_locator = page.locator('div.slicerItemContainer:has-text("Select All")')
                select_all_locator.click(timeout=5000)
                logging.info("Deselected all facilities initially")
                time.sleep(1)
            except Exception as deselect_e:
                logging.warning(f"Failed to deselect all initially: {deselect_e}")

            # If ending_facilities is provided, select all facilities from the list
            if ending_facilities:
                facility_list = [f.strip() for f in ending_facilities.split(',') if f.strip()]
                for facility_name in facility_list:
                    try:
                        # Click the facility directly
                        locator = page.locator(f'div.slicerItemContainer:has-text("{facility_name}")')
                        locator.click(timeout=5000)  # Reduced timeout to 5 seconds
                        logging.info(f"Selected facility '{facility_name}'")
                        time.sleep(1)  # Wait for selection to apply
                    except Exception as select_e:
                        logging.warning(f"Selection failed for '{facility_name}': {select_e}")

        except Exception as e:
            logging.warning(f"Failed to select Ending Facility: {e}")

        # # Debug: List all buttons on the page before clicking activation
        # buttons = page.query_selector_all('button')
        # logging.info(f"Found {len(buttons)} buttons on the page:")
        # for i, btn in enumerate(buttons):
        #     text = btn.inner_text() or btn.get_attribute('aria-label') or btn.get_attribute('title') or "No text"
        #     btn_id = btn.get_attribute('id') or "No id"
        #     btn_class = btn.get_attribute('class') or "No class"
        #     logging.info(f"Button {i}: text='{text}', id='{btn_id}', class='{btn_class}'")

        # List of buttons to click
        buttons_to_click = [
            ("Activation Duration101", "after_activation_click.png"),
            ("Activations Report101", "after_activations_report_click.png"),
            ("Facility Overview101", "after_facility_overview_click.png"),
            ("Attempts Overview101", "after_attempts_overview_click.png")
        ]

        try:
            for button_text, screenshot_name in buttons_to_click:
                logging.info(f"Looking for '{button_text}' button...")
                button = page.locator(f'button:has-text("{button_text}")')
                button.click()
                logging.info(f"Clicked '{button_text}' button")
                time.sleep(3)  # Wait for new page/section to load
                page.screenshot(path=screenshot_name)  # Debug screenshot

                # Open facility dropdown
                try:
                    if button_text == "Attempts Overview101":
                        # Debug: List all slicer dropdown menus on the page
                        slicers = page.query_selector_all('div.slicer-dropdown-menu')
                        logging.info(f"Found {len(slicers)} slicer dropdown menus on the page after '{button_text}':")
                        for i, slicer in enumerate(slicers):
                            aria_label = slicer.get_attribute('aria-label') or "No aria-label"
                            slicer_id = slicer.get_attribute('id') or "No id"
                            slicer_class = slicer.get_attribute('class') or "No class"
                            logging.info(f"Slicer {i}: aria-label='{aria_label}', id='{slicer_id}', class='{slicer_class}'")

                        facility_chevron_selector = 'div.slicer-dropdown-menu[aria-label="FacilityName"] i.dropdown-chevron'
                        page.wait_for_selector(facility_chevron_selector, timeout=30000)
                        page.click(facility_chevron_selector)
                        logging.info(f"Opened Facility dropdown after '{button_text}'")

                        # Force popup visibility
                        try:
                            popup_id = page.get_attribute('div.slicer-dropdown-menu[aria-label="FacilityName"]', 'aria-controls')
                            specific_popup_selector = f'#{popup_id}'
                            page.evaluate(f'''() => {{
                                const popup = document.querySelector('{specific_popup_selector}');
                                if (popup) {{
                                    popup.style.display = 'block';
                                    popup.style.visibility = 'visible';
                                    popup.style.position = 'absolute';
                                    popup.style.zIndex = '9999';
                                }}
                            }}''')
                            logging.info(f"Forced popup visibility for Attempts Overview101: {specific_popup_selector}")
                        except Exception as force_e:
                            logging.warning(f"Failed to force popup for Attempts Overview101: {force_e}")

                        # Deselect all by clicking "Select All"
                        try:
                            select_all_locator = page.locator('div.slicerItemContainer:has-text("Select All")')
                            select_all_locator.click(timeout=5000)
                            logging.info("Deselected all facilities for Attempts Overview101")
                            time.sleep(1)
                        except Exception as deselect_e:
                            logging.warning(f"Failed to deselect all for Attempts Overview101: {deselect_e}")

                        # Select required facilities
                        if ending_facilities:
                            facility_list = [f.strip() for f in ending_facilities.split(',') if f.strip()]
                            for facility_name in facility_list:
                                try:
                                    locator = page.locator(f'div.slicerItemContainer:has-text("{facility_name}")')
                                    locator.click(timeout=5000)
                                    logging.info(f"Selected facility '{facility_name}' for Attempts Overview101")
                                    time.sleep(1)
                                except Exception as select_e:
                                    logging.warning(f"Selection failed for '{facility_name}' in Attempts Overview101: {select_e}")
                    else:
                        ending_chevron_selector = 'div.slicer-dropdown-menu[aria-label="EndingLocation"] i.dropdown-chevron'
                        page.wait_for_selector(ending_chevron_selector, timeout=30000)
                        page.click(ending_chevron_selector)
                        logging.info(f"Opened Ending Facility dropdown after '{button_text}'")
                    time.sleep(2)

                    if button_text == "Facility Overview101":
                        # Force popup visibility
                        try:
                            popup_id = page.get_attribute('div.slicer-dropdown-menu[aria-label="EndingLocation"]', 'aria-controls')
                            specific_popup_selector = f'#{popup_id}'
                            page.evaluate(f'''() => {{
                                const popup = document.querySelector('{specific_popup_selector}');
                                if (popup) {{
                                    popup.style.display = 'block';
                                    popup.style.visibility = 'visible';
                                    popup.style.position = 'absolute';
                                    popup.style.zIndex = '9999';
                                }}
                            }}''')
                            logging.info(f"Forced popup visibility for Facility Overview101: {specific_popup_selector}")
                        except Exception as force_e:
                            logging.warning(f"Failed to force popup for Facility Overview101: {force_e}")

                        # Deselect all by clicking "Select All"
                        try:
                            select_all_locator = page.locator('div.slicerItemContainer:has-text("Select All")')
                            select_all_locator.click(timeout=5000)
                            logging.info("Deselected all facilities for Facility Overview101")
                            time.sleep(1)
                        except Exception as deselect_e:
                            logging.warning(f"Failed to deselect all for Facility Overview101: {deselect_e}")

                        # Select required facilities
                        if ending_facilities:
                            facility_list = [f.strip() for f in ending_facilities.split(',') if f.strip()]
                            for facility_name in facility_list:
                                try:
                                    locator = page.locator(f'div.slicerItemContainer:has-text("{facility_name}")')
                                    locator.click(timeout=5000)
                                    logging.info(f"Selected facility '{facility_name}' for Facility Overview101")
                                    time.sleep(1)
                                except Exception as select_e:
                                    logging.warning(f"Selection failed for '{facility_name}' in Facility Overview101: {select_e}")

                except Exception as e:
                    logging.warning(f"Failed to open dropdown after '{button_text}': {e}")

        except Exception as e:
            logging.warning(f"Failed to click buttons or process pages: {e}")

        try:
            page.wait_for_selector('span[localize="Export"]', timeout=60000)  # Wait for Export button to appear
            logging.info("Dashboard loaded, clicking Export button...")
            page.click('span[localize="Export"]')  # Click the Export span/button
            time.sleep(1)  # Wait for menu to open
            logging.info("Export menu opened, clicking PDF option...")
            page.click('span[localize="Pdf"]')  # Click the PDF span/button
            time.sleep(2)  # Wait for dialog to open
            page.screenshot(path="after_pdf_click.png")  # Debug screenshot after PDF click
            logging.info("PDF dialog opened, clicking final Export button...")
            time.sleep(5)  # Extra wait for dialog to fully load
            try:
                page.screenshot(path="after_dialog_open.png")  # Debug screenshot after dialog opens
            except Exception as e:
                logging.warning(f"Could not take dialog screenshot: {e}")
            with page.expect_download(timeout=300000) as download_info:  # Increased timeout to 5 minutes
                page.click('button#okButton')  # Click the final Export button in the dialog
            download = download_info.value
            download.save_as(output_path)
            logging.info("PDF downloaded successfully to %s", output_path)
        except Exception as e:
            logging.error(f"Export button not found: {e}")
            raise Exception("Export button not found - check if dashboard loaded correctly. Screenshot: after_dashboard_load.png")
        browser.close()
    return output_path

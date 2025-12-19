import time
import logging

def check_activations_and_export(page, output_path, blank_selected):
    """
    Check for activations and export PDF if applicable.
    Returns (has_activations, activation_count)
    """
    has_activations = True
    activation_count = 0

    # If '(Blank)' was selected (blank_selected = True), skip Activations report and export
    # because blank means 0 activations, so send no-activations email
    if blank_selected:
        logging.info("'(Blank)' was selected in EFF — returning early with has_activations=False to send no-activations email")
        return False, 0

    # Click Activations report button before export
    try:
        logging.info("Looking for 'Activations report' button...")
        time.sleep(10)  # Additional wait time before clicking Activations report button
        page.locator('button:has-text("Activations report")').first.click(timeout=10000)
        logging.info("Clicked 'Activations report' button")
        time.sleep(10)  # Increased wait time for page to load after clicking Activations report

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
        logging.warning(f"Failed to click 'Activations report' button: {e}")

    # Export PDF
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

    return has_activations, activation_count

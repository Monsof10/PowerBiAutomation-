"""
Power BI Automation Module
Uses Playwright to automate Power BI Service interaction
"""
import logging
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PowerBIAutomation:
    """Handles Power BI Service automation using Playwright"""
    
    def __init__(self, email=None, password=None, report_url=None, headless=False):
        """
        Initialize Power BI automation
        
        Args:
            email: Power BI account email
            password: Power BI account password
            report_url: URL of the report to export
            headless: Run browser in headless mode
        """
        self.email = email or config.POWERBI_EMAIL
        self.password = password or config.POWERBI_PASSWORD
        self.report_url = report_url or config.POWERBI_REPORT_URL
        self.headless = headless or config.HEADLESS_MODE
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        
        # Validate credentials
        if not self.email or not self.password:
            raise ValueError("Power BI credentials not provided")
        if not self.report_url:
            raise ValueError("Power BI report URL not provided")
    
    def start_browser(self):
        """Start the browser and create a new context"""
        logger.info("Starting browser...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            accept_downloads=True
        )
        self.page = self.context.new_page()
        logger.info("Browser started successfully")
    
    def login(self):
        """Login to Power BI Service"""
        logger.info("Navigating to Power BI login page...")
        
        try:
            # Navigate to report URL (will redirect to login)
            self.page.goto(self.report_url, timeout=config.PAGE_LOAD_TIMEOUT * 1000)
            time.sleep(2)
            
            # Check if already logged in
            if "app.powerbi.com" in self.page.url and "login" not in self.page.url.lower():
                logger.info("Already logged in")
                return True
            
            # Enter email
            logger.info("Entering email...")
            email_input = self.page.locator('input[type="email"]').first
            email_input.fill(self.email)
            time.sleep(1)
            
            # Click Next/Submit button
            next_button = self.page.locator('input[type="submit"], button[type="submit"]').first
            next_button.click()
            time.sleep(3)
            
            # Enter password
            logger.info("Entering password...")
            try:
                password_input = self.page.locator('input[type="password"]').first
                password_input.wait_for(timeout=10000)
                password_input.fill(self.password)
                time.sleep(1)
                
                # Click Sign in button
                signin_button = self.page.locator('input[type="submit"], button[type="submit"]').first
                signin_button.click()
                time.sleep(3)
            except PlaywrightTimeoutError:
                logger.warning("Password input not found immediately, checking login state...")
            
            # Handle "Stay signed in?" dialog
            try:
                stay_signed_in = self.page.locator('input[type="submit"]').first
                if stay_signed_in.is_visible(timeout=5000):
                    logger.info("Handling 'Stay signed in' prompt...")
                    stay_signed_in.click()
                    time.sleep(2)
            except:
                pass
            
            # Wait for Power BI to load
            logger.info("Waiting for Power BI to load...")
            self.page.wait_for_load_state('networkidle', timeout=30000)
            time.sleep(3)
            
            # Verify we're on Power BI
            if "app.powerbi.com" in self.page.url:
                logger.info("Login successful!")
                return True
            else:
                logger.error("Login may have failed - unexpected URL")
                return False
                
        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout during login: {e}")
            raise Exception("Login timeout - check credentials or network connection")
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise
    
    def navigate_to_report(self):
        """Navigate to the specific report"""
        logger.info(f"Navigating to report: {self.report_url}")
        
        try:
            self.page.goto(self.report_url, timeout=config.PAGE_LOAD_TIMEOUT * 1000)
            self.page.wait_for_load_state('networkidle', timeout=30000)
            time.sleep(5)  # Wait for report to fully render
            
            logger.info("Report loaded successfully")
            return True
        except PlaywrightTimeoutError:
            logger.error("Timeout loading report")
            raise Exception("Report loading timeout - check URL and permissions")
        except Exception as e:
            logger.error(f"Error navigating to report: {e}")
            raise
    
    def apply_date_filter(self, filter_option="Last 30 days"):
        """
        Apply date filter to the report
        
        Args:
            filter_option: The date filter to apply (e.g., "Last 30 days")
        """
        logger.info(f"Attempting to apply date filter: {filter_option}")
        
        try:
            # This is a generic approach - may need customization based on your report
            # Look for filter pane or date filter elements
            
            # Try to find and click filter pane
            try:
                filter_pane = self.page.locator('[aria-label*="Filter"], [title*="Filter"]').first
                if filter_pane.is_visible(timeout=5000):
                    filter_pane.click()
                    time.sleep(2)
            except:
                logger.warning("Filter pane not found or already open")
            
            # Try to find date-related filter
            try:
                # Look for date filter dropdown or slicer
                date_elements = self.page.locator('text=/date|Date|DATE|Period|Last 30/i')
                if date_elements.count() > 0:
                    date_elements.first.click()
                    time.sleep(2)
                    
                    # Try to select "Last 30 days" option
                    option = self.page.locator(f'text="{filter_option}"').first
                    if option.is_visible(timeout=5000):
                        option.click()
                        time.sleep(3)
                        logger.info(f"Date filter '{filter_option}' applied successfully")
                    else:
                        logger.warning(f"Could not find '{filter_option}' option")
                else:
                    logger.warning("Date filter elements not found")
            except Exception as e:
                logger.warning(f"Could not apply date filter automatically: {e}")
                logger.info("Proceeding without date filter - may need manual configuration")
            
            return True
            
        except Exception as e:
            logger.warning(f"Error applying date filter: {e}")
            logger.info("Continuing without date filter...")
            return False
    
    def export_to_pdf(self, output_path=None):
        """
        Export the report as PDF
        
        Args:
            output_path: Path where PDF should be saved
            
        Returns:
            Path to downloaded PDF file
        """
        if output_path is None:
            output_path = config.DOWNLOADS_FOLDER / f"powerbi_report_{int(time.time())}.pdf"
        
        logger.info("Exporting report to PDF...")
        
        try:
            # Set up download handler
            download_info = None
            
            with self.page.expect_download(timeout=config.DOWNLOAD_TIMEOUT * 1000) as download:
                # Look for File menu or Export button
                try:
                    # Try clicking File menu
                    file_menu = self.page.locator('[aria-label="File"], button:has-text("File")').first
                    if file_menu.is_visible(timeout=5000):
                        file_menu.click()
                        time.sleep(2)
                        
                        # Click Export option
                        export_option = self.page.locator('text="Export"').first
                        export_option.click()
                        time.sleep(2)
                        
                        # Click PDF option
                        pdf_option = self.page.locator('text="PDF"').first
                        pdf_option.click()
                        time.sleep(2)
                        
                        # Click Export/Download button
                        export_button = self.page.locator('button:has-text("Export"), button:has-text("Download")').first
                        export_button.click()
                        
                    else:
                        # Alternative: Look for Export button directly
                        export_button = self.page.locator('[aria-label*="Export"], button:has-text("Export")').first
                        export_button.click()
                        time.sleep(2)
                        
                        pdf_option = self.page.locator('text="PDF"').first
                        pdf_option.click()
                        time.sleep(2)
                        
                        download_button = self.page.locator('button:has-text("Export"), button:has-text("Download")').first
                        download_button.click()
                
                except Exception as e:
                    logger.error(f"Could not find export buttons: {e}")
                    # Try keyboard shortcut as fallback
                    logger.info("Trying keyboard shortcut...")
                    self.page.keyboard.press('Control+P')
                    time.sleep(2)
            
                download_info = download.value
            
            # Save the downloaded file
            if download_info:
                download_info.save_as(str(output_path))
                logger.info(f"PDF downloaded successfully to: {output_path}")
                return output_path
            else:
                raise Exception("Download failed - no file received")
                
        except PlaywrightTimeoutError:
            logger.error("Timeout waiting for PDF download")
            raise Exception("PDF export timeout - report may be too large or export failed")
        except Exception as e:
            logger.error(f"Error exporting to PDF: {e}")
            raise
    
    def close(self):
        """Close browser and cleanup"""
        logger.info("Closing browser...")
        
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        
        logger.info("Browser closed")
    
    def run_full_automation(self, apply_filter=True):
        """
        Run the complete automation process
        
        Args:
            apply_filter: Whether to apply date filter
            
        Returns:
            Path to downloaded PDF file
        """
        pdf_path = None
        
        try:
            logger.info("Starting Power BI automation...")
            
            # Start browser
            self.start_browser()
            
            # Login
            self.login()
            
            # Navigate to report (redundant if login navigates there, but safe)
            self.navigate_to_report()
            
            # Apply date filter if requested
            if apply_filter:
                self.apply_date_filter()
            
            # Export to PDF
            pdf_path = self.export_to_pdf()
            
            logger.info("Automation completed successfully!")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Automation failed: {e}")
            raise
        finally:
            self.close()


def run_automation(email=None, password=None, report_url=None, apply_filter=True, headless=False):
    """
    Convenience function to run the full automation
    
    Args:
        email: Power BI email
        password: Power BI password
        report_url: Report URL
        apply_filter: Apply date filter
        headless: Run in headless mode
        
    Returns:
        Path to downloaded PDF
    """
    automation = PowerBIAutomation(email, password, report_url, headless)
    return automation.run_full_automation(apply_filter)


if __name__ == "__main__":
    # Test the automation
    try:
        pdf_path = run_automation()
        print(f"Success! PDF saved to: {pdf_path}")
    except Exception as e:
        print(f"Error: {e}")


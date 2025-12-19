import time
import logging

def perform_login(page, username, password):
    """
    Perform Microsoft login steps on the given page.
    """
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

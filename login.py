import os
import time
from typing import LiteralString
from playwright.sync_api import sync_playwright, Playwright, expect, Page, Browser, BrowserContext, Locator
from dotenv import load_dotenv
from shutil import rmtree

from utils.captcha_solver import get_captcha_and_solve
from utils.data_processor import clean_file, html_to_csv, combine_csv

load_dotenv()

def login_run(playwright: Playwright) -> None:
    vtop_password: str | None = os.getenv('VTOP_PASSWORD')
    vtop_username: str | None = os.getenv('VTOP_USERNAME')

    if not vtop_password or not vtop_username:
        print("VTOP_PASSWORD or VTOP_USERNAME not found in .env file. Exiting.")
        return
    
    os.makedirs("temp", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    browser: Browser = playwright.chromium.launch(
        headless=False
    )
    context: BrowserContext = browser.new_context()
    page: Page = context.new_page()
    
    page.goto("https://vtopcc.vit.ac.in/")
    page.locator("#stdForm a").click()

    max_retries = 5
    logged_in = False

    for attempt in range(max_retries):
        print(f"--- Login Attempt {attempt + 1}/{max_retries} ---")

        page.locator("#username").fill(vtop_username)
        page.locator("#password").fill(vtop_password)

        try:
            print("LOG: Checking for CAPTCHA image...")
            captcha_image_locator: Locator = page.locator("#captchaBlock img")
            expect(captcha_image_locator).to_be_visible(timeout=5000)

            print("LOG: Captcha Image found. Proceeding to solve.")
            image_data_uri: str | None = captcha_image_locator.get_attribute("src")
            
            solved_captcha = get_captcha_and_solve(image_data_uri)

            if not solved_captcha:
                print("LOG: CAPTCHA solver failed, will retry.")
                continue

            page.locator("#captchaStr").fill(solved_captcha)
            print(f"LOG: Filled CAPTCHA with: {solved_captcha}")

        except Exception:
            print("LOG: CAPTCHA block not found or timed out. Skipping CAPTCHA step.")

        page.locator("#submitBtn").click()

        try:
            error_message: Locator = page.get_by_role("alert").get_by_text("Invalid Captcha")
            expect(error_message).to_be_visible(timeout=10000)
            print("LOG: Invalid CAPTCHA text found. Retrying...")

        except Exception:
            print('LOG: CAPTCHA valid or not present, moving forward.')
            try:
                time.sleep(1)
                page.locator("#btnClosePopup").click(timeout=10000)
                logged_in = True
                break
            except Exception:
                recaptcha_response = input("If there's a Google reCAPTCHA on screen, press 'y' and solve it: ")
                if recaptcha_response.lower() == 'y':
                    input("Press Enter when you've completed the reCAPTCHA...")
                    logged_in = True
                    break
    
    if not logged_in:
        print(f"FATAL: Failed to log in after {max_retries} attempts. Exiting.")
        browser.close()
        return

    # ---------------- JUST LOG-IN TO VTOP -------------------

    print("Login successful. Press ENTER to close the browser.")
    rmtree('temp/')
    input()
    context.close()
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        login_run(playwright)
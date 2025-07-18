import os
from time import sleep
from playwright.sync_api import sync_playwright, Playwright, expect, Page, Browser, BrowserContext, Locator
from dotenv import load_dotenv
from shutil import rmtree
from utils.captcha_solver import get_captcha_and_solve
from datetime import datetime

load_dotenv()

def login_run(playwright: Playwright, headless=False) -> None:
    vtop_password: str | None = os.getenv('VTOP_PASSWORD')
    vtop_username: str | None = os.getenv('VTOP_USERNAME')

    if not vtop_password or not vtop_username:
        print("VTOP_PASSWORD or VTOP_USERNAME not found in .env file. Exiting.")
        return

    os.makedirs("temp", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    data_path = f'temp/attendance_{datetime.today().strftime("%Y-%m-%d")}.html'
    clean_data = f'data/clean_attendance_{datetime.today().strftime("%Y-%m-%d")}.html'
    output_path = f'data/attendance_{datetime.today().strftime("%Y-%m-%d")}.csv'

    browser: Browser = playwright.chromium.launch(headless=headless)
    context: BrowserContext = browser.new_context()
    page: Page = context.new_page()

    page.goto("https://vtopcc.vit.ac.in/")
    page.locator("#stdForm a").click()

    page.wait_for_load_state('networkidle', timeout=25000)

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

        except Exception as e:
            print(f"Error: {e}")
            print("LOG: CAPTCHA block not found or timed out. Skipping CAPTCHA step.")

        page.locator("#submitBtn").click()

        sleep(1)  
        
        if "login" not in page.url.lower():
            print("LOG: Login successful.")
            logged_in = True
            break

        try:
            error_message = page.get_by_role("alert").get_by_text("Invalid Captcha")
            expect(error_message).to_be_visible(timeout=5000)
            
            print("LOG: Invalid CAPTCHA text found. Retrying...")
            continue
        
        except Exception:
            sleep(5)
            continue

    if not logged_in:
        print(f"FATAL: Failed to log in after {max_retries} attempts. Exiting.")
        browser.close()
        return
    
    sleep(1)
    page.locator("#btnClosePopup").click(timeout=20000)
    return page, context, browser


if __name__ == "__main__":
    with sync_playwright() as playwright:
        page, context, browser=login_run(playwright)
        close = input('Press Enter to exit:')
        if close:
            print('Closing browser...')
            sleep(1)
            browser.close()
            context.close()
import os
from time import sleep
from typing import LiteralString
from playwright.sync_api import sync_playwright, Playwright, expect, Page, Browser, BrowserContext, Locator
from dotenv import load_dotenv
from shutil import rmtree
from captcha_solver import get_captcha_and_solve
from data_processor import clean_file, html_to_csv, combine_csv
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

load_dotenv()

def attendance_run(playwright: Playwright) -> None:
    vtop_password: str | None = os.getenv('VTOP_PASSWORD')
    vtop_username: str | None = os.getenv('VTOP_USERNAME')

    if not vtop_password or not vtop_username:
        print("VTOP_PASSWORD or VTOP_USERNAME not found in .env file. Exiting.")
        return

    os.makedirs("temp", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    data_path = 'temp/attendance.html'
    clean_data = 'data/clean_attendance.html'
    output_path = f'data/final_attendance{datetime.today().strftime('%Y-%m-%d')}.csv'

    browser: Browser = playwright.chromium.launch(
        executable_path='/usr/bin/brave-browser',
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

        # Ask if there's a Google reCAPTCHA to solve manually
        recaptcha_response = input("If there's a Google reCAPTCHA on screen, press 'y' and solve it: ")
        if recaptcha_response.lower() == 'y':
            input("Press Enter when you've completed the reCAPTCHA...")
            logged_in = True
            break

        try:
            error_message: Locator = page.get_by_role("alert").get_by_text("Invalid Captcha")
            expect(error_message).to_be_visible(timeout=10000)
            print("LOG: Invalid CAPTCHA text found. Retrying...")

        except Exception:
            print('LOG: CAPTCHA valid or not present, moving forward.')
            sleep(2)
            page.locator("#btnClosePopup").click(timeout=20000)
            logged_in = True
            break


    if not logged_in:
        print(f"FATAL: Failed to log in after {max_retries} attempts. Exiting.")
        browser.close()
        return

    page.locator('#vtopHeader button[data-bs-target="#expandedSideBar"]').click()
    page.locator("#acMenuItemHDG0067 button").click()
    page.locator("#acMenuCollapseHDG0067 a[data-url='academics/common/StudentAttendance']").click()

    page.mouse.click(764, 345)

    page.locator("#semesterSubId").select_option('CH20252601')
    page.locator("#viewStudentAttendance button[type='submit']").click()

    table_content_locator = page.locator("#getStudentDetails table[class=table]")
    expect(table_content_locator).to_be_visible(timeout=5000)

    table_html = table_content_locator.inner_html()
    print('LOG: Attendance table extracted')

    try:
        with open(data_path, 'w', encoding='utf-8') as f:
            f.write(table_html)
        print(f"LOG: Table data in {data_path}")
    except Exception as e:
        print(e)

    try:
        clean_file(data_path, clean_data)
        html_to_csv(clean_data, output_path)
        print('LOG: cleaning up temp folder')
    except Exception as e:
        print(e)

    rmtree('temp/')

    print("\nLOG: Job done successfully.")

    print("Closing browser in 10 seconds.")
    sleep(10)
    context.close()
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        attendance_run(playwright)

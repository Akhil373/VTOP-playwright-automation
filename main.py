import os
import time
from typing import LiteralString
from playwright.sync_api import sync_playwright, Playwright, expect, Page, Browser, BrowserContext, Locator
from dotenv import load_dotenv

from captcha_solver import get_captcha_and_solve
from data_processor import clean_file, html_to_csv, combine_csv

load_dotenv()

def run(playwright: Playwright) -> None:
    vtop_password: str | None = os.getenv('VTOP_PASSWORD')
    vtop_username: str | None = os.getenv('VTOP_USERNAME')

    if not vtop_password or not vtop_username:
        print("VTOP_PASSWORD or VTOP_USERNAME not found in .env file. Exiting.")
        return
    
    os.makedirs("temp", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    browser: Browser = playwright.firefox.launch(headless=False)
    context: BrowserContext = browser.new_context(
        viewport={"width": 800, "height": 600},
        screen={"width": 800, "height": 600}
    )
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
            expect(error_message).to_be_visible(timeout=3000)
            print("LOG: Invalid CAPTCHA text found. Retrying...")

        except Exception:
            print('LOG: CAPTCHA valid or not present, moving forward.')
            logged_in = True
            break
    
    if not logged_in:
        print(f"FATAL: Failed to log in after {max_retries} attempts. Exiting.")
        browser.close()
        return

    try:
        page.locator("#btnClosePopup").click(timeout=5000)
    except Exception:
        print("LOG: Popup did not appear. Continuing.")


    # ---------------- JUST LOG-IN TO VTOP -------------------

    # Temporarily using this code just to log-in to VTOP and continue with my work
    print("Login successful. Press ENTER to close the browser.")
    input()
    context.close()
    browser.close()

    # -------- COMMENT ABOVE SECTION TO START SCRAPING ---------

    page.locator('#vtopHeader button[data-bs-target="#expandedSideBar"]').click()
    page.locator("#acMenuItemHDG0067 button").click()
    page.locator("#acMenuCollapseHDG0067 a[data-url='academics/common/CalendarPreview']").click()
    
    page.mouse.click(764, 345) 

    time.sleep(1)
    page.locator("#semesterSubId").select_option("CH20242505")
    page.locator("#classGroupId").select_option("ALL")
    time.sleep(1)

    parent_div: Locator = page.locator("#getListForSemester")
    month_locator: Locator = parent_div.locator("a")

    total_months: int = month_locator.count()
    print(f"Total {total_months} months found.")

    for i in range(total_months):
        raw_html_file = os.path.join("temp", f"raw_html{i+1}.html")
        clean_html_file = os.path.join("data", f"clean_html{i+1}.html")
        output_csv_path = os.path.join("temp", f"academic_calendar{i+1}.csv")

        all_month_links = page.locator("#getListForSemester a")
        current_month = all_month_links.nth(i)
        
        month_name = current_month.text_content()
        if not month_name:
            print(f"Warning: Could not get text for month at index {i}. Skipping.")
            continue
            
        print(f"LOG: Parsing {month_name.strip()}")
        current_month.click()

        table_content_locator: Locator = page.locator("#list-wrapper table")
        expect(table_content_locator).to_be_visible(timeout=10000)
        
        table_html = table_content_locator.inner_html()
        print("LOG: Academic calendar HTML content extracted.")
        
        with open(raw_html_file, "w", encoding='utf-8') as f:
            f.write(table_html)
        
        clean_file(raw_html_file, clean_html_file)
        html_to_csv(clean_html_file, output_csv_path, month_name.strip())

    
    combine_csv()

    print("\nLOG: Job done successfully.")

    print("Closing browser in 10 seconds.")
    time.sleep(10)
    context.close()
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
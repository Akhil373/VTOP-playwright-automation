import os
import time
from playwright.sync_api import sync_playwright, Playwright, expect, Page, Browser, BrowserContext, Locator
from dotenv import load_dotenv

from captcha_solver import get_captcha_and_solve
from data_processor import clean_file, html_to_csv

load_dotenv()


def run(playwright: Playwright) -> None:
    """Main function to orchestrate the web scraping process."""
    vtop_password: str | None = os.getenv('VTOP_PASSWORD')
    vtop_username: str | None = os.getenv('VTOP_USERNAME')

    if not vtop_password or not vtop_username:
        print("VTOP_PASSWORD or VTOP_USERNAME not found in .env file. Exiting.")
        return

    raw_html_file = os.path.join("temp", "raw_html.html")
    clean_html_file = os.path.join("data", "clean_html.html")
    captcha_image_path = os.path.join("temp", "captcha.jpg")
    output_csv_path = os.path.join("data", "academic_calendar.csv")
    
    os.makedirs("temp", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    browser: Browser = playwright.chromium.launch(headless=False)
    context: BrowserContext = browser.new_context()
    page: Page = context.new_page()

    try:
        page.goto("https://vtopcc.vit.ac.in/")
        
        page.locator("#stdForm a").click()

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
                print("LOG: Unable to solve CAPTCHA. Exiting.")
                return

            page.locator("#captchaStr").fill(solved_captcha)
            print(f"LOG: Filled CAPTCHA with: {solved_captcha}")

        except Exception:
            print("LOG: CAPTCHA block not found or timed out. Skipping CAPTCHA step.")

        page.locator("#submitBtn").click()

        try:
            error_message: Locator = page.get_by_role("alert").get_by_text("Invalid Captcha")
            expect(error_message).to_be_visible(timeout=3000)
            print("LOG: Invalid CAPTCHA. Please try again. Exiting.")
            return
        except Exception:
            print('LOG: CAPTCHA valid or not present, moving forward.')

        time.sleep(2) 
        if page.locator("#btnClosePopup").is_visible():
            page.locator("#btnClosePopup").click()

        page.locator('#vtopHeader button[data-bs-target="#expandedSideBar"]').click()
        page.locator("#acMenuItemHDG0067 button").click()
        page.locator("#acMenuCollapseHDG0067 a[data-url='academics/common/CalendarPreview']").click()
        page.mouse.click(764, 345)

        time.sleep(1)
        page.locator("#semesterSubId").select_option("CH20242505")
        page.locator("#classGroupId").select_option("ALL")
        time.sleep(1)

        page.locator("#getListForSemester a").last.click()

        time.sleep(2)
        table_content_locator: Locator = page.locator("#list-wrapper table")
        expect(table_content_locator).to_be_visible(timeout=10000)
        
        table_html = table_content_locator.inner_html()
        print("LOG: Academic calendar HTML content extracted.")
        
        with open(raw_html_file, "w", encoding='utf-8') as f:
            f.write(table_html)
        
        clean_file(raw_html_file, clean_html_file)
        html_to_csv(clean_html_file, output_csv_path)

        print("\nLOG: Job done successfully.")

    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}")
    finally:
        print("Closing browser in 10 seconds.")
        time.sleep(10)
        context.close()
        browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
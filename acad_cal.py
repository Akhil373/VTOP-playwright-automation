import os
from time import sleep
from typing import LiteralString
from playwright.sync_api import sync_playwright, Playwright, expect, Page, Browser, BrowserContext, Locator
from dotenv import load_dotenv
from shutil import rmtree
from login import login_run

from utils.captcha_solver import get_captcha_and_solve
from utils.data_processor import clean_file, html_to_csv, combine_csv

load_dotenv()

def calendar_run(playwright: Playwright) -> None:
    page, context, browser = login_run(playwright, False)

    page.locator('#vtopHeader button[data-bs-target="#expandedSideBar"]').click()
    page.locator("#acMenuItemHDG0067 button").click()
    page.locator("#acMenuCollapseHDG0067 a[data-url='academics/common/CalendarPreview']").click()

    page.mouse.click(764, 345)

    sleep(0.5)
    page.locator("#semesterSubId").select_option("CH20252601")
    page.locator("#classGroupId").select_option("ALL")
    sleep(0.5)

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
        sleep(1)

        table_content_locator: Locator = page.locator("#list-wrapper table")
        expect(table_content_locator).to_be_visible(timeout=10000)

        table_html = table_content_locator.inner_html()
        print("LOG: Academic calendar HTML content extracted.")

        with open(raw_html_file, "w", encoding='utf-8') as f:
            f.write(table_html)

        clean_file(raw_html_file, clean_html_file)
        html_to_csv(clean_html_file, output_csv_path, month_name.strip())


    combine_csv()

    rmtree('temp/')

    print("\nLOG: Job done successfully.")

    print("Closing browser in 5 seconds.")
    sleep(10)
    context.close()
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        calendar_run(playwright)

import os
from time import sleep
from playwright.sync_api import sync_playwright, Playwright, expect, Page, Browser, BrowserContext, Locator
from dotenv import load_dotenv
from shutil import rmtree
from utils.captcha_solver import get_captcha_and_solve
from utils.data_processor import clean_file, html_to_csv, attendance_stats
from datetime import datetime
from login import login_run

load_dotenv()

def attendance_run(playwright: Playwright) -> None:
    page, context, browser = login_run(playwright, False)

    data_path = f'temp/attendance_{datetime.today().strftime("%Y-%m-%d")}.html'
    clean_data = f'data/clean_attendance_{datetime.today().strftime("%Y-%m-%d")}.html'
    output_path = f'data/attendance_{datetime.today().strftime("%Y-%m-%d")}.csv'

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

    attendance_stats(output_path)

    rmtree('temp/')

    print("\nLOG: Job done successfully.")

    print("Closing browser in 5 seconds.")
    sleep(5)
    context.close()
    browser.close()
    
if __name__ == "__main__":
    with sync_playwright() as playwright:
        attendance_run(playwright)

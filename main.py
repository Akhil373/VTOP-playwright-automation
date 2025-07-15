from playwright.sync_api import sync_playwright
from plyer import notification

def run_calendar():
    from acad_cal import calendar_run
    with sync_playwright() as playwright:
        calendar_run(playwright)

def run_attendance():
    from attendance import attendance_run
    with sync_playwright() as playwright:
        attendance_run(playwright)

def run_login():
    from login import login_run
    with sync_playwright() as playwright:
        login_run(playwright)

if __name__ == '__main__':
    print('Select option\n')
    print('1. Academic Calendar')
    print('2. Attendance Data')
    print('3. Just login to VTOP')
    try:
        ch = int(input('Enter: '))
        match ch:
            case 1:
                print('Scraping Academic Calendar...')
                run_calendar()
            case 2:
                print('Scraping Attedance Data...')
                run_attendance()
            case 3:
                print('Logging to VTOP...')
                run_login()
            case _:
                print('Input Error')

        notification.notify(
            title='Vtop-Automation',
            message='Script has finished running',
            timeout=5
        )
    except Exception as e:
        print(f'Error: {str(e)}')
        import traceback
        traceback.print_exc()

import os
from playwright.sync_api import sync_playwright, Playwright, expect, Page, Browser, BrowserContext, Locator
# from dotenv import load_dotenv
import base64
from time import sleep

# load_dotenv()

def login_run(playwright: Playwright) -> None:    
    dataset_path = 'temp/dataset'

    browser: Browser = playwright.chromium.launch(
        executable_path='/usr/bin/brave-browser',
        headless=False
    )
    context: BrowserContext = browser.new_context(
        viewport={"width": 800, "height": 600},
        screen={"width": 800, "height": 600}
    )
    page: Page = context.new_page()
    
    page.goto("https://vtopcc.vit.ac.in/")
    page.locator("#stdForm a").click()

    captcha_image_locator: Locator = page.locator("#captchaBlock img")

    for i in range(198, 300):
        print(f'iteration number: {i}')
        print("LOG: Checking for CAPTCHA image...")
        expect(captcha_image_locator).to_be_visible(timeout=10000)

        print("LOG: Captcha Image found. Reading source.")
        image_data_uri: str | None = captcha_image_locator.get_attribute("src")

        header, encoded_data = image_data_uri.split(",", 1)
        image_data: bytes = base64.b64decode(encoded_data)
        
        file_path = os.path.join(dataset_path, f"captcha{i}.jpg")
        with open(file_path, "wb") as f:
            f.write(image_data)
        print(f"CAPTCHA image saved to {file_path}")

        if i < 300:
            print("LOG: Clicking reload button.")
            page.locator('#button-addon2').click()

            print("LOG: Waiting for new image to load...")
            expect(captcha_image_locator).not_to_have_attribute("src", image_data_uri, timeout=15000)
            print("LOG: New image detected.")


    print('\nClosing browser in 5s')
    sleep(5)
    context.close()
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        login_run(playwright)
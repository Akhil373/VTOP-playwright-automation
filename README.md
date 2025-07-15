# Playwright VTOP Automation

Automation Playwright and Python to automate access to the VTOP portal, including login, CAPTCHA solving, and data extraction.

## Project Structure
- `main.py`: Orchestrates the automation, login, CAPTCHA solving, and data extraction.
- `captcha_solver.py`: Handles CAPTCHA solving (Gemini API and local OCR).
- `data_processor.py`: Cleans HTML and converts it to CSV.
- `data/`: Stores cleaned HTML and final CSV output.
- `temp/`: Stores temporary files (e.g., raw HTML, CAPTCHA images).

## Setup
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   Or use `pyproject.toml` with your preferred tool (e.g., `pip`, `poetry`).

2. Create a `.env` file with your VTOP credentials:
   ```env
   GOOGLE_API_KEY=gemini_api_key
   VTOP_USERNAME=your_username
   VTOP_PASSWORD=your_password
   ```

## Usage
Run the main script:
```sh
python main.py
```

## Example
This repository includes an example that extracts the academic calendar from VTOP and saves it as a CSV file. You can adapt the code to automate other tasks on VTOP as needed.

## CAPTCHA Solving Note
CAPTCHA solving in this project uses general-purpose OCR and Gemini API, which may not always succeed. For more reliable results, consider custom training a machine learning model specifically for the target CAPTCHA. Since this project focuses on Playwright automations, CAPTCHA solving may occasionally fail and require retries.

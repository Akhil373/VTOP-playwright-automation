import pandas as pd
from bs4 import BeautifulSoup
import os
import glob
import csv

def clean_file(input_file, output_file) -> None:
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            stripped_line: str = line.strip()
            if stripped_line:
                outfile.write(stripped_line + '\n')

def html_to_csv(file_path, output_path, month=None) -> None:
    html_string: str = ""
    with open(file_path) as f:
        html_string = f.read()

    soup = BeautifulSoup(html_string, 'html.parser')
    data: list = []
    table_rows= soup.find_all('tr')

    for row in table_rows:
        all_cells = row.find_all(['th', 'td']) # type: ignore
        cols = [cell.get_text(strip=True) for cell in all_cells]
        data.append(cols)

    header = data[0]
    table_data = data[1:]
    df = pd.DataFrame(table_data, columns=header)
    if month:
        df.insert(0, 'Month', month)
        print("---Academic Calendar---")

    print('---Attendance---')
    print(df)
    df.to_csv(output_path, index=False)

    print(f"\nData successfully saved to {output_path}")

def combine_csv(input_dir="temp"):
    file_pattern = os.path.join(input_dir, 'academic_calendar*.csv')
    output_file = os.path.join("data", 'academic_calendar.csv')

    all_files = glob.glob(file_pattern)

    if not all_files:
        print(f"No files found with pattern '{file_pattern}'")
    else:
        df_list = [pd.read_csv(file) for file in all_files]
        combined_df = pd.concat(df_list, ignore_index=True)
        combined_df.to_csv(output_file, index=False)
        print(f"Successfully combined {len(all_files)} files into '{output_file}'")


def attendance_stats(current_attendance):
    df = pd.read_csv(current_attendance, skipfooter=1, engine='python')

    df['Attended Classes'] = pd.to_numeric(df['Attended Classes'])
    df['Total Classes'] = pd.to_numeric(df['Total Classes'])

    attended_sum = df['Attended Classes'].sum()
    total_sum = df['Total Classes'].sum()

    missed_courses_df = df[df['Attended Classes'] < df['Total Classes']]

    if total_sum > 0:
        overall_percent = (attended_sum / total_sum) * 100
        print(f'Overall Percentage: {overall_percent:.2f}%')
    else:
        print('Error: Total classes is 0.')

    print(f'Total Attended Classes: {attended_sum}')
    print(f'Total Classes: {total_sum}')
    
    if not missed_courses_df.empty:
        print("\nCourses with Missed Classes:")
        print(missed_courses_df[['Course\nTitle', 'Attended Classes', 'Total Classes', 'Attendance Percentage']])
    else:
        print("\nGreat! No classes missed in any course.")

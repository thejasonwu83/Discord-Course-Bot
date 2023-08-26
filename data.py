import pandas as pd
import numpy as np
import math

grades_df = pd.read_csv("grades-by-year-dataset.csv")
gpa_df = pd.read_csv("gpa-by-year-dataset.csv")

"""
Year | Term | YearTerm | Subject | Number | Course Title | Sched Type
A+ | A | A- | B+ | B | B- | C+ | C | C- | D+ | D | D- | F | W | Primary Instructor
"""

gpa = {
    'A+': 4.0,
    'A' : 4.0,
    'A-': 3.67,
    'B+': 3.33,
    'B' : 3.0,
    'B-': 2.67,
    'C+': 2.33,
    'C' : 2.0,
    'C-': 1.67,
    'D+': 1.33,
    'D' : 1.0,
    'D-': 0.67,
    'F' : 0.0
}

def calc_gpa(g: pd.DataFrame, index: int):
    num_students = np.sum(g[index:index+13])
    total_points = 4.0 * (g['A+'] + g['A']) + 3.67 * g['A-'] + 3.33 * g['B+'] + 3 * g['B'] + 2.67 * g['B-'] + 2.33 * g['C+'] + 2 * g['C'] + 1.67 * g['C-'] + 1.33 * g['D+'] + g['D'] + 0.67 * g['D-']
    if total_points == 0:
        print(g)
    return round(total_points / num_students, 2)

def calc_gpa_df(orig_df: pd.DataFrame, name: str, index: int):
    gpa_df = orig_df.copy()
    gpa_df['Average GPA'] = gpa_df.apply(lambda row: calc_gpa(row, index), axis=1)
    gpa_df.to_csv(name + ".csv", index=False)

def calc_median(g: pd.Series, og: pd.DataFrame, index: int):
    left_idx = 0
    right_idx = 12
    while g[left_idx] == 0:
        left_idx = left_idx + 1
    while g[right_idx] == 0:
        right_idx = right_idx - 1
    left = g[left_idx]
    right = g[right_idx]
    while left_idx != right_idx:
        if left < right:
            left_idx = left_idx + 1
            while g[left_idx] == 0:
                left_idx = left_idx + 1
            left = left + g[left_idx]
        elif right <= left:
            right_idx = right_idx - 1
            while g[right_idx] == 0:
                right_idx = right_idx - 1
            right = right + g[right_idx]
    return og.columns[left_idx + index]

def calc_median_df(g: pd.DataFrame, name: str, index: int):
    g['Median Grade'] = g.apply(lambda row: calc_median(row[index:index+13], g, index), axis=1)
    g.to_csv(name + ".csv", index=False)

def calc_std(g: pd.DataFrame, index: int):
    num_students = np.sum(g[index:index+13])
    mean = g['Average GPA']
    variance = (g['A+'] + g['A']) * (mean - 4.0) ** 2 + g['A-'] * (mean - 3.67) ** 2 + g['B+'] * (mean - 3.33) ** 2 + g['B'] * (mean - 3.0) ** 2 + g['B-'] * (mean - 2.67) ** 2 + g['C+'] * (mean - 2.33) ** 2 + g['C'] * (mean - 2.0) ** 2 + g['C-'] * (mean - 1.67) ** 2 + g['D+'] * (mean - 1.33) ** 2 + g['D'] * (mean - 1) ** 2 + g['D-'] * (mean - 0.67) ** 2
    return round(math.sqrt(variance / num_students), 2)
    
def calc_std_df(g: pd.DataFrame, name: str, index: int):
    g['Standard Deviation'] = g.apply(lambda row: calc_std(row, index), axis=1)
    g.to_csv(name + ".csv", index=False)

def parse_last_names(name: str):
    names = str(name).split(", ")
    return names[0]

def parse_last_names_df(g: pd.DataFrame, filename: str):
    g["Instructor Last Name"] = g.apply(lambda row: parse_last_names(row['Primary Instructor']), axis=1)
    g.to_csv(filename + ".csv", index=False)

def condense_by_term():
    Years = []
    Terms = []
    Subjects = []
    Numbers = []
    Grades = []
    Instructors = []
    grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'W']
    for grade in grades:
        Grades.append([grade])
    terms = ["Fall", "Spring", "Summer", "Winter"]
    years = list(range(2010, 2023))[::-1]
    for year in years:
        for term in terms:
            if (term == "Winter") & (year < 2014):
                continue
            df = grades_df.loc[(grades_df['Term'] == term) & (grades_df['Year'] == year)]
            subjects = sorted(set((df['Subject'].to_list())))
            for subject in subjects:
                subject_df = df.loc[df['Subject'] == subject]
                numbers = sorted(set(subject_df['Number'].to_list()))
                for number in numbers:
                    course_df = subject_df.loc[subject_df['Number'] == number]
                    instructors = set(course_df['Primary Instructor'].to_list()[1:])
                    for instructor in instructors:
                        instructor_df = course_df.loc[course_df['Primary Instructor'] == instructor]
                        aggregate_grades = []
                        for grade in grades:
                            aggregate_grades.append(sum(instructor_df[grade].to_list()))
                        Years.append(year)
                        Terms.append(term)
                        Subjects.append(subject)
                        Numbers.append(number)
                        for i in range(len(Grades)):
                            Grades[i].append(int(aggregate_grades[i]))
                        Instructors.append(instructor)
    data = [Years, Terms, Subjects, Numbers]
    for grade in Grades:
        data.append(grade[1:])
    data.append(Instructors)
    columns=["Years", "Term", "Subject", "Number", 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'W', "Primary Instructor"]
    df = pd.DataFrame(data).transpose()
    df.columns = columns
    df = df.dropna()
    df.to_csv("condensed-grades-by-term.csv", index=False)

def condense_by_instructor():
    grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'W']
    condensed_df = pd.read_csv("condensed-grades-by-term.csv")
    Subjects = []
    Numbers = []
    Grades = []
    Instructors = []
    grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'W']
    for grade in grades:
        Grades.append([grade])
    subjects = sorted(set(condensed_df['Subject'].to_list()))
    for subject in subjects:
        subject_df = condensed_df.loc[condensed_df['Subject'] == subject]
        numbers = sorted(set(subject_df['Number'].to_list()))
        for number in numbers:
            numbers_df = subject_df.loc[subject_df['Number'] == number]
            instructors = set(numbers_df['Primary Instructor'])
            for instructor in instructors:
                instructor_df = numbers_df.loc[numbers_df['Primary Instructor'] == instructor]
                aggregate_grades = []
                for grade in grades:
                    aggregate_grades.append(sum(instructor_df[grade].to_list()))
                Subjects.append(subject)
                Numbers.append(number)
                for i in range(len(Grades)):
                    Grades[i].append(int(aggregate_grades[i]))
                Instructors.append(instructor)
    data = [Subjects, Numbers]
    for grade in Grades:
        data.append(grade[1:])
    data.append(Instructors)
    columns=["Subject", "Number", 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'W', "Primary Instructor"]
    df = pd.DataFrame(data).transpose()
    df.columns = columns
    df = df.dropna()
    df.to_csv("condensed-grades-by-instructor.csv", index=False)

def condense_by_course():
    grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'W']
    condensed_df = pd.read_csv("condensed-grades-by-instructor.csv")
    Subjects = []
    Numbers = []
    Grades = []
    grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'W']
    for grade in grades:
        Grades.append([grade])
    subjects = sorted(set(condensed_df['Subject'].to_list()))
    for subject in subjects:
        subject_df = condensed_df.loc[condensed_df['Subject'] == subject]
        numbers = sorted(set(subject_df['Number'].to_list()))
        for number in numbers:
            numbers_df = subject_df.loc[subject_df['Number'] == number]
            aggregate_grades = []
            for grade in grades:
                aggregate_grades.append(sum(numbers_df[grade].to_list()))
            Subjects.append(subject)
            Numbers.append(number)
            for i in range(len(Grades)):
                Grades[i].append(int(aggregate_grades[i]))
    data = [Subjects, Numbers]
    for grade in Grades:
        data.append(grade[1:])
    columns=["Subject", "Number", 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'W']
    df = pd.DataFrame(data).transpose()
    df.columns = columns
    df = df.dropna()
    df.to_csv("condensed-grades-by-course.csv", index=False)

def main():
    df1 = pd.read_csv("condensed-gpa-by-term.csv")
    df2 = pd.read_csv("condensed-gpa-by-instructor.csv")
    df3 = pd.read_csv("condensed-gpa-by-course.csv")
    parse_last_names_df(df1, "condensed-gpa-by-term")
    parse_last_names_df(df2, "condensed-gpa-by-instructor")


if __name__ == "__main__":
    main()


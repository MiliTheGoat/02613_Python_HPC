class Student:
    def __init__(self, name, list_of_courses):
        self.name = name
        self.courses = list_of_courses
    def attends(self, course):
        if course in self.courses:
            return True
        else:
            return False
        

def coursestudents(list_of_students, course):
    students_attending = []
    for student in list_of_students:
        if student.attends(course):
            students_attending.append(student.name)
    return students_attending
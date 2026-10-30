from modules.courses import get_courses
from modules.students import get_students
from modules.assignments import get_assignments

# di dalam do_GET()
elif self.path == "/courses":
 self.send_json({"courses": get_courses()})
elif self.path == "/students":
 self.send_json({"students": get_students()})
elif self.path == "/assignments":
 self.send_json({"assignments": get_assignments()})
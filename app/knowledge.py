"""
VoxCampus University Knowledge Base
====================================
Categories:
  courses | admissions | fees | exams | faculty |
  departments | schedules | facilities | events | academic | general
"""

from typing import List
from app.rag import Chunk

_RAW_CHUNKS: List[dict] = [

    # ══════════════════════════════════════════════════════
    # COURSES
    # ══════════════════════════════════════════════════════
    {"id": "crs-001", "cat": "courses", "title": "B.Tech Programs",
     "content": "Chitkara University offers B.Tech (4 years) in: Computer Science & Engineering (CSE), "
                "CSE-AI/ML, CSE-Data Science, Electronics & Communication (ECE), Mechanical Engineering, "
                "Civil Engineering, Electrical Engineering, Information Technology (IT), and Biotechnology."},

    {"id": "crs-002", "cat": "courses", "title": "CSE B.Tech Specializations",
     "content": "B.Tech CSE students can specialize in: Artificial Intelligence & Machine Learning, "
                "Data Science & Analytics, Cybersecurity, Cloud Computing, Internet of Things (IoT), "
                "and Full Stack Development."},

    {"id": "crs-003", "cat": "courses", "title": "Undergraduate Programs (Non-Engineering)",
     "content": "Non-engineering UG programs include: BCA (3 years), B.Sc in Physics/Chemistry/Maths/"
                "Biotechnology/Nursing, B.Com (General & Honours), BBA, B.Pharma (4 years), "
                "and B.Architecture (5 years)."},

    {"id": "crs-004", "cat": "courses", "title": "Postgraduate Programs",
     "content": "PG programs: M.Tech (2 years) in CSE/ECE/Mechanical/Civil/Biotechnology, "
                "MBA (2 years) in Marketing/Finance/HR/Operations/Business Analytics, "
                "MCA (2 years), M.Sc in Maths/Physics/Chemistry/Biotechnology, M.Pharma (2 years)."},

    {"id": "crs-005", "cat": "courses", "title": "Doctoral Programs",
     "content": "Ph.D programs are available in Engineering, Sciences, Management, Pharmacy, "
                "and Architecture at Chitkara University."},

    {"id": "crs-006", "cat": "courses", "title": "MBA Specializations",
     "content": "The 2-year MBA program offers specializations in Marketing, Finance, Human Resources, "
                "Operations Management, and Business Analytics."},

    # ══════════════════════════════════════════════════════
    # ADMISSIONS
    # ══════════════════════════════════════════════════════
    {"id": "adm-001", "cat": "admissions", "title": "Admission Process Steps",
     "content": "Admission steps: (1) Apply online at admissions.chitkara.edu.in, "
                "(2) JEE Main / CUET / Chitkara University Entrance Test, "
                "(3) Document verification, (4) Seat allotment and fee payment, "
                "(5) Report to campus."},

    {"id": "adm-002", "cat": "admissions", "title": "B.Tech Eligibility",
     "content": "For B.Tech: 10+2 with PCM and minimum 60% marks. "
                "JEE Main score is preferred. Merit-based admission also available."},

    {"id": "adm-003", "cat": "admissions", "title": "MBA & PG Eligibility",
     "content": "MBA: graduation with min. 50%; CAT/MAT/GMAT accepted. "
                "M.Tech: B.Tech/B.E. with min. 55%; GATE preferred. "
                "MCA: BCA/B.Sc (IT/CS) with min. 55%."},

    {"id": "adm-004", "cat": "admissions", "title": "BCA & B.Sc Eligibility",
     "content": "BCA and B.Sc require 10+2 with minimum 50% marks. "
                "No specific stream mandatory for BCA; science stream preferred for B.Sc."},

    {"id": "adm-005", "cat": "admissions", "title": "Documents Required",
     "content": "Documents needed: 10th & 12th marksheets, graduation marksheets (PG), "
                "JEE/GATE/CAT scorecard, Transfer Certificate, Migration Certificate, "
                "Character Certificate, 6 photos, Aadhar Card, category certificate (if applicable)."},

    {"id": "adm-006", "cat": "admissions", "title": "Admission Deadlines 2026",
     "content": "2026 batch: Applications open January 2026. "
                "Last date June 30, 2026. Counselling July 2026. Classes begin August 2026."},

    {"id": "adm-007", "cat": "admissions", "title": "Admission Contact",
     "content": "Admissions office: +91-1723-980000, admissions@chitkara.edu.in, www.chitkara.edu.in."},

    # ══════════════════════════════════════════════════════
    # FEES
    # ══════════════════════════════════════════════════════
    {"id": "fee-001", "cat": "fees", "title": "B.Tech Fee Structure",
     "content": "Annual B.Tech fee: CSE/IT/AI-ML — ₹1,80,000 to ₹2,20,000. "
                "ECE/Mechanical/Civil — ₹1,50,000 to ₹1,80,000 per year."},

    {"id": "fee-002", "cat": "fees", "title": "UG Non-Engineering Fees",
     "content": "Annual fees: BCA — ₹80,000–₹1,00,000; B.Sc — ₹60,000–₹80,000; "
                "BBA/B.Com — ₹70,000–₹90,000 per year."},

    {"id": "fee-003", "cat": "fees", "title": "PG Programs Fee",
     "content": "Annual PG fees: M.Tech — ₹1,20,000–₹1,60,000; MBA — ₹1,50,000–₹2,00,000; "
                "MCA — ₹1,00,000–₹1,20,000 per year."},

    {"id": "fee-004", "cat": "fees", "title": "Hostel and Mess Charges",
     "content": "Hostel: ₹60,000–₹90,000/year (AC/Non-AC). Mess: ₹45,000–₹55,000/year."},

    {"id": "fee-005", "cat": "fees", "title": "Scholarships Available",
     "content": "Scholarships: Merit (up to 100% waiver for JEE rank < 5000), Sports (national/state), "
                "SC/ST government schemes, Chitkara Excellence Award (95%+ in 12th), Sibling Discount (10%)."},

    {"id": "fee-006", "cat": "fees", "title": "Fee Payment Options",
     "content": "Semester-wise payment available. EMI via partner banks. Online payment through university portal. "
                "Fees subject to annual revision."},

    {"id": "fee-007", "cat": "fees", "title": "Supplementary Exam Fee",
     "content": "Re-exam fee: ₹500 per paper. Held in June (Odd Semester) and July (Even Semester)."},

    # ══════════════════════════════════════════════════════
    # EXAMS
    # ══════════════════════════════════════════════════════
    {"id": "exm-001", "cat": "exams", "title": "Semester Structure",
     "content": "Two semesters: Odd (August–December) and Even (January–May)."},

    {"id": "exm-002", "cat": "exams", "title": "Mid-Term Exams",
     "content": "Odd Semester mid-terms: October (Week 2–3). Even Semester mid-terms: March (Week 2–3)."},

    {"id": "exm-003", "cat": "exams", "title": "End-Term Exams",
     "content": "Odd Semester end-terms: November–December. Even Semester end-terms: April–May. "
                "Results declared within 30 days at student.chitkara.edu.in."},

    {"id": "exm-004", "cat": "exams", "title": "Practical Examinations",
     "content": "Practicals held in last 2 weeks of each semester. Lab files must be submitted before practical exam."},

    {"id": "exm-005", "cat": "exams", "title": "Grading System",
     "content": "Grades: O (90–100, 10pts), A+ (80–89, 9pts), A (70–79, 8pts), B+ (60–69, 7pts), "
                "B (50–59, 6pts), C (40–49, 5pts), F (below 40, fail)."},

    {"id": "exm-006", "cat": "exams", "title": "Supplementary Exam Rules",
     "content": "Students with F grade can take supplementary exam. Fee: ₹500/paper. "
                "June (Odd Semester) and July (Even Semester)."},

    {"id": "exm-007", "cat": "exams", "title": "Exam Rules",
     "content": "ID card mandatory. No electronic devices allowed. 75% attendance required to appear in exams."},

    # ══════════════════════════════════════════════════════
    # FACULTY
    # ══════════════════════════════════════════════════════
    {"id": "fac-001", "cat": "faculty", "title": "CSE Department Faculty",
     "content": "CSE has 60+ faculty members. Specializations: AI/ML, Data Science, Cloud, Cybersecurity, Networks. "
                "500+ research publications. Office: CSE Block, Room 201."},

    {"id": "fac-002", "cat": "faculty", "title": "ECE Department Faculty",
     "content": "ECE has 40+ faculty. Specializations: VLSI, Embedded Systems, Signal Processing, IoT."},

    {"id": "fac-003", "cat": "faculty", "title": "Mechanical Engineering Faculty",
     "content": "Mechanical dept specializes in CAD/CAM, Thermal Engineering, Manufacturing. PhD-qualified faculty."},

    {"id": "fac-004", "cat": "faculty", "title": "Management (MBA) Faculty",
     "content": "Management school led by Dean with IIM PhD. Specializations: Marketing, Finance, HR, Operations, Analytics."},

    {"id": "fac-005", "cat": "faculty", "title": "Faculty Contact & Office Hours",
     "content": "Office hours: Mon–Fri, 9 AM–5 PM. Contact via ERP: erp.chitkara.edu.in → Faculty Directory. "
                "Email: firstname.lastname@chitkara.edu.in."},

    {"id": "fac-006", "cat": "faculty", "title": "Mentor System",
     "content": "Each student gets a faculty mentor at program start for academic guidance, "
                "career advice, and support throughout the degree."},

    {"id": "fac-007", "cat": "faculty", "title": "Research Labs",
     "content": "Labs available: AI Lab, IoT Lab, Robotics Lab, Pharma Research Lab, "
                "VLSI Design Lab, Cloud Computing Lab, Cybersecurity Lab."},

    # ══════════════════════════════════════════════════════
    # DEPARTMENTS
    # ══════════════════════════════════════════════════════
    {"id": "dep-001", "cat": "departments", "title": "Department of Computer Science (CSE)",
     "content": "The CSE department is the largest at Chitkara University with 60+ faculty and 5000+ students. "
                "It offers B.Tech, M.Tech, and Ph.D programs. Key research areas: AI, ML, Cybersecurity, Cloud, IoT, Data Science. "
                "Location: CSE Block, Rajpura campus."},

    {"id": "dep-002", "cat": "departments", "title": "Department of Electronics & Communication (ECE)",
     "content": "ECE department offers B.Tech and M.Tech programs. Research areas include VLSI Design, "
                "Embedded Systems, Signal Processing, IoT, and 5G Communications. Has state-of-the-art electronics labs."},

    {"id": "dep-003", "cat": "departments", "title": "Department of Mechanical Engineering",
     "content": "Mechanical Engineering offers B.Tech and M.Tech. Focus areas: CAD/CAM, Thermal Engineering, "
                "Manufacturing, Robotics, Automobile Engineering. Has advanced manufacturing lab and 3D printing facility."},

    {"id": "dep-004", "cat": "departments", "title": "Department of Civil Engineering",
     "content": "Civil Engineering offers B.Tech and M.Tech. Specializations: Structural Engineering, "
                "Environmental Engineering, Transportation, Construction Management. Has survey and materials testing labs."},

    {"id": "dep-005", "cat": "departments", "title": "School of Business (MBA)",
     "content": "Chitkara Business School offers MBA with specializations in Marketing, Finance, HR, Operations, "
                "and Business Analytics. Ranked among top B-schools in North India. Has dedicated placement cell."},

    {"id": "dep-006", "cat": "departments", "title": "Department of Pharmacy",
     "content": "Pharmacy department offers B.Pharma and M.Pharma programs. Has WHO-GMP compliant labs, "
                "pharmaceutical analysis lab, and research center. Strong industry connections for internships."},

    {"id": "dep-007", "cat": "departments", "title": "Department of Applied Sciences",
     "content": "Applied Sciences covers Physics, Chemistry, Mathematics, and Biology. "
                "Supports all engineering programs with foundation courses. Also offers B.Sc and M.Sc programs."},

    {"id": "dep-008", "cat": "departments", "title": "School of Architecture",
     "content": "Architecture school offers B.Architecture (5 years). Equipped with design studios, "
                "model-making labs, and advanced CAD facilities. Has collaborations with international architecture firms."},

    {"id": "dep-009", "cat": "departments", "title": "Department of BCA & IT",
     "content": "BCA/IT department offers 3-year BCA and MCA programs. Focus on software development, "
                "web technologies, database management, and cybersecurity. Industry-aligned curriculum."},

    # ══════════════════════════════════════════════════════
    # ACADEMIC SCHEDULES
    # ══════════════════════════════════════════════════════
    {"id": "sch-001", "cat": "schedules", "title": "Academic Calendar 2025-26",
     "content": "Academic year 2025-26: Odd Semester — August 1 to December 31, 2025. "
                "Even Semester — January 1 to May 31, 2026. Summer break: June–July 2026."},

    {"id": "sch-002", "cat": "schedules", "title": "Class Timings",
     "content": "Regular class hours: Monday to Friday, 8:00 AM to 5:00 PM. "
                "Lunch break: 12:30 PM to 1:30 PM. Saturday: 8:00 AM to 1:00 PM (for special sessions)."},

    {"id": "sch-003", "cat": "schedules", "title": "Holiday List",
     "content": "Major holidays: Republic Day (Jan 26), Holi, Good Friday, Eid, Independence Day (Aug 15), "
                "Dussehra, Diwali, Guru Nanak Jayanti, Christmas. Full holiday list available on university portal."},

    {"id": "sch-004", "cat": "schedules", "title": "Registration & Enrollment Schedule",
     "content": "Course registration: First week of each semester via ERP portal (erp.chitkara.edu.in). "
                "Fee payment deadline: 2 weeks after registration. Late fee applies after deadline."},

    {"id": "sch-005", "cat": "schedules", "title": "Internship Schedule",
     "content": "Summer internship period: June–July (8 weeks minimum for B.Tech). "
                "Industrial training mandatory in 6th semester for engineering students. "
                "Placement drives: October–March."},

    {"id": "sch-006", "cat": "schedules", "title": "Workshop & Seminar Schedule",
     "content": "Technical workshops and seminars are held every month in collaboration with industry partners. "
                "Guest lectures scheduled every Friday. Students can register via the ERP portal."},

    # ══════════════════════════════════════════════════════
    # UNIVERSITY FACILITIES
    # ══════════════════════════════════════════════════════
    {"id": "fac-f-001", "cat": "facilities", "title": "Campus Overview",
     "content": "Chitkara University has two campuses: Rajpura (Punjab) and Baddi (Himachal Pradesh). "
                "Both are fully residential campuses with 24/7 facilities and smart infrastructure."},

    {"id": "fac-f-002", "cat": "facilities", "title": "Hostels",
     "content": "Separate hostels for boys and girls with 24/7 security. "
                "Rooms available: AC single, AC double, Non-AC double. "
                "Facilities: Wi-Fi, laundry, common room, TV room, gym. Warden available 24/7."},

    {"id": "fac-f-003", "cat": "facilities", "title": "Library",
     "content": "Central library with 1 lakh+ books, 500+ national/international journals, "
                "digital library access (IEEE, Springer, Elsevier). "
                "Open Monday–Saturday, 8 AM–10 PM. Study rooms available."},

    {"id": "fac-f-004", "cat": "facilities", "title": "Sports Facilities",
     "content": "Sports complex includes: cricket ground, football field, basketball court, "
                "badminton courts, volleyball court, table tennis, swimming pool, and indoor gymnasium. "
                "Professional coaches available. Inter-university sports competitions held annually."},

    {"id": "fac-f-005", "cat": "facilities", "title": "Medical Center",
     "content": "On-campus medical center with qualified doctors and nursing staff available 24/7. "
                "Free first aid and basic medical care for all students. "
                "Ambulance facility available for emergencies."},

    {"id": "fac-f-006", "cat": "facilities", "title": "Cafeteria & Food Court",
     "content": "Multiple cafeterias and food courts on campus serving veg and non-veg meals. "
                "Timing: Breakfast 7–9 AM, Lunch 12–2 PM, Snacks 4–6 PM, Dinner 7–9 PM. "
                "Hygienic FSSAI-certified food outlets."},

    {"id": "fac-f-007", "cat": "facilities", "title": "IT Infrastructure & Wi-Fi",
     "content": "Campus-wide high-speed Wi-Fi (1 Gbps backbone). Computer labs with 1000+ systems. "
                "24/7 internet access in hostels. VPN access for research resources."},

    {"id": "fac-f-008", "cat": "facilities", "title": "Transport Facility",
     "content": "University buses available from major cities: Chandigarh, Patiala, Ambala, Mohali. "
                "Bus timing: Morning pickup 7 AM, Evening drop 6 PM. "
                "Contact transport office for routes and fees."},

    {"id": "fac-f-009", "cat": "facilities", "title": "Auditorium & Conference Halls",
     "content": "Main auditorium with 2000-seat capacity for convocation, cultural events, conferences. "
                "Multiple seminar halls (50–300 seats) with projectors and AV equipment. "
                "Available for student club events and academic conferences."},

    {"id": "fac-f-010", "cat": "facilities", "title": "Bank & ATM",
     "content": "On-campus bank branch (Punjab National Bank) and multiple ATMs for cash withdrawals. "
                "Banking hours: Monday–Friday, 10 AM–4 PM."},

    # ══════════════════════════════════════════════════════
    # EVENTS
    # ══════════════════════════════════════════════════════
    {"id": "evt-001", "cat": "events", "title": "Annual Technical Fest — Innovision",
     "content": "Innovision is Chitkara University's annual technical festival held every February. "
                "Events include hackathons, robotics competitions, coding contests, project exhibitions, "
                "and guest lectures from industry leaders. Open to students from all universities."},

    {"id": "evt-002", "cat": "events", "title": "Cultural Fest — Utsav",
     "content": "Utsav is the annual cultural festival held in October/November. "
                "Events include music competitions, dance performances, drama, fashion show, "
                "art exhibitions, and celebrity performances. 3-day event."},

    {"id": "evt-003", "cat": "events", "title": "Sports Meet — Chitkara Premier League",
     "content": "Annual inter-department and inter-college sports competition held in January. "
                "Sports: cricket, football, basketball, badminton, chess, athletics. "
                "Students can register through the sports department."},

    {"id": "evt-004", "cat": "events", "title": "Convocation Ceremony",
     "content": "Annual convocation held in November for graduating students. "
                "Degrees awarded by Chancellor. Gold medals for top performers. "
                "Students must register for convocation through the ERP portal."},

    {"id": "evt-005", "cat": "events", "title": "Placement Drive",
     "content": "On-campus placement drives conducted October through March. "
                "Top recruiters: Google, Microsoft, Amazon, Infosys, TCS, Wipro, Cognizant, HCL. "
                "Students must register on the placement portal at least 1 month before."},

    {"id": "evt-006", "cat": "events", "title": "Workshops & Hackathons",
     "content": "Monthly technical workshops on AI, Cloud, Cybersecurity, Web Dev, etc. "
                "Semester-wise hackathons with cash prizes. "
                "Guest lectures by industry professionals every Friday afternoon."},

    {"id": "evt-007", "cat": "events", "title": "International Conferences",
     "content": "Chitkara University hosts international research conferences annually. "
                "ICCCT (Computing & Communication Technologies), ICBDA (Big Data Analytics). "
                "Students can submit research papers and present at conferences."},

    # ══════════════════════════════════════════════════════
    # ACADEMIC POLICIES
    # ══════════════════════════════════════════════════════
    {"id": "aca-001", "cat": "academic", "title": "Attendance Policy",
     "content": "Minimum 75% attendance required in every subject to appear in end-term exams. "
                "Medical leave considered with doctor's certificate. "
                "Attendance available on ERP portal. Students below 75% get detained (DT)."},

    {"id": "aca-002", "cat": "academic", "title": "CGPA & Academic Standing",
     "content": "CGPA is calculated on a 10-point scale. "
                "Minimum CGPA 5.0 required to continue in program. "
                "Academic probation for CGPA below 5.0. Distinction: CGPA 8.5+. First Division: CGPA 6.5+."},

    {"id": "aca-003", "cat": "academic", "title": "Project & Thesis Guidelines",
     "content": "Final year B.Tech project: 6th and 7th semester. Thesis for M.Tech/MBA. "
                "Students must form team of 2–4, select guide, and submit synopsis by October. "
                "Project evaluated by internal + external examiners."},

    {"id": "aca-004", "cat": "academic", "title": "Industrial Training",
     "content": "6-week industrial training mandatory for B.Tech students after 6th semester. "
                "Students must arrange internship themselves or through placement cell. "
                "Report submission and presentation mandatory. Graded as pass/fail."},

    {"id": "aca-005", "cat": "academic", "title": "Student ERP Portal",
     "content": "ERP portal (erp.chitkara.edu.in) is used for: course registration, fee payment, "
                "attendance tracking, result checking, timetable, exam schedule, and faculty contact. "
                "Login credentials provided at admission."},

    {"id": "aca-006", "cat": "academic", "title": "Anti-Ragging Policy",
     "content": "Chitkara University has strict zero-tolerance anti-ragging policy. "
                "Any form of ragging leads to immediate expulsion. "
                "24/7 anti-ragging helpline: 1800-180-5522. Anonymous complaints accepted."},

    {"id": "aca-007", "cat": "academic", "title": "Student Clubs & Societies",
     "content": "Active student clubs: Coding Club, Robotics Club, Entrepreneurship Cell (E-Cell), "
                "Literary Club, Music Club, Dance Society, Photography Club, NSS, NCC. "
                "Students can join or start clubs through student affairs office."},

    {"id": "aca-008", "cat": "academic", "title": "Research & Innovation",
     "content": "Students can apply for research internships under faculty. "
                "Chitkara Innovation and Incubation Centre (CIIC) supports student startups. "
                "Seed funding up to ₹5 lakhs for promising startups. IPR cell helps with patents."},

    # ══════════════════════════════════════════════════════
    # GENERAL
    # ══════════════════════════════════════════════════════
    {"id": "gen-001", "cat": "general", "title": "About Chitkara University",
     "content": "Chitkara University: established 2002 (Punjab), 2010 (HP). Private deemed university. "
                "NAAC A+ grade. NBA accredited programs. 25,000+ students. 500+ recruiting companies."},

    {"id": "gen-002", "cat": "general", "title": "Campus Locations",
     "content": "Two campuses: Rajpura, Punjab and Baddi, Himachal Pradesh. "
                "Both fully residential with smart classrooms, labs, hostels, sports, and medical center."},

    {"id": "gen-003", "cat": "general", "title": "Placements",
     "content": "500+ companies recruit from Chitkara: Google, Microsoft, Amazon, Infosys, TCS, Wipro, Cognizant. "
                "Average package: ₹6–8 LPA. Highest package: ₹45 LPA (2025). Dedicated placement cell."},

    {"id": "gen-004", "cat": "general", "title": "Rankings & Accreditations",
     "content": "NAAC A+ Grade. NBA accredited B.Tech programs. "
                "Ranked among top private universities in North India by NIRF. "
                "QS India Rankings listed university."},

    {"id": "gen-005", "cat": "general", "title": "University Contact",
     "content": "Main: +91-1723-980000. Admissions: admissions@chitkara.edu.in. "
                "Helpdesk: help@chitkara.edu.in. Website: www.chitkara.edu.in. ERP: erp.chitkara.edu.in."},
]


# ══════════════════════════════════════════════════════════
# PUBLIC FUNCTIONS
# ══════════════════════════════════════════════════════════
def get_all_chunks() -> List[Chunk]:
    """Return all knowledge as Chunk objects for RAG indexing."""
    return [
        Chunk(
            chunk_id=item["id"],
            category=item["cat"],
            title=item["title"],
            content=item["content"]
        )
        for item in _RAW_CHUNKS
    ]


def detect_category(query: str) -> str:
    """Lightweight category classifier — for history tagging only."""
    _KEYWORDS = {
        "courses":     ["course", "program", "degree", "btech", "b.tech", "mba", "bca",
                        "mca", "m.tech", "bachelor", "master", "engineering", "management"],
        "admissions":  ["admission", "apply", "eligibility", "document", "deadline",
                        "entrance", "jee", "cuet", "enroll", "registration"],
        "fees":        ["fee", "fees", "cost", "tuition", "hostel", "scholarship",
                        "payment", "charges", "how much", "emi", "waiver"],
        "exams":       ["exam", "schedule", "timetable", "mid term", "end term",
                        "result", "grade", "backlog", "supplementary", "attendance"],
        "faculty":     ["faculty", "professor", "teacher", "hod", "department",
                        "staff", "dean", "mentor", "instructor"],
        "departments": ["department", "dept", "school", "cse", "ece", "mechanical",
                        "civil", "pharmacy", "architecture", "bca dept", "applied science"],
        "schedules":   ["schedule", "timetable", "calendar", "holiday", "timing",
                        "class time", "registration date", "internship date", "workshop"],
        "facilities":  ["facility", "facilities", "hostel", "library", "sports",
                        "cafeteria", "food", "wifi", "transport", "bus", "medical",
                        "gym", "swimming", "auditorium", "atm", "bank"],
        "events":      ["event", "fest", "festival", "hackathon", "competition",
                        "convocation", "placement drive", "workshop", "seminar",
                        "innovision", "utsav", "sports meet", "conference"],
        "academic":    ["attendance", "cgpa", "project", "thesis", "internship",
                        "erp", "anti-ragging", "club", "society", "research",
                        "startup", "innovation", "patent", "probation"],
    }
    q = query.lower()
    best, best_score = "general", 0
    for cat, kws in _KEYWORDS.items():
        score = sum(1 for kw in kws if kw in q)
        if score > best_score:
            best_score, best = score, cat
    return best


def get_knowledge_context(query: str, category: str = None) -> str:
    """Kept for the no-AI fallback path in foundry.py."""
    if category is None:
        category = detect_category(query)
    chunks = [c for c in get_all_chunks() if c.category == category]
    if not chunks:
        chunks = get_all_chunks()
    return "\n\n".join(f"{c.title}:\n{c.content}" for c in chunks[:6])

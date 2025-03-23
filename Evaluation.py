from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import BleuScore, RougeScore
from ragas.metrics._string import NonLLMStringSimilarity, DistanceMeasure
import asyncio

# 从FAQ文档中提取的完整问题列表（英文问题+原文回答）
faq_pairs = [
    # General Advising
    {
        "question": "How should I prepare for my advising appointment?",
        "reference": """●	Part of your experience at DKU is developing a high-quality advisor-student relationship. Prior to meeting with your academic advisor, reflect/revise your short-term and long-term goals, consider your strengths and areas of growth from previous session(s), take time to review courses/major(s) of interest, identify 5-6 courses you want to discuss with your advisor (be flexible). It’s always a good idea to write down all the topics you want to go over in order to ensure you do not miss anything.
●	Schedule your appointment with your advisor at least a week in advance of registration and let them know if you already have specific questions you want to discuss. Finally, be open to having a constructive dialogue to set realistic expectations about your plan. 
●	You might what to use the 4-year plan to map out what courses you have taken and what you have left to complete your major requirement
""",
        "response": """Part of your experience at DKU is developing a high-quality advisor-student relationship. Prior to meeting with your academic advisor, reflect/revise your short-term and long-term goals, consider your strengths and areas of growth from previous session(s), take time to review courses/major(s) of interest, identify 5-6 courses you want to discuss with your advisor (be flexible). It’s always a good idea to write down all the topics you want to go over in order to ensure you do not miss anything.
Schedule your appointment with your advisor at least a week in advance of registration and let them know if you already have specific questions you want to discuss. Finally, be open to having a constructive dialogue to set realistic expectations about your plan.
You might want to use the 4-year plan to map out what courses you have taken and what you have left to complete your major requirement."""
    },
    {
        "question": "How can I find information about majors and academic policies?",
        "reference": """●	You may refer to the UG Bulletin, which can be found online at https://dukekunshan.edu.cn/en/registrar-office on the website of the Office of the Registrar. Be sure to keep using the Bulletin from the year you entered, newer versions may have requirements for new students that you will not be held to. 
●	To get a general sense of when courses are being offered, you can refer to the DKU Degree Course Planning Sheet, which can be found on the Office of Advising website at https://dukekunshan.edu.cn/en/academics/advising along with additional resources. 
""",
        "response": """According to the DKU FAQ provided in the conversation history, to find information about majors and academic policies, you may refer to the UG Bulletin, located on the Registrar’s Office Website. The UG Bulletin is a publication that indicates the majors available to a student and the policies that they must hold to. You can also refer to the DKU Degree Course Planning Sheet, which can be found on the Office of Advising website, along with additional resources."""
    },
    {
        "question": "How often should I meet with my advisor?",
        "reference": """●	You are required to meet with your advisor each semester before class registration and before you declare a major. Your advisor might arrange additional advising sessions throughout the semesters. You are also encouraged to be in touch with your advisor and reach out any time you have questions or concerns. """,
        "response": "You are required to meet with your advisor each semester before class registration and before you declare a major. Your advisor might arrange additional advising sessions throughout the semesters. You are also encouraged to be in touch with your advisor and reach out any time you have questions or concerns."
    },
    {
        "question": "Can I change my academic advisor?",
        "reference": """●	If you want a specific faculty to be your academic advisor, you should confirm it with both your current and potential advisor, reach an agreement, and then submit the request to the Office of Undergraduate Advising using the following link: https://dukekunshan.formstack.com/workflows/advisor_change_request_form 
●	As part of the steps, you wll be asked to complete a 4-year plan. This is for your new advisor to better understand your degree progress and for you two to discuss in your advising meetings. 
●	It is not guaranteed that the switch can be made for a faculty advisor who is at their advisee limit, even if they agree. All requests are subject to review by the Director of Academic Advising or their designee. 
""",
        "response": "If you want to change your academic advisor, you should confirm it with both your current and potential advisor, reach an agreement, and then submit the request to the Office of Undergraduate Advising using the following link: https://dukekunshan.formstack.com/workflows/advisor_change_request_form. As part of the steps, you’ll be asked to complete a 4-year plan. This is for your new advisor to better understand your degree progress and for you two to discuss in your advising meetings. It is not guaranteed that the switch can be made for a faculty advisor who is at their advisee limit, even if they agree. All requests are subject to review by the Director of Academic Advising or their designee."
    },

    # Declare or Change a Major
    {
        "question": "When can I declare a major?",
        "reference": """●	You may declare a major in the Spring term of your sophomore year. All students must secure formal approval of their long-range plans and declare a major no later than the last teaching day of the first seven-week session in their fourth semester.
●	Until that time, students should be exploring different options of majors to ensure that they are making the best choice for themselves. 
●	Students who do not declare their major may be prevented from registering for classes for their fifth undergraduate semester and from participating in a semester or study abroad program.
●	Information related to declaring your major will be provided in the 3rd 7-week session of the Sophomore year. Please refer to the Office of Undergraduate Advising if you have questions about the major declaration. 
""",
        "response": """According to the information provided in the Conversation History, you may declare a major in the Spring term of your sophomore year. All students must secure formal approval of their long-range plans and declare a major no later than the last teaching day of the first seven-week session in their fourth semester. Please note that you should explore different options of majors to ensure that you are making the best choice for yourself until then. Students who do not declare their major may be prevented from registering for classes for their fifth undergraduate semester and from participating in a semester or study abroad program."""
    },
    {
        "question": "What is the process for major declaration?",
        "reference": """●	Step 1: Prepare to declare by identifying an intended major and planning a pathway to graduation
●	Step 2: Advisor Meeting
●	Step 3: Major Declaration Application Form
""",
        "response": """The process for major declaration at Duke Kunshan University involves several steps:

Prepare to Declare: Before declaring a major, students should identify an intended major and plan a pathway to graduation. This involves consulting resources such as the UG Advising Resource Page and preparing materials such as a What-If Report and a Four-Year Plan.
Advisor Meeting: Students should meet with their advisor well before the declaration deadline to review and approve their What-If Report and Four-Year Plan. The advisor can also remove the Academic Advising Hold after reviewing both documents.
Major Declaration Application Form: Students should submit the Major Declaration Application Form, which can be found on the Registrar's website under 'Student Forms'.
It's worth noting that students who do not declare their major may be prevented from registering for classes for their fifth undergraduate semester and from participating in a semester or study abroad program."""
    },
    {
        "question": "Can I change my declared major?",
        "reference": """●	Yes, but before you do so, please refer to the UG Bulletin and the DKU Degree Requirement Sheet about the new major requirements and work out a new 4-year graduation plan. This kind of planning is to make sure that you can graduate on time.
●	The next step is to consult your academic advisor about the new major and your plan. 
●	After that, you can request to change your major by submitting a form to the Office of the University Registrar. Major Change Form may be found on the Registrar’s website under ‘Student Forms’ (https://www.dukekunshan.edu.cn/about/student-records-and-resources/).    
●	No changes in majors can be made after the end of the Drop/Add period of the first session of the Fall term in the senior year.
●	Every change of major request is subject to review and is not guaranteed approval.
""",
        "response": "Yes, you can change your declared major. Before doing so, please refer to the UG Bulletin and the DKU Degree Requirement Sheet about the new major requirements and work out a new 4-year graduation plan to ensure that you can graduate on time. The next step is to consult your academic advisor about the new major and your plan. After that, you can request to change your major by submitting a form to the Office of the University Registrar. Major Change Form may be found on the Registrar’s website under ‘Student Forms’ (https://www.dukekunshan.edu.cn/about/student-records-and-resources/). No changes in majors can be made after the end of the Drop/Add period of the first session of the Fall term in the senior year. Every change of major request is subject to review and is not guaranteed approval."
    },
    {
        "question": "Is there a specific order of courses by semester to graduate?",
        "reference": """●	No. Specific courses may not be offered in every session. Your exact pathway will depend on the courses offered in a particular semester, the pre-requisites you need to fulfill, your interests, and discussions with your advisor. Your goal should be to build your own pathway looking forward and make adjustments along the way with consideration to degree requirements. Counting as electives, courses outside major requirements can contribute to and enrich your college experience, learning, and understanding. """,
        "response": "There is no specific order of courses by semester that students must take to graduate. Your exact pathway will depend on the courses offered in a particular semester, the pre-requisites you need to fulfill, your interests, and discussions with your advisor. Your goal should be to build your own pathway looking forward and make adjustments along the way with consideration to degree requirements. Counting as electives, courses outside major requirements can contribute to and enrich your college experience, learning, and understanding."
    },

    # Curriculum
    {
        "question": "What are the core components of the DKU Curriculum?",
        "reference": """●	General Education 
○	3 Common Core Courses (12 credits)
○	2-4 Languages Courses (8-16 credits)
○	3 Courses as Distribution Requirements (12 credits)
○	1 Quantitative Reasoning Course (4 credits)
○	1 Writing Course (2 credits) *required for students admitted Fall 2023 and beyond*
●	Major
○	Divisional foundation courses
○	Interdisciplinary
○	Disciplinary
○	Signature work
●	Electives
●	Other requirements
○	1 non-credit mini-term
○	1 Signature work product
○	1 non-credit DKU 101 *required for students admitted Fall 2021 and beyond*
""",
        "response": """The core components of the DKU Curriculum include:

General Education
3 Common Core Courses (12 credits)
2-4 Languages Courses (8-16 credits)
3 Courses as Distribution Requirements (12 credits)
1 Quantitative Reasoning Course (4 credits)
1 Writing Course (2 credits) required for students admitted Fall 2023 and beyond
Major
Divisional foundation courses
Interdisciplinary
Disciplinary
Signature work
Electives
Other requirements
1 non-credit mini-term
1 Signature work product
1 non-credit DKU 101 required for students admitted Fall 2021 and beyond"""
    },
 
    {
        "question": "What are the Common Core courses?",
        "reference": """●	The common core courses provide opportunities for students to develop a degree of common knowledge and shared experience. They focus on big questions and critical challenges which every student should prepare to engage. They also focus on writing and speaking and aim to develop communication skills over time. The common core courses are :
○	GCHINA 101 - China In the World (Year 1)
○	GLOCHALL 201 - Global Challenges in Science, Technology, and Health (Year 2)
○	ETHLDR 201 - Ethics, Citizenship and the Examined Life (Year 3)
""",
        "response": """The Common Core courses are a set of core courses required of all students at Duke Kunshan University. These courses provide opportunities for students to develop a degree of common knowledge and shared experiences. The three common core courses are:

China in the World (Year 1)
Global Challenges in Science, Technology and Health (Year 2)
Ethics, Citizenship and the Examined Life (Year 3)
These courses must be taken during the designated year of study and must be taken in sequence, so that the common experience and development of communication skills extend across time. Completing the first two Common Core classes is an eligibility requirement for all study away."""
    },

    {
        "question": "What are the Distribution Requirements?",
        "reference": """●	The distribution requirement is intended to broaden students’ educational experience and ensure that all graduates have an acquaintance with a broad variety of knowledge fields. Students are required to take at least one 4-credit course in each of the three divisional areas:
○	Arts and Humanities (AH)
○	Natural and Applied Sciences (NAS)
○	Social Sciences (SS)
●	When searching for courses, you may specify the “Course Attribute” to “Division” in the search criteria, where you can further specify AH, NAS, or SS.
●	Please note that courses with two divisional attributes can only be counted towards one  area attribute. Put another way, you cannot use one class for two distribution requirements even if the course has both attributes.
""",
        "response": """The Distribution Requirements at Duke Kunshan University (DKU) are intended to broaden students' educational experience and ensure that all graduates have an acquaintance with a broad variety of fields of inquiry and approaches to knowledge.

According to the DKU Definitions (https://academic-advising.dukekunshan.edu.cn/dkudefinitions/), the distributional requirement is designed to ensure that students take at least one 4-credit course in each of the three divisional areas:

Arts and Humanities (AH)
Natural and Applied Sciences (NAS)
Social Sciences (SS)
Students can fulfill the distribution requirement in a divisional area by taking one four-credit or two two-credit courses with that divisional area attribute. When searching for courses, students may specify the "Course Attribute" to "Division" in the search criteria, where they can further specify AH, NAS, or SS."""
    },

    {
        "question": "What is the Quantitative Reasoning Requirement?",
        "reference": """●	The Quantitative Reasoning (QR) requirement aims to ensure that all students graduate with critical skills in quantitative analysis and deductive reasoning. 
●	QR requirement can be fulfilled by taking a course with QR attribute or by approved transfer credit from study abroad or summer programs for computer science, mathematics, or statistics courses.
●	QR requirements can also be fulfilled by AP or IPC credits. More detailed information on qualified AP or IPC credits can be found in the Quantitative Reasoning Course Requirement section of the UG Bulletin.
""",
        "response": """The Quantitative Reasoning (QR) requirement is a requirement for all students at Duke Kunshan University. The QR requirement aims to ensure that all students graduate with critical skills in quantitative analysis and deductive reasoning. This requirement can be fulfilled by taking a course with the Quantitative Reasoning (QR) attribute or by approved transfer credit from study abroad or summer programs for computer science, mathematics, or statistics courses. Transfer credit requires the review and approval from the appropriate division chair to fulfill the distributional requirement. The QR requirement cannot be fulfilled by AP or IPC credits."""
    },
    
    {
        "question": "What are the required language courses?",
        "reference": """●	8 to 16 credits of language courses are required for all students. All students will be assigned to EAP (English for Academic Purposes) Track or CSL (Chinese as a Second Language) Track based on students’ secondary education’s language medium.
●	For the EAP track, students are required to take EAP 101A,101B, and EAP 102A, 102B. WOC is available for students to develop advanced English writing and oral communication skills.
●	For the CSL track, students without any previous Chinese training are required to take CHINESE 101,102, 201, and 202. Students who have previous Chinese knowledge and are placed in a higher level Chinese class still need to take 8 credits of Chinese classes starting with and including whatever level course they are placed into. That is to say, students who begin their Chinese study in CHINESE 101A are required to take Chinese courses until they complete CHINESE 202B; students who begin studying Chinese in CHINESE 201A or a higher level course are required to take 8 credits, starting with and including whatever level course they are placed into. 
""",
        "response": """The required language courses at Duke Kunshan University are subject to the EAP (English for Academic Purposes) Track or CSL (Chinese as a Second Language) Track, depending on the student's secondary education language medium. Here is a breakdown of the required language courses for each track:

EAP Track:
EAP 101A and 101B
EAP 102A and 102B
WOC (Written and Oral Communication) courses for advanced English writing and oral communication skills
CSL Track:
CHINESE 101, 102, 201, and 202 for students without previous Chinese training
For students with previous Chinese knowledge, they are required to take 8 credits of Chinese classes, starting with the course they are placed into, until they complete CHINESE 202B"""
    },
    {
        "question": "What’s Duke 34? How many credits must I earn from courses taught by Duke faculty and what are my options for doing so?",
        "reference": """●	All students must earn 34 credits from courses taught or co-taught by Duke faculty. These courses can be taken at DKU as well as at Duke. Courses with a course attribute of Duke Instructor (DINS) are approved for this requirement. Depending on whether a student studies at Duke, there are 2 possible options for completing the Duke credit requirement:
○	Option A: Semester (16 credits) at Duke + 18 credits at DKU over 4 years
○	Option B: 34 credits at DKU over 4 years (take courses with DINS code).
●	A majority of students complete the Duke 34 without 
""",
        "response": """Duke 34 refers to the requirement for students to earn 34 credits from courses taught or co-taught by Duke faculty. These credits can be earned by taking courses at DKU or at Duke University. There are two possible options for completing the Duke credit requirement:

Option A: Semester (16 credits) at Duke + 18 credits at DKU over 4 years
Option B: 34 credits at DKU over 4 years (take courses with DINS code)"""
    },
    {
        "question": "What are the additional requirements for Mainland Chinese and HMT students?",
        "reference": """●	Additional requirements by the Ministry of Education of China for Mainland Chinese and HMT students are the following:
○	16 credits of Chinese Society and Culture (CHSC) courses.
○	8 credits of PE course.
○	2 credits (Class of 2022) / 4 credits (Class of 2023 and Beyond) of Military Training.
■	*Note that HMT students may substitute the military training credits with credits from specific designated Chinese studies courses.
○	Passing the physical proficiency test set by the Ministry of Education of China.
""",
        "response": """According to the DKU Student Handbook and the UG Bulletin, the additional requirements for Mainland Chinese and HMT students are:

Chinese Society and Culture (CHSC) courses: These credits cannot be counted toward the 136 credit requirement, but they may be counted toward the additional credit requirements for students from the Chinese mainland, Hong Kong, Macau, and Taiwan.
Military training: HMT students may substitute the military training credits with credits from specific designated Chinese studies courses.
Passing the physical proficiency test set by the Ministry of Education of China.
Additional CHSC courses: CHSC 101, CHSC 102, CHSC 104, and CHSC 105 are compulsory courses for all Chinese mainland and HMT students. CHSC 106 and CHSC 107 are elective courses offered for HMT students who need to take extra CHSC courses to replace the military training credits."""
    },
    {
        "question": "Can I take the Chinese Society and Culture courses as an international student?",
        "reference": """●	Yes. CHSC courses are optional for international students. Students should note that the Chinese Society and Culture courses are taught in Chinese and do not count toward the 136 credits for the DKU degree. """,
        "response": """Yes, international students can take the Chinese Society and Culture courses. CHSC courses are optional for international students, and students should note that they are taught in Chinese and do not count toward the 136 credits for the DKU degree. A total of 136 Duke Kunshan University credits is required for international students to graduate and obtain the degrees, inclusive of 34 Duke Kunshan University credits earned through courses taught or co-taught by Duke faculty."""
    },
    {
        "question": "How many courses from foundations, interdisciplinary, and disciplinary studies should I have taken by the end of Year 2 to stay on track for completing a major? ",
        "reference": """●	Although you may still be exploring and do not plan to declare your major until the Spring of your sophomore year, you should consult with your advisor to plan ahead. While there is no specific course or credit requirement that must be completed prior to declaring your major in your sophomore year, be mindful of course sequencing when considering your major pathway to stay on track to graduation. 
●	If you are interested in Arts and Humanities and Social Sciences majors, you should plan to complete the 2 divisional foundation courses and 5-6 (100-200 level) disciplinary or interdisciplinary major courses by the end of your sophomore year. 
●	If you are interested in Natural and Applied Sciences majors, you should plan to complete the 5 divisional foundation courses plus any remaining 100-level and most or all of the 200-level disciplinary and interdisciplinary major courses by the end of the sophomore year.
●	You can refer to the Course Planning Sheet for more information/suggestions on course sequencing. 
○	Class of 2025 and before _ Course Planning Sheet
○	Class of 2026 and Beyond _ Course Planning Sheet
""",
        "response": """Based on the DKU Bulletin, by the end of Year 2, students should have taken the following courses:

Divisional Foundation Courses: 2-4 courses (8-16 credits)
Interdisciplinary Studies: 4-7 courses (16-28 credits)
Disciplinary Studies: 4-8 courses (16-32 credits)
Note that the exact number of courses and credits may vary depending on the student's major and academic plan. It is recommended that students consult with their advisor to determine their individual course sequence and ensure they are on track to complete their major requirements."""
    },
     #Course Registration:
    {
        "question": "How to search for courses based on distribution requirements (attributes)?",
        "reference": """●	 To search for classes with the attribute:
○	1. Navigate to Class search (Student Service - Academics - Search)
○	2. Enter the following Search Criteria:
■	a. Desired term (for example, 2024 Fall Term)
■	b. Course Career: Undergraduate
■	c. Course Attribute: Curriculum
■	d. Course Attribute Value: Quantitative Reasoning, AH, NS, SS
○	3. Unselect “show open classes only”
○	4. Hit the search button
●	Note: According to the 2023-24 Bulletin, courses with two divisional area attributes can only be counted as one area attribute; Courses with both a QR and divisional area attribute can only be counted as one of these areas.
""",
        "response": """To search for classes with specific attributes, follow these steps:

Navigate to the Class search tool in the Student Service section of the website.
Enter the following Search Criteria:
Desired term (e.g., 2024 Fall Term)
Course Career: Undergraduate
Course Attribute: Curriculum
Select the desired attribute from the drop-down menu.
Click on the "Search" button to view the list of classes that match your search criteria.
You can then filter the results by other criteria, such as course name or instructor, to find the class that best fits your needs.
For example, if you want to search for classes with the attribute "Arts and Humanities", you would follow these steps:

Navigate to the Class search tool.
Enter the following Search Criteria:
Desired term: 2024 Fall Term
Course Career: Undergraduate
Course Attribute: Arts and Humanities
Select "Arts and Humanities" from the drop-down menu.
Click on the "Search" button to view the list of classes that match your search criteria."""
    },
    {
        "question": "How do I find the courses taught by Duke Instructor (with DINS code)?",
        "reference": """To search for classes with DINS code:
○	1. Navigate to Class search (Student Search - Academics - Search)
○	2. Enter the following Search Criteria:
■	a. Desired term (for example, 2024 Fall Term)
■	b. Course Career: Undergraduate
■	c. Requirement Designation: Duke Instructor.
○	3. Unselect “show open classes only”
○	4. Hit the search button
""",
        "response": """According to the DKU website, you can search for classes with DINS code by following these steps:

Navigate to Class search (Student Service - Academics - Search)
Enter the following Search Criteria: a. Desired term (for example, 2024 Fall Term) b. Course Career: Undergraduate c. Course Attribute: Curriculum and then select Duke Instructor (DINS code)
For precise details, including policy exceptions, please refer to the Registration section in Part 6 of the UG Bulletin."""
    },
    {
        "question": "Why do I have a ‘Hold’ in my account?",
        "reference": """●	The Academic Advising Hold is in place to ensure that you are meeting with your academic advisor to make quality decisions related to your academic plans. A Hold will temporarily block you from enrolling in classes; once you have met with your advisor, the Hold will be removed and you can then register for classes. 
●	Be sure to reach out to your advisor at least one week prior to registration and schedule a meeting. 
●	Other Holds including Bursar Hold, Registration Hold, Signature Work Hold, and Pathway to Success Hold are placed for different reasons. You can view detailed information by clicking on the Hold and you may contact the corresponding offices for questions.
""",
        "response": """If you have an 'Hold' in your account, it is likely due to an Academic Advising Hold. This hold is placed to ensure that you are meeting with your academic advisor to make quality decisions related to your academic plans. A hold will temporarily block you from enrolling in classes; once you have met with your advisor, the hold will be removed and you can then register for classes."""
    },
    {
        "question": "Can I make changes to my course schedule after registration?",
        "reference": """●	Yes. You may drop and add courses during the Drop/Add period. Courses dropped during this period do not appear on the official Duke Kunshan transcript. 
●	After the Drop/ Add period, no courses may be added, but you may still withdraw from a class with the permission of your academic advisor. Courses withdrawn will receive a designation of W on academic record. For more information about course withdrawal, please refer to the Registration section on UG Bulletin. 
""",
        "response": """Yes, you may make changes to your course schedule after registration. You can drop and add courses during the Drop/Add period. Courses dropped during this period do not appear on the official Duke Kunshan transcript. After the Drop/Add period, no courses may be added, but you may still withdraw from a class with the permission of your academic advisor. Courses withdrawn will receive a designation of W on your academic record."""
    },
    {
        "question": "Who should I consult if I have concerns related to my registration? ",
        "reference": """●	This depends on the question or concern. Students should consult the Office of the Registrar at DKU-registrar@dukekunshan.edu.cn if they want to celebrate, voice concerns, or have questions related to the registration process or if they have trouble with SIS.
●	If the question is policy related you can reach out to Academic Advising at advising@dukekunshan.edu.cn.
●	For questions about whether or not a class is working for a student’s degree please see your academic advisor or view your Advising Report/What-if Report  in SIS. 
""",
        "response": """According to the DKU Undergraduate Bulletin, if you have concerns related to your registration, you should consult the Office of the Registrar at DKU-registrar@dukekunshan.edu.cn or Academic Advising at advising@dukekunshan.edu.cn, depending on whether your question is related to the registration process or policy."""
    },
    #Course Load
    {
        "question": "How many credits can I take in a semester?",
        "reference": """●	The normal course load is 16-20 credits per semester (8-10 credits in each 7-week session). 
●	As freshman, you are required to enroll in a maximum of 8 credits for the first session of your first semester.
●	In addition, you may enroll in up to one credit of PE courses without special permission from your advisor.
●	You should be reminded that it is your responsibility to be certain that the courses selected and overall load is aligned with academic requirements. For detailed information on course load, please see the Undergraduate Course Load section of the UG Bulletin.
""",
        "response": """The normal course load at Duke Kunshan University is 16-20 credits per semester (8-10 credits in each 7-week session). As a freshman, you are required to enroll in a maximum of 8 credits for the first session of your first semester. Additionally, you may enroll in up to one credit of PE courses without special permission from your advisor. However, students on academic probation may register for no more than 16 credits plus one PE course."""
    },
    {
        "question": "How many credits can I take in a semester if I’m on academic probation?",
        "reference": """●	Students on academic probation may register for no more than 16 credits plus one PE course. """,
        "response": """According to the Undergraduate Course Load section in Part 6 of the UG Bulletin, students on academic probation may register for no more than 16 credits plus one PE course. This means that if you are on academic probation, you can take a maximum of 16 credits, plus one credit of PE courses, in a semester."""
    },
    {
        "question": "What is a course overload and how can I request for an overload?",
        "reference": """●	Overload is defined as enrolling in more than 10 credits in a 7-week session or more than 20 credits in a semester, exclusive of PE, up to 24 credits.
●	Request form can be found on the Registrar’s Website under student forms. Students need special permission from both their academic advisor and the Dean of Academic Services’ Office to enroll in an overload. 
""",
        "response": """"""
    },
    {
        "question": "What is a course underload?",
        "reference": """●	A course load between 12 and 15 credits is considered a course underload. There are two categories of underload: withdrawal to underload (when a course is withdrawn) and enrollment to underload (when you never signed up for 16 hours to begin with). 
●	The maximum number of underloads is two-semester (medical withdrawals are not counted in this number), and there are only two possible enrollment scenarios involving 2 underloads:
○	One withdrawal to an underload plus one enrollment in an underload, or
○	Two enrollments in an underload.
●	Seniors needing only 3 courses to graduate may request an part-time degree status  for their last semester and it is not affected by the underload policies described here.
""",
        "response": """A course overload is defined as enrolling in more than 10 credits in a 7-week session or more than 20 credits in a semester, exclusive of PE, up to 24 credits. To request for an overload, you need special permission from both your academic advisor and the Dean of Academic Services' Office. You can find the request form on the Registrar's Website under student forms."""
    },
    {
        "question": "What should I be aware of about the course underload?",
        "reference": """●	An underload may affect a student’s scholarship or ability to graduate on time.
●	Students taking an underload will be ineligible for the Dean’s list and the Dean’s list with Distinction during that semester.
●	You should not count on an overload later to compensate for a previous underload.
""",
        "response": """You should be aware of the following when considering a course underload:

A course underload may affect your scholarship or ability to graduate on time.
Students taking an underload will be ineligible for the Dean's list and the Dean's list with Distinction during that semester.
You should not count on an overload later to compensate for a previous underload.
To enroll in an underload, you must meet the following minimum criteria for eligibility:
Have a declared major
Have a GPA of at least 3.0 and not be on academic probation
Be enrolled on campus at Duke Kunshan University – enrolling in an underload is not permitted when you are studying away or otherwise away from Duke Kunshan University
For a first underload term: have already passed at least 64 credits
There are only two possible enrollment scenarios involving 2 underloads:
One withdrawal to an underload plus one enrollment in an underload, or
Two enrollments in an underload.
Seniors needing only 3 courses to graduate may request a part-time degree status for their last semester and it is not affected by the underload policies described here."""
    },
    {
        "question": "How can I enroll/ withdraw to an underload?",
        "reference": """●	Request form can be found on the Registrar’s Website under student forms. Students need special permission from both their academic advisor and the Dean of Academic Services to enroll in an underload.
●	For the specific policies and criteria on the underloads, please refer to the UG Bulletin sections titled Underload, Withdrawing to an Underload, and Enrollment in an Underload. 
""",
        "response": """To enroll/ withdraw to an underload, you need to request a form from the Registrar's Website under student forms. You will need special permission from both your academic advisor and the Dean of Academic Services to enroll in an underload. The maximum number of underloads is two-semester (medical withdrawals are not counted in this number), and there are only two possible enrollment scenarios involving 2 underloads: one withdrawal to an underload plus one enrollment in an underload, or two enrollments in an underload.

If you are withdrawing from a class after the Drop/Add period, you must first obtain permission from your academic advisor. You can then withdraw from a class by submitting a Course Withdrawal Form, which can be found on the Registrar's Website, under Student Records and Resources.

Please note that withdrawal to an underload (fewer than 16 hours) is only permitted once. For specific policies and criteria on the underloads, please refer to the UG Bulletin sections titled Underload, Withdrawing to an Underload, and Enrollment in an Underload."""
    },
    #Course Withdrawal
    {
        "question": "How can I withdraw from a class?",
        "reference": """●	To withdraw from a class after the Drop/Add period, you must first obtain permission from your academic advisor. 
●	Then you can withdraw from a class by submitting a Course Withdrawal Form, which can be found on the Registrar’s Website, under Student Records and Resources.
●	Withdraw from a class is permitted in multiple Fall/ Spring semesters, as long as a course load of 16 credits is maintained. 
●	Withdrawal to an underload (fewer than 16 hours) is only permitted once.
""",
        "response": """To withdraw from a class, you must first obtain permission from your academic advisor. Then, you can withdraw from a class by submitting a Course Withdrawal Form, which can be found on the Registrar's Website, under Student Records and Resources.

Withdraw from a class is permitted in multiple Fall/Spring semesters, as long as a course load of 16 credits is maintained. Withdrawal to an underload (fewer than 16 hours) is only permitted once.

The deadline for requesting withdrawal from a course in a Fall/Spring semester is four weeks prior to the last day of classes for fourteen-week courses and two weeks prior to the last day of classes for seven-week courses. You can refer to the Academic Calendar for the withdraw deadline date.

The deadline applies to course withdrawals for any reason other than medical.

For more information, please refer to the UG Bulletin sections titled Withdrawal from a course, Withdrawal to an Underload, and Medical Withdrawal from a course."""
    },
    {
        "question": "Will courses that I withdrew show on my transcript?",
        "reference": """●	Yes, such courses receive a designation of W on the your academic record.""",
        "response": """Courses that you withdrew show on your transcript with a designation of W."""
    },
    {
        "question": "When is the deadline to withdraw from a class?",
        "reference": """●	The deadline for requesting withdrawal from a course in a Fall/ Spring semester is four weeks prior to the last day of classes for fourteen-week courses and two weeks prior to the last day of classes for seven-week courses. You can refer to the Academic Calendar for the withdraw deadline date. 
●	The deadline applies to course withdrawals for any reason other than medical.
""",
        "response": """The deadline for requesting withdrawal from a course in a Fall/Spring semester is four weeks prior to the last day of classes for 14-week courses and two weeks prior to the last day of classes for 7-week courses. You can refer to the Academic Calendar for the withdraw deadline date. The deadline applies to course withdrawals for any reason other than medical."""
    },
    #CR/NC Grading System
    {
        "question": "What is the procedure of CR/NC a course?",
        "reference": """●	After getting approval from your advisor, you can file a form with the Registrar to request changing the grading basis to CR/NC. 
●	The CR/NC form can be found on the DKU Registrar’s website under Student Records and Resources.
●	Note that once you have notified the registrar to change the grading basis to CR/NC, you may not change it back to a regular grade, please see the detailed policy in the UG bulletin.
""",
        "response": """To CR/NC a course, you need to follow these steps:

Get approval from your advisor.
File a form with the Registrar to request changing the grading basis to CR/NC. The form can be found on the DKU Registrar’s website under Student Records and Resources.
Note that once you have notified the registrar to change the grading basis to CR/NC, you may not change it back to a regular grade. Please see the detailed policy in the UG bulletin."""
    },
    {
        "question": "What letter grade would be considered CR and what would be considered NC?",
        "reference": """●	If you received a grade of C- or better in the course, you’ll receive a CR (Credit).
●	If you received a grade of D+ or below in the course, you’ll receive an NC (No Credit).
""",
        "response": """According to the UG Bulletin, a grade of C- or better in the course will be considered a CR (Credit), and a grade of D+ or below in the course will be considered an NC (No Credit)."""
    },

    #Incomplete Grade
    {
        "question": "When do I get assigned an Incomplete (I) grade?",
        "reference": """●	If, because of illness, emergency, or circumstances outside your reasonable control, you cannot complete work for a course or cannot attend the final examination, you may request in writing to the instructor the assignment of an I (incomplete) for the course.
●	An incomplete grade will not be authorized if the student has a history of excessive absences or failure to coursework in a timely fashion. 
""",
        "response": """According to the section "Incomplete Grade," an I grade is assigned when a student requests it in writing to the instructor due to illness, emergency, or circumstances outside their reasonable control. The specific timing of when the I grade is assigned is not explicitly stated in this section, but it is mentioned that the student must satisfactorily complete the work by the last class day (Thursday) of the fifth week of the subsequent regular session, except when an earlier deadline has been established by the instructor."""
    },
    {
        "question": "What’s the regular deadline for resolving the Incomplete grade?",
        "reference": """●	You must satisfactorily complete the work by the last class day (Thursday) of the fifth week of the subsequent regular session except when an earlier deadline has been established by the instructor.
●	An earlier deadline might be established when you apply to study abroad. 
●	An I grade assigned in the summer must be resolved in the succeeding fall term. 
●	Please see the UG bulletin for detailed information on Incomplete Coursework.
""",
        "response": """
According to the Incomplete Grade policy, you must satisfactorily complete the work by the last class day (Thursday) of the fifth week of the subsequent regular session except when an earlier deadline has been established by the instructor."""
    },

    {
        "question": "What happens if I fail to resolve the Incomplete grade by the deadline?",
        "reference": """●	If the I is not completed by the deadline, it will convert to an F and be reported to the Office of Registrar. """,
        "response": """If you fail to resolve the Incomplete grade by the deadline, it will convert to an F and be reported to the Office of Registrar."""
    },
    #Course Repeat
    {
        "question": "What is the process for repeating a course?",
        "reference": """●	Students who failed the course (F, NC) need permission from their academic advisor; Students who received a passing grade (C-, D+, D, D-) for the course but who wish to repeat it to improve that grade and their GPA may do so only with permission from both their academic advisor and the Dean of Undergraduate Studies. 
●	To process the course retake, a Course Repeat Form needs to be filled out. The form can be found on the Registrar’s Website under Student Formshttps://www.dukekunshan.edu.cn/about/student-records-and-resources/.
●	The detailed Course Repeat policy can be found in the UG bulletin. 
""",
        "response": """According to the DKU FAQ, the process for repeating a course is as follows:

Students who failed the course (F, NC) need permission from their academic advisor; Students who received a passing grade (C-, D+, D, D-) for the course but who wish to repeat it to improve that grade and their GPA may do so only with permission from both their academic advisor and the Dean of Undergraduate Studies.

To process the course retake, a Course Repeat Form needs to be filled out. The form can be found on the Registrar’s Website under Student Forms https://www.dukekunshan.edu.cn/about/student-records-and-resources/.

The detailed Course Repeat policy can be found in the UG bulletin."""
    },
    {
        "question": "Can I repeat a course with a CR grade?",
        "reference": """●	A student may NOT repeat a course for which the grade of the record is CR, regardless of what the original grade was. 
●	If the student chooses to appeal they should appeal in writing to their academic advisor, who will make a recommendation to the Dean of Undergraduate Studies, whose decision is final.
""",
        "response": """According to the information provided, a student may NOT repeat a course for which the grade of the record is CR, regardless of what the original grade was."""
    },
    {
        "question": "Can I repeat a DKU course at Duke University?",
        "reference": """●	In rare cases and only by petition to the Dean of Undergraduate Studies, a student might be permitted to repeat a Duke Kunshan course at Duke University.""",
        "response": """
Yes, in rare cases and only by petition to the Dean of Undergraduate Studies, a student might be permitted to repeat a Duke Kunshan course at Duke University. However, such requests will only be considered if there is an equivalent course offered at both universities.

According to the UG Bulletin, students are permitted to repeat courses they’ve taken at Duke Kunshan University in which they have received a grade of C- or below. However, a course may be repeated only at Duke Kunshan University, with rare exceptions. The bulletin also states that students who failed a course need permission from their academic advisor before registering for the same course a second time.

To repeat a course, students must submit an appeal in writing to their assigned academic advisor explaining the purpose of repeating the course and outlining a plan of study, including a plan to seek help from either the professor and/or the advisor."""
    },

    #Global Education and Study Abroad
    {
        "question": "Who is eligible for Study Abroad?",
        "reference": """●	Students must be in good academic, conduct, and financial standing in order to study away. Students placed on academic or conduct probation that will be in effect during their planned term away are not eligible to study away. 
●	Students accepted into study away programs who are then placed on academic or conduct probation may be liable for the program costs, even if they withdraw from the program. 
●	Students should refer to the "DKU Global Education Website" for complete eligibility requirements. Students who do not meet the eligibility requirements may not study away.
""",
        "response": """
According to the DKU Global Education website, students who are in good academic, conduct, and financial standing are eligible for study abroad. Specifically, students must apply and receive preapproval to participate in any credit-bearing study away opportunities through the Office of Global Education. Additionally, students who are on academic suspension, leave of absence, or probation may not study away during the terms of their suspension or probation. It is recommended to refer to the DKU Global Education website for complete eligibility requirements."""
    },
    {
        "question": "Is there a minimum GPA requirement to participate in the Study Abroad Program?",
        "reference": """●	As long as students are in good academic standing, there is no minimum GPA requirement for the Duke University and Duke Marine Lab programs.
●	For detailed Eligibility Guidelines for Study Abroad, please refer to the DKU Global Education website.
""",
        "response": """According to the Office of Global Education, there is no minimum GPA requirement for the Duke University and Duke Marine Lab programs. However, students must be in good academic, conduct, and financial standing to study away. For detailed Eligibility Guidelines for Study Abroad, please refer to the DKU Global Education website."""
    },
    {
        "question": "When is the deadline to apply for Study Abroad?",
        "reference": """●	Application timeline can be found on the DKU Global Education Website. s""",
        "response": """To answer your question, the deadline to apply for Study Abroad can be found on the DKU Global Education Website. According to the information provided on the website, the application timeline for semester study away programs starts in the fall term of the sophomore year. However, the exact deadline may vary depending on the program and the student's eligibility.

For precise details, including policy exceptions, please provide keywords like your academic year or major. You can also refer to the DKU Global Education Website for the most up-to-date information on advising for global learning experiences, preapproved program lists, application processes, and credit-transfer processes."""
    },
    {
        "question": "Who provides advising and support for me when I’m studying abroad at Duke?",
        "reference": """●	Prior to your arrival at Duke, DKU students work with the assigned DKU academic advisors and the Duke Office of DKU Relations to plan your academic experience and complete course registration. 
●	While at Duke, DKU students continue to be supported by DKU academic advisors and Duke Office of Duke Kunshan University Relations. Students may contact the office at dkurelations@duke.edu, contact the Duke’s Academic Dean for DKU Students at liguo.zhang@duke.edu, or stop by at Suite 214, Flowers Building, 404 Chapel Drive, Durham.
●	More information can be found on the Duke Office of Duke Kunshan University Relations website.
""",
        "response": """According to the Office of Global Education and Study Abroad, prior to their arrival at Duke, DKU students work with the assigned DKU academic advisors and the Duke Office of DKU Relations to plan their academic experience and complete course registration. While at Duke, DKU students continue to be supported by DKU academic advisors and Duke Office of Duke Kunshan University Relations. Students may contact the office at dkurelations@duke.edu, contact the Duke’s Academic Dean for DKU Students at liguo.zhang@duke.edu, or stop by at Suite 214, Flowers Building, 404 Chapel Drive, Durham."""
    },
#     {
#         "question": "Where can I find the Duke/ DKU equivalencies courses?",
#         "reference": """●	Course equivalencies can be found at the DKU Global Education Website under Prepare – Duke-DKU Credit Transfer.""",
#         "response": """"""
#     },
#     {
#         "question": "Where can I find the Duke/ DKU equivalencies courses?",
#         "reference": """●	Course equivalencies can be found at the DKU Global Education Website under Prepare – Duke-DKU Credit Transfer.""",
#         "response": """"""
#     },
#     {
#         "question": "How do I submit a Course Equivalency Request?",
#         "reference": """●	If you think a Duke course can be equivalent to a DKU course you may submit a course equivalency request to the Office of Global Education to have it reviewed. 
# ●	Instruction can be found at  DKU Global Education Website under Prepare – Duke-DKU Credit Transfer.
# """,
#         "response": """"""
#     },
    #Leave of Absence(LOA):
    {
        "question": "How do I request a Personal Leave of Absence?",
        "reference": """●	You must be in good academic standing and have completed one semester at DKU in order to request an LOA.
●	First you must consult with your family or guardian to get their approval.
●	You can then request a personal leave of absence by completing a leave of absence request form and submitting it to the Office of Undergraduate Studies prior to the first day of classes of the term in which the leave is granted. 
●	The leave of absence request form can be found on the Registrar’s Office at https://dukekunshan.edu.cn/en/registrar-office/student-records. 
""",
        "response": """"""
    },
    {
        "question": "Can I request a Leave of Absence for military service?",
        "reference": """●	Yes. Students called to a military service can request a leave of absence as early as the first term in the freshmen year. 
●	If the leave of absence starts from the first term in their freshmen year, students should first complete all the new student registration procedures before applying for a leave of absence.
""",
        "response": """"""
    },
    {
        "question": "How do I request a Medical Leave of Absence?",
        "reference": """●	A medical leave of absence request can be granted at any time with proper medical documentation and a leave of absence request form. 
●	You must provide a diagnosis from a Level II hospital or above or a recommendation from a licensed psychological counselor to the Campus Health Services and Counseling and Psychological Services.
●	For physical health reasons:
○	If you received treatment at the DKU Clinic, the attending physician should fill in the Healthcare Provider's Recommendation Form for you to submit, along with your LOA application form, to UG Studies.
○	External healthcare providers will complete the Medical Leave of Absence: External Healthcare Provider’s Recommendation Form.
●	For mental health reasons:
○	If you received a course of treatment at DKU CAPS, your therapist will fill out the Healthcare Healthcare Provider's Recommendation Form (if the therapist supports the student’s MLOA) for the student to submit, along with your LOA application form, to Academic Services.
○	External healthcare providers will complete the Medical Leave of Absence: External Healthcare Provider’s Recommendation Form.
●	The leave of absence request form can be found on the Registrar’s Office at https://dukekunshan.edu.cn/en/registrar-office/student-records. 
""",
        "response": """"""
    },
    {
        "question": "How long can I be on Leave of Absence?",
        "reference": """●	A personal leave of absence can be one or two semesters. 
●	A Medical leave of absence may have a different duration depending on the circumstances. Please remain in contact with your academic advisor and the advising office (advising@dukekunshan.edu.cn) to inform them of any updates.
""",
        "response": """"""
    },
    {
        "question": "How long can I be on Leave of Absence?",
        "reference": """●	A personal leave of absence can be one or two semesters. 
●	A Medical leave of absence may have a different duration depending on the circumstances. Please remain in contact with your academic advisor and the advising office (advising@dukekunshan.edu.cn) to inform them of any updates.
""",
        "response": """"""
    },
    {
        "question": "Can I take classes at different universities while I’m on Leave of Absence?",
        "reference": """●	Yes. You may receive transfer credit for no more than two courses (for a total of 8 DKU credits) taken at another accredited four-year institution in the US or similarly accredited institution abroad and with liberal arts and general education curriculum while on leave of absence for personal or medical reasons. """,
        "response": """"""
    },
    {
        "question": "How long can I be on Leave of Absence?",
        "reference": """●	A personal leave of absence can be one or two semesters. 
●	A Medical leave of absence may have a different duration depending on the circumstances. Please remain in contact with your academic advisor and the advising office (advising@dukekunshan.edu.cn) to inform them of any updates.
""",
        "response": """"""
    },
    {
        "question": "How do I return from Leave of Absence?",
        "reference": """●	You must submit a Return from Leave of Absence Application and receive approval in order to return from any type of leave of absence, including suspension or involuntary leave of absence.
●	The Return from Leave of Absence Application form can be found on the Registrar’s Office Website.
●	The deadlines for this application, including all supporting materials, are 5:00 p.m. May 1 (BJT) for Fall Semester and 5:00 p.m. October 1 (BJT) for Spring Semester. Late or incomplete applications will not be accepted.
●	Please note that if you are returning from a medical leave of absence, you will be asked to provide additional medical documentation for application for re-admissions. 
●	For more information, please refer to the UG Bulletin “Leave of Absence” section and Guide for Taking a Leave of Absence document. This document is updated once an academic year.
""",
        "response": """"""
    },
    {
        "question": "Will taking a Leave of Absence affect my financial aid?",
        "reference": """●	If you are a Chinese student, contact china-finaid@dukekunshan.edu.cn.
●	If you are an international student, contact international-finaid@dukekunshan.edu.cn. 
""",
        "response": """"""
    },
    #Academic Standing
    {
        "question": "What is considered good academic standing?",
        "reference": """●	Regardless of the GPA, students are considered in good academic standing when they are not placed in Academic Warning or Academic Probation and do meet the Academic Continuation requirements. """,
        "response": """"""
    },
    {
        "question": "How long can I be on Leave of Absence?",
        "reference": """●	A personal leave of absence can be one or two semesters. 
●	A Medical leave of absence may have a different duration depending on the circumstances. Please remain in contact with your academic advisor and the advising office (advising@dukekunshan.edu.cn) to inform them of any updates.
""",
        "response": """"""
    },
    {
        "question": "What is considered an Academic Warning?",
        "reference": """●	A single or more grade of F or NC (excluding PE courses) in a term
●	A second or more grade of D (D, D-, D+) over the student’s tenure at DKU
●	Failure to meet the term credit requirements (See section on Term Credit Requirements).
●	A grade of C- or below for CAPSTONE 495 Signature Work Capstone I
●	Failure to meet Signature Work milestones and submission deadlines (mentor agreement, project proposal, or other documentation).
""",
        "response": """"""
    },
    {
        "question": "What is considered Academic Probation?",
        "reference": """For the Class of 2025 and beyond:
●	At the end of each fall and spring semester, failure to meet a 2.0 GPA (either a term GPA or a cumulative GPA) will result in academic probation for the following semester. 
""",
        "response": """"""
    },
    {
        "question": "What should I do if I’m placed on academic probation?",
        "reference": """●	You must acknowledge your probationary status to the Office of Academic Services in writing in order to continue at the university. In most cases this acknowledgement will go through Academic Advising.
●	You are required to meet with the Director of Academic Advising prior to the Drop/Add deadline.
●	You are also expected to seek assistance from other campus resources and meet with your academic advisor periodically.
●	You are expected to clear your probationary status during the semester of probation.
""",
        "response": """"""
    },
    {
        "question": "How do I clear my probationary status?",
        "reference": """●	You must enroll in 16 credits (plus up to one PE credit), of which no more than 4 credits may be taken on a Credit/ No Credit basis.
●	Probationary status cannot be cleared the semester which you withdraw to underload. 
For the Class of 2022 to 2024:
●	A grade of C, CR, or better must be earned in each course, or a C average (GPA 2.0) must be achieved in that semester. 
●	Note that if you received a C average (GPA 2.0) for the semester but have a grade combination that would result in academic probation, you will continue your probationary status through the next semester of enrollment.
For the Class of 2025 and beyond:
●	You must achieve a term and cumulative GPA of at least  2.0.
""",
        "response": """"""
    },
    {
        "question": "How do I return from Academic Suspension?",
        "reference": """●	You may apply for Return to the University by contacting the Office of Academic Services. 
●	The deadlines for filing this application are 5:00 PM China time May 1 for return in the subsequent Fall Term and October 1 for return in the subsequent Spring Term.
●	After reinstated, you will be placed on academic probation. 
""",
        "response": """"""
    },
    #PE Class and National Student Physical Health Standard Test (NSPHST
    {
        "question": "Do I need to take PE courses and do the credits count toward graduation?",
        "reference": """●	Students from mainland China and HMT are required to take 4 credits of PE courses. PE courses are optional for students from other locations. 
●	Regardless of residency status or participation in varsity sports, a maximum of 2 credits for PE can be applied toward the minimum 136 credits required for a bachelor’s degree. 
●	Note: PE courses can be half or full 1 credit course
""",
        "response": """"""
    },
    {
        "question": "Do PE courses affect my grades or academic standing?",
        "reference": """●	No, PE courses are only offered on a Credit/ No Credit basis, thus they don’t affect your GPA. They are not taken into consideration when we are determining academic standing either. However, receiving an NC from PE class will make you ineligible for the Dean's list. """,
        "response": """"""
    },
    {
        "question": "What is the National PE test and must I take it?",
        "reference": """●	The National Student Physical Health Standard Test (NSPHST) is required by Chinese Ministry of Education and is mandatory for all China mainland and HMT students to participate in. 
●	If you are a student from China mainland and HMT, you need to pass the NSPHST in order to graduate. 
""",
        "response": """"""
    },
    {
        "question": "What is the scoring standard for NSPHST and graduation requirement?",
        "reference": """●	Performance scoring:
○	Excellent >90.0%
○	Good 80.0-89.9%
○	Pass 60.0-79.9%
○	Fail 50.0-59.9%, but still receive diploma/graduate
■	Please note that the certificate will indicate that students have failed the NSPHST.
○	Fail <50.0%, cannot receive diploma/graduate
●	Final graduation score = 50% (average of Freshman/Sophomore/Junior year) + 50% (Senior year)
""",
        "response": """"""
    },
    {
        "question": "What are the items assessed in NSPHST?",
        "reference": """●	Items assessed include Body Mass Index (BMI), vital capacity, 50-meter run, Sit and Reach, standard long jump, pull-up (for male)/1-minute sit-up (for female), and 1000-meter run (for male)/800-meter run (for female).""",
        "response": """"""
    },
    {
        "question": "Can I make up the NSPHST if I fail the first time?",
        "reference": """●	Students who failed the first time or were exempted from the first exam are qualified to retake the exam. Please contact DKU Athletics for more information.""",
        "response": """"""
    },
    {
        "question": "How many make up opportunities are offered?",
        "reference": """●	Only 1 make-up opportunity is offered, and if you miss both tests, you’ll receive 0 for this attempt.
●	Different make-up policies apply if you have a medical exemption.
""",
        "response": """"""
    },
    {
        "question": "Can I retake the NSPHST to improve my previous score?",
        "reference": """●	Only students who failed the first time, or who had a medical exemption can take the second opportunity.""",
        "response": """"""
    },
    {
        "question": "Does NSPHST score affect GPA?",
        "reference": """●	No, but students will receive an official diploma/transcript with their final score. """,
        "response": """"""
    },
    {
        "question": "Can I be exempt from the NSPHST?",
        "reference": """●	Yes. A permanent exemption is possible for students with a permanent medical disability that directly affects performance on the tests. 
●	Students who have minor medical issues on the day of testing may also apply for an exemption with the DKU Athletics team but must take the makeup opportunity.
●	Please note that students without a medical certificate or an official exemption from the Athletics team will receive 0 for the test.  
●	Additionally, for female students who are on the menstrual cycle the day of the test and wish to apply for exemption, you should consider if you are physically able to perform the test, because under MOE rules this is not a valid medical exemption. However, it is understood that not all female students have the same experience during this period, hence please consult the DKU Athletics for the possibility of a medical exemption. Note that because there are 6-week differences between testing dates, students who missed the first testing opportunity for this reason, cannot use the same reason to miss the second opportunity, unless there is a verified medical condition.
""",
        "response": """"""
    },
    {
        "question": "Can I apply for exemption after the test is done?",
        "reference": """●	No retrospective exemptions are provided. Students should apply for exemption at the earliest possible convenience, and one week before the test as the latest. """,
        "response": """"""
    },
    #Credits Transfer
    {
        "question": "How many AP scores can I transfer?",
        "reference": """●	A maximum of 8 credits can be transferred from AP/ IPC/ Pre Matriculation credits. """,
        "response": """"""
    },
    {
        "question": "How many credits can I transfer from Study Abroad?",
        "reference": """●	A Duke Kunshan University student may receive credit for a maximum of 40 credits taken elsewhere, through a combination of AP/IPC credit or approved transfer or study away credit. """,
        "response": """"""
    },
    {
        "question": "Can I transfer credits from the college-level courses that I took prior to coming to DKU?",
        "reference": """●	Yes, but only if they meet each of the following criteria: 
○	Were taken after the commencement of the junior year of high school and yielded a grade of B- or better;
○	Not used to meet high school diploma requirements; 
○	Taken on the college campus;
○	Taken in competition with degree candidates of the college;
○	Taught by a regular member of the college faculty;
○	Offered as part of the regular curriculum of the college;
○	And not taken on a study abroad program completed prior to matriculation at Duke Kunshan
●	A formal review will be conducted after an official transcript of all college courses taken and documentation pertaining to these criteria are received by the DKU Registrar. 
""",
        "response": """"""
    },
    {
        "question": "Can I transfer credits from courses I take during my Leave of Absence?",
        "reference": """●	Yes. A maximum of 8 may be from coursework undertaken while on voluntary leave of absence for personal or medical reasons. 
●	The transferred courses must be at another accredited four-year institution in the United States or similarly accredited institution abroad and with liberal arts and general education curriculum.
""",
        "response": """"""
    },
    {
        "question": "Can I transfer credits from courses I take during my suspension?",
        "reference": """●	Yes. A maximum of 8 may be from coursework undertaken while on suspension for academic reasons. """,
        "response": """"""
    },
    #Academic Recognition and Honors
    {
        "question": "How do I get on the Dean’s List?",
        "reference": """●	You must earn a grade point average for a semester that places them in the highest third of undergraduates in their class year and in addition, must 
○	(1) complete at least 16 credits for a regularly assigned grade (i.e., no Credit/No Credit courses); 
○	(2) receive no incomplete (I) or failing (F, NC) grades (including PE courses).
""",
        "response": """"""
    },
    {
        "question": "What is the Dean’s List with Distinction honor?",
        "reference": """●	Students who in addition earn semester grade point averages that place them in the highest 10% of undergraduates in their class year will receive the Dean’s List with Distinction honor, while the remainder of those placing in the highest one third will receive the Dean’s List honor.""",
        "response": """"""
    },
    {
        "question": "What are the Latin Honors?",
        "reference": """●	There are three categories of Lain Honors: Summa Cum Laude, Magna Cum Laude, and Cum Laude.
●	The eligibility of these Latin honors is based on the cumulative GPA for all work at DKU.
""",
        "response": """"""
    },
    #Graduation
    {
        "question": "How do I apply for graduation?",
        "reference": """●	The Diploma Form submitted by students is an official notification that they expect to have completed all requirements for the degree and to receive the diploma on particular graduation date.
●	Information regarding the location and date of availability of the online diploma form is sent to prospective graduates at their Duke Kunshan University e-mail address
""",
        "response": """"""
    },
    {
        "question": "How many credits do I need to graduate?",
        "reference": """●	A total of 136 Duke Kunshan University credits is required for students to graduate and obtain the degrees, inclusive of 34 Duke Kunshan University credits earned through courses taught or co-taught by Duke faculty (8.5 DKU courses).
●	Note that mainland Chinese and HMT students have additional credit requirements above the 136 credits (depending on their residency status).
""",
        "response": """"""
    },
    {
        "question": "When is the graduation ceremony/ commencement?",
        "reference": """●	Please follow the commencement website for more information. The commencement date for each academic year is posted on the academic calendar.""",
        "response": """"""
    },
    {
        "question": "What are the graduation confirmations?",
        "reference": """●	Students will receive three confirmations of graduation: a Duke University diploma (issued by Duke University), a Duke Kunshan University diploma (from the Ministry of Education of the PRC), and a Duke Kunshan University graduation certificate (from the Ministry of Education of the PRC).""",
        "response": """"""
    },
    {
        "question": "Can I graduate in Fall semester?",
        "reference": """●	Graduation and commencement are two separate activities. Commencement is held once a year in May. However, students may graduate and receive their diploma at the end of Fall or Spring semester. 
●	Students who complete graduation requirements at the end of Summer or Fall term will receive their diploma in December. These students are eligible to participate in the following Spring commencement ceremony.
●	Students who need less than 20 credits for graduation at the end of Spring term may request to participate in the annual commencement exercises.
""",
        "response": """"""
    },
    #Uncategorized
    {
        "question": "When is the deadline to add an Independent Study (research or non-research) course?",
        "reference": """●	If you are doing an Independent Study for 14 weeks, the deadline to add the course is by the end of the second week of the semester. If you are doing it for 7 weeks, the deadline is by the end of the Drop/Add of the session in which you will be doing the independent study.
●	Students can find guidelines and the application form for the Independent Study at https://dukekunshan.edu.cn/en/registrar-office/student-records (Office of the Registrar). 
""",
        "response": """"""
    },
]


async def evaluate_responses():
    scorers = {
        'levenshtein': NonLLMStringSimilarity(),
        'bleu': BleuScore(),
        'rouge': RougeScore()
    }
    
    results = []
    
    for pair in faq_pairs:
        sample = SingleTurnSample(
            response=pair["response"],  # 预留response字段
            reference=pair["reference"]
        )
        
        scores = {}
        comments = []
        # 并行计算指标
        tasks = {
            name: scorer.single_turn_ascore(sample)
            for name, scorer in scorers.items()
        }
        completed = await asyncio.gather(*tasks.values())
        
        # 结构化存储结果
        for (name, score) in zip(scorers.keys(), completed):
            scores[name] = round(score, 4)
            comments.append(
                f"{name.capitalize()} Score: {round(score*100,2)}% " + 
                {"levenshtein": "(Edit Distance)", 
                 "bleu": "(N-gram Precision)",
                 "rouge": "(LCS F1)"}[name]
            )
        
        results.append({
            "question": pair["question"][:50] + "..." if len(pair["question"]) > 50 else pair["question"],
            "scores": scores,
            "details": {
                "reference_length": len(pair["reference"]),
                "response_placeholder": "PENDING RESPONSE INPUT",
                "assessment_notes": comments
            }
        })
    
    # 输出格式化结果
    for idx, res in enumerate(results, 1):
        print(f"\nAssessment #{idx}")
        print(f"Question: {res['question']}")
        print("Metrics:")
        for metric, score in res['scores'].items():
            print(f"- {metric.upper()}: {score}")
        print("\nDiagnostics:")
        print(f"- Reference length: {res['details']['reference_length']} chars")
        print("- Assessment Notes:")
        for note in res['details']['assessment_notes']:
            print(f"  > {note}")
        print("━"*60)

if __name__ == "__main__":
    asyncio.run(evaluate_responses())


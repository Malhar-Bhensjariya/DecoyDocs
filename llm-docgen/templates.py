# templates.py
# Small collection of natural-language templates to prime Gemini for different doc types.

# TEMPLATES = {
#     "generic_report": (
#         "You are a professional writer creating an internal business document. "
#         "Produce a clear, realistic, and believable document with a short executive summary, "
#         "two or three sections with headings, a small table-like bulleted summary of figures (if relevant), "
#         "and a concluding recommendation. Use realistic names, dates (recent year), and monetary figures where appropriate."
#     ),

#     "employee_bonus": (
#         "Create an internal HR memo titled '2025 Employee Bonuses' describing bonus allocation by department, "
#         "criteria used, a short breakdown of bonus ranges, and an executive summary for managers. Include believable reasons "
#         "for allocations and short example numbers."
#     ),

#     "q3_financial": (
#         "Create a Q3 financial summary report for a mid-sized tech company. Include revenue, expenses, YoY comparisons, "
#         "brief commentary on key drivers (product launches, channel performance), and a short outlook for Q4."
#     ),

#     "hr_review": (
#         "Write a short HR performance review template for an employee in Software Engineering. Include strengths, areas for improvement, "
#         "goals for next quarter, and suggested training."
#     ),

#     "sales_pipeline": (
#         "Create a sales pipeline status report for the week, listing top 5 deals, expected close dates, potential revenue, and risks."
#     ),
# }
TEMPLATES = {
    "generic_report": {
        "prompt": (
            "You are a professional writer creating an internal business document. "
            "Produce a clear, realistic, and believable document with a short executive summary, "
            "two or three sections with headings, a small table-like bulleted summary of figures (if relevant), "
            "and a concluding recommendation. Use realistic names, dates (recent year), and monetary figures where appropriate."
        ),
        "title": "Corporate Strategy and Growth Report - Q1 2026"
    },

    "employee_bonus": {
        "prompt": (
            "Create an internal HR memo titled '2025 Employee Bonuses' describing bonus allocation by department, "
            "criteria used, a short breakdown of bonus ranges, and an executive summary for managers."
        ),
        "title": "2025 Employee Bonuses"
    },

    "q3_financial": {
        "prompt": (
            "Create a Q3 financial summary report for a mid-sized tech company. Include revenue, expenses, YoY comparisons, "
            "brief commentary on key drivers (product launches, channel performance), and a short outlook for Q4."
        ),
        "title": "Q3 2025 Financial Summary"
    },

    "hr_review": {
        "prompt": (
            "Write a short HR performance review template for an employee in Software Engineering. Include strengths, areas for improvement, "
        "goals for next quarter, and suggested training."
        ),
        "title": "Software Engineering - HR Review"
    },

    "sales_pipeline": {
        "prompt": (
            "Create a sales pipeline status report for the week, listing top 5 deals, expected close dates, potential revenue, and risks."
        ),
        "title": "Weekly Sales Pipeline Report"
    }
}

SAMPLE_TITLES = [
    "2025 Employee Bonuses",
    "Q3 2025 Financial Summary",
    "Software Engineering - Midyear Review",
    "Weekly Sales Pipeline - North America",
    "Product Launch Readout - Gemini Project",
]

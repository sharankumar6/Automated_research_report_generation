# It works in 3 Layers:

# workflow-1: Generate Multiple Analyst personas for a topic(with optional human feedback loop)

# workflow-2: For each analyst, run an interview loop:
#             - analyst asks questions
#             - systems search web / wikipedia
#             - "expert" answers using retrieved context
#             - save interview + write a memo/section

# workflow-3: Run all interviews in parallel (map), then merge all memos into a final report with Intro + Conclusion (reduce)

# Backend:
#         - Workflow
#         - Utility
#         - config


'''
* Run the code: uvicorn research_and_analyst.api.main:app --reload
'''

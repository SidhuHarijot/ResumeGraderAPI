class status_codes:
    APPLIED = 600
    PENDING_RE_EVALUATION = 601
    GRADED = 700
    SHORTLISTED = 701
    SELECTED = 710
    CONTACTED = 720
    FEEDBACK_SENT = 721
    NOT_SUITABLE = 900
    ISSUE_GRADING = 910

    @staticmethod
    def get_status(status_code: int):
        if status_code == status_codes.APPLIED:
            return "Applied"
        elif status_code == status_codes.PENDING_RE_EVALUATION:
            return "Pending Re-Evaluation"
        elif status_code == status_codes.GRADED:
            return "Graded"
        elif status_code == status_codes.SHORTLISTED:
            return "Shortlisted"
        elif status_code == status_codes.SELECTED:
            return "Selected"
        elif status_code == status_codes.CONTACTED:
            return "Contacted"
        elif status_code == status_codes.FEEDBACK_SENT:
            return "Feedback Sent"
        elif status_code == status_codes.NOT_SUITABLE:
            return "Not Suitable"
        elif status_code == status_codes.ISSUE_GRADING:
            return "Issue Grading"
        else:
            raise ValueError(f"Invalid status code: {status_code}")
    
    @staticmethod
    def get_all_codes():
        return [
            status_codes.APPLIED,
            status_codes.PENDING_RE_EVALUATION,
            status_codes.GRADED,
            status_codes.SHORTLISTED,
            status_codes.SELECTED,
            status_codes.CONTACTED,
            status_codes.FEEDBACK_SENT,
            status_codes.NOT_SUITABLE,
            status_codes.ISSUE_GRADING
        ]

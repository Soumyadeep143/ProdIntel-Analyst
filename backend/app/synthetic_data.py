from __future__ import annotations

from typing import Any

PRODUCT_AREAS = ["search", "analytics", "notifications", "billing", "collaboration"]
SOURCE_TEMPLATES = {
    "support_ticket": [
        "Users report {issue} in {area}.",
        "Customers are seeing {issue} when using {area}.",
        "Repeated complaints mention {issue} in {area}.",
    ],
    "github_issue": [
        "Issue opened for {issue} affecting {area}.",
        "Engineering needs to fix {issue} in {area}.",
        "Regression reported around {issue} for {area}.",
    ],
    "prd": [
        "The PRD for {area} prioritizes work on {issue}.",
        "The roadmap for {area} includes a plan to address {issue}.",
        "Product direction for {area} calls for better handling of {issue}.",
    ],
    "meeting_note": [
        "Meeting notes highlight {issue} in {area}.",
        "Team discussion focused on {issue} affecting {area}.",
        "Stakeholders asked for prioritization of {issue} in {area}.",
    ],
    "release_note": [
        "Release notes mention improvements for {issue} in {area}.",
        "The latest release improves {issue} in {area}.",
        "Customers should see fewer issues with {issue} in {area}.",
    ],
    "customer_interview": [
        "Customer interview highlights {issue} as a key friction point in {area}.",
        "Interviewee expressed dissatisfaction with {issue} in {area}.",
        "Feedback from customer interview notes {issue} within {area}.",
    ],
    "research_document": [
        "User research on {area} shows usability issues around {issue}.",
        "Market research notes {issue} in {area} as an area of potential churn.",
        "Usability research documentation highlights {issue} in {area}.",
    ],
    "competitor_report": [
        "Competitor analysis shows our {area} lacks compared to peers on {issue}.",
        "Product comparison report flags {issue} as a disadvantage in {area}.",
        "Market report indicates competitors are winning on handling {issue} in {area}.",
    ],
}

ISSUES = [
    "slow search latency",
    "missing notification alerts",
    "confusing billing invoices",
    "poor export reliability",
    "broken collaboration invites",
    "unclear permission warnings",
    "duplicate dashboard widgets",
    "inconsistent analytics filters",
]


def generate_synthetic_documents(count: int = 1000) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for index in range(count):
        source_type = [
            "support_ticket",
            "github_issue",
            "prd",
            "meeting_note",
            "release_note",
            "customer_interview",
            "research_document",
            "competitor_report",
        ][index % 8]
        area = PRODUCT_AREAS[index % len(PRODUCT_AREAS)]
        issue = ISSUES[index % len(ISSUES)]
        title = f"{area.title()} issue #{index + 1}"
        body_template = SOURCE_TEMPLATES[source_type][index % len(SOURCE_TEMPLATES[source_type])]
        body = body_template.format(issue=issue, area=area)
        documents.append(
            {
                "id": f"{source_type}-{index + 1:03d}",
                "source_type": source_type,
                "title": title,
                "body": body,
                "author": f"author-{(index % 7) + 1}",
                "created_at": f"2026-0{(index % 6) + 1:01d}-1{index % 9 + 1:01d}T00:00:00Z",
                "tags": [area, issue.split()[0]],
                "related_ids": [],
            }
        )

    return documents

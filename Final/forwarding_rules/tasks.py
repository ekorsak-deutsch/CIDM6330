import os
import json
from datetime import datetime
from celery import shared_task
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .repository import create_repositories


def _create_report_base(report_name, title_text):
    """
    Create a base report with common elements
    
    Args:
        report_name: Name for the report file
        title_text: Title text for the report
        
    Returns:
        tuple: (doc, elements, styles, report_path)
    """
    # Generate filename based on timestamp if not provided
    if not report_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = report_name or f"{title_text.lower().replace(' ', '_')}_{timestamp}.pdf"
    
    # Full path to the report file
    report_path = os.path.join(settings.REPORTS_DIR, report_name)
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        report_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Container for the 'Flowable' objects (paragraphs, tables, etc.)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    normal_style = styles['Normal']
    
    # Add title
    title = Paragraph(title_text, title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_paragraph = Paragraph(f"Generated: {timestamp}", normal_style)
    elements.append(timestamp_paragraph)
    elements.append(Spacer(1, 24))
    
    return doc, elements, styles, report_path


def _add_statistics_section(elements, rule_repo, styles):
    """
    Add statistics section to the report
    
    Args:
        elements: List of report elements
        rule_repo: Repository for forwarding rules
        styles: Report styles
    """
    heading_style = styles['Heading2']
    
    # Add statistics
    stats = rule_repo.get_statistics()
    elements.append(Paragraph("Statistics", heading_style))
    
    # Create a table for statistics
    stats_data = [["Metric", "Value"]]
    for key, value in stats.items():
        # Format the key to be more readable
        formatted_key = " ".join(word.capitalize() for word in key.split("_"))
        stats_data.append([formatted_key, str(value)])
    
    stats_table = Table(stats_data, colWidths=[300, 100])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 24))


def _add_rules_section(elements, rules, filter_repo, styles, include_filters=True):
    """
    Add rules section to the report
    
    Args:
        elements: List of report elements
        rules: List of rules
        filter_repo: Repository for filters
        styles: Report styles
        include_filters: Whether to include filter information
    """
    heading_style = styles['Heading2']
    
    # Custom styles
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        spaceAfter=12
    )
    
    # Add rules details
    elements.append(Paragraph("Forwarding Rules", heading_style))
    elements.append(Spacer(1, 12))
    
    # Process each rule
    for rule in rules:
        # Rule header
        rule_title = f"Rule #{rule.id}: {rule.email}"
        elements.append(Paragraph(rule_title, section_style))
        
        # Rule details table
        rule_data = [
            ["Attribute", "Value"],
            ["Name", rule.name],
            ["Forwarding Email", rule.forwarding_email or "None"],
            ["Disposition", rule.disposition or "None"],
            ["Has Filters", "Yes" if rule.has_forwarding_filters else "No"],
            ["Error", rule.error or "None"],
            ["Investigation Note", rule.investigation_note or "None"]
        ]
        
        rule_table = Table(rule_data, colWidths=[150, 250])
        rule_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(rule_table)
        elements.append(Spacer(1, 12))
        
        # Add filter information if requested
        if include_filters and rule.has_forwarding_filters:
            # Get filters for this rule
            filters = filter_repo.get_filters_for_rule(rule.id)
            
            if filters:
                elements.append(Paragraph("Filter Configuration:", styles['Heading3']))
                
                for filter_obj in filters:
                    # Format JSON for better presentation
                    criteria_str = json.dumps(filter_obj.criteria, indent=2)
                    action_str = json.dumps(filter_obj.action, indent=2)
                    
                    filter_data = [
                        ["Attribute", "Value"],
                        ["Filter ID", str(filter_obj.id)],
                        ["Created At", filter_obj.created_at or "Unknown"],
                        ["Criteria", criteria_str],
                        ["Action", action_str]
                    ]
                    
                    filter_table = Table(filter_data, colWidths=[150, 250])
                    filter_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    
                    elements.append(filter_table)
                    elements.append(Spacer(1, 12))
        
        # Add separator between rules
        elements.append(Spacer(1, 24))


@shared_task
def generate_rules_report(report_name=None):
    """
    Generate a PDF report of all forwarding rules in the database with filter details
    
    Args:
        report_name: Optional name for the report file
        
    Returns:
        str: Path to the generated PDF report
    """
    # Create repositories to access data
    rule_repo, filter_repo = create_repositories()
    
    # Get all rules
    rules = rule_repo.get_all_rules()
    
    # Create report base
    doc, elements, styles, report_path = _create_report_base(
        report_name, 
        "Email Forwarding Rules Audit Report"
    )
    
    # Add statistics section
    _add_statistics_section(elements, rule_repo, styles)
    
    # Add rules section with filters
    _add_rules_section(elements, rules, filter_repo, styles, include_filters=True)
    
    # Build the PDF
    doc.build(elements)
    
    # Return the path to the generated report
    return report_path


@shared_task
def generate_stats_report(report_name=None):
    """
    Generate a PDF report with only statistics about forwarding rules
    
    Args:
        report_name: Optional name for the report file
        
    Returns:
        str: Path to the generated PDF report
    """
    # Create repositories to access data
    rule_repo, filter_repo = create_repositories()
    
    # Create report base with appropriate name
    if not report_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"stats_report_{timestamp}.pdf"
        
    doc, elements, styles, report_path = _create_report_base(
        report_name, 
        "Email Forwarding Rules Statistics Report"
    )
    
    # Add statistics section
    _add_statistics_section(elements, rule_repo, styles)
    
    # Add summary paragraph
    normal_style = styles['Normal']
    summary = Paragraph(
        "This report contains only statistical information about email forwarding rules. "
        "For detailed information about individual rules, please generate a complete report.",
        normal_style
    )
    elements.append(summary)
    
    # Build the PDF
    doc.build(elements)
    
    # Return the path to the generated report
    return report_path


@shared_task
def generate_rules_only_report(report_name=None):
    """
    Generate a PDF report of all forwarding rules without filter details
    
    Args:
        report_name: Optional name for the report file
        
    Returns:
        str: Path to the generated PDF report
    """
    # Create repositories to access data
    rule_repo, filter_repo = create_repositories()
    
    # Get all rules
    rules = rule_repo.get_all_rules()
    
    # Create report base with appropriate name
    if not report_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"rules_only_report_{timestamp}.pdf"
        
    doc, elements, styles, report_path = _create_report_base(
        report_name, 
        "Email Forwarding Rules Only Report"
    )
    
    # Add rules section without filters
    _add_rules_section(elements, rules, filter_repo, styles, include_filters=False)
    
    # Add note about filters being excluded
    normal_style = styles['Normal']
    note = Paragraph(
        "Note: This report contains only basic information about forwarding rules. "
        "Filter details have been excluded. For complete information including filters, "
        "please generate a full report.",
        normal_style
    )
    elements.append(note)
    
    # Build the PDF
    doc.build(elements)
    
    # Return the path to the generated report
    return report_path 
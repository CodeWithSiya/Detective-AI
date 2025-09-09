from django.conf import settings
from app.models.text_analysis_result import TextAnalysisResult
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
import logging
import html

logger = logging.getLogger(__name__)

class ReportService:
    """
    Service for generating PDF reports from analysis results.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 09/09/2025
    """

    def __init__(self):
        """
        Initialise the Report Service.
        """
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """
        Setup custom paragraph styles for the report.
        """
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e')
        ))

        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        ))

    def _get_standard_table_style(self):
        """
        Get standard table styling to maintain consistency.
        """
        return TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ])

    def generate_analysis_report(self, analysis_result: TextAnalysisResult, user_email: str) -> BytesIO:
        """
        Generate a PDF report for a text analysis result.

        :param analysis_result: TextAnalysisResult instance.
        :param user_email: Email of the user requesting the report.
        :return: BytesIO buffer containing the PDF
        :raises: Exception if report generation fails
        """
        try:
            # Validate inputs
            if not analysis_result:
                raise ValueError("Analysis result cannot be None")
            if not user_email:
                raise ValueError("User email cannot be empty")

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
            story = []

            # Main Report Content.
            title = Paragraph("AI Content Detection Report", self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 20))

            self._add_report_metadata(story, analysis_result, user_email)     
            self._add_analysis_summary(story, analysis_result)
            self._add_detection_details(story, analysis_result)
            self._add_statistics_section(story, analysis_result)
            self._add_text_sample(story, analysis_result)
            self._add_footer(story)

            # Build document with canvas elements (watermark and page numbers).
            doc.build(
                story,
                onFirstPage=self._apply_canvas_elements,
                onLaterPages=self._apply_canvas_elements
            )

            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {str(e)}")
            raise Exception(f"Report generation failed: {str(e)}")
    
    def _add_report_metadata(self, story, analysis_result: TextAnalysisResult, user_email: str):
        """
        Add report metadata section.
        """
        try:
            story.append(Paragraph("Report Information", self.styles['SectionHeader']))

            # Safely get analysis ID
            analysis_id = getattr(analysis_result, 'id', 'N/A')
            created_at = getattr(analysis_result, 'created_at', None)
            created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S UTC') if created_at else 'N/A'
            processing_time = getattr(analysis_result, 'processing_time_ms', 'N/A')

            metadata_data = [
                ['Report ID:', str(analysis_id)],
                ['Generated For:', html.escape(user_email)],
                ['Analysis Date:', created_at_str],
                ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')],
                ['Processing Time:', f"{processing_time}ms"]
            ]

            table = Table(metadata_data, colWidths=[2*inch, 4*inch])
            table.setStyle(self._get_standard_table_style())
            
            story.append(table)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            logger.error(f"Failed to add report metadata: {str(e)}")
            # Add a placeholder section so the report doesn't fail completely
            story.append(Paragraph("Report Information - Error Loading", self.styles['SectionHeader']))
            story.append(Spacer(1, 20))

    def _add_analysis_summary(self, story, analysis_result: TextAnalysisResult):
        """
        Add analysis summary section.
        """
        try:
            story.append(Paragraph("Analysis Summary", self.styles['SectionHeader']))
            
            # Main result
            detection_result = getattr(analysis_result, 'detection_result', '')
            is_ai_generated = detection_result == 'AI_GENERATED'
            result_color = 'red' if is_ai_generated else 'green'
            result_text = "AI Generated" if is_ai_generated else "Human Written"
            
            # Format probability safely
            probability = getattr(analysis_result, 'probability', None)
            probability_text = f"{probability:.1%}" if probability is not None else "N/A"
            
            confidence = getattr(analysis_result, 'confidence', None)
            confidence_text = f"{confidence:.1%}" if confidence is not None else "N/A"
            
            enhanced_analysis = getattr(analysis_result, 'enhanced_analysis_used', False)
            
            summary_data = [
                ['Detection Result:', f'<font color="{result_color}"><b>{result_text}</b></font>'],
                ['Confidence Score:', probability_text],
                ['Model Confidence:', confidence_text],
                ['Enhanced Analysis:', "Yes" if enhanced_analysis else "No"]
            ]
            
            table = Table(summary_data, colWidths=[2*inch, 4*inch])
            table.setStyle(self._get_standard_table_style())
            
            story.append(table)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            logger.error(f"Failed to add analysis summary: {str(e)}")
            story.append(Paragraph("Analysis Summary - Error Loading", self.styles['SectionHeader']))
            story.append(Spacer(1, 20))

    def _add_detection_details(self, story, analysis_result: TextAnalysisResult):
        """
        Add detection details section.
        """
        try:
            detection_reasons = getattr(analysis_result, 'detection_reasons', None)
            if not detection_reasons:
                return
                
            story.append(Paragraph("Detection Details", self.styles['SectionHeader']))
            
            for reason in detection_reasons:
                if not isinstance(reason, dict):
                    continue
                    
                # Color code by type
                type_colors = {
                    'critical': 'red',
                    'warning': 'orange',
                    'info': 'blue',
                    'success': 'green'
                }
                
                reason_type = reason.get('type', 'info')
                color = type_colors.get(reason_type, 'black')
                
                # Safely get and escape title
                title = reason.get("title", "Unknown")
                title_escaped = html.escape(str(title))
                title_text = f'<font color="{color}"><b>{title_escaped}</b></font>'
                story.append(Paragraph(title_text, self.styles['BodyText']))
                
                # Safely get and escape description and impact
                description = html.escape(str(reason.get('description', 'No description available')))
                impact = html.escape(str(reason.get('impact', 'No impact information')))
                
                story.append(Paragraph(f"Description: {description}", self.styles['BodyText']))
                story.append(Paragraph(f"Impact: {impact}", self.styles['BodyText']))
                story.append(Spacer(1, 10))
                
        except Exception as e:
            logger.error(f"Failed to add detection details: {str(e)}")

    def _add_statistics_section(self, story, analysis_result: TextAnalysisResult):
        """
        Add statistics section.
        """
        try:
            statistics = getattr(analysis_result, 'statistics', None)
            if not statistics:
                return
                
            story.append(Paragraph("Text Statistics", self.styles['SectionHeader']))
            
            stats_data = [
                ['Total Words:', str(statistics.get('total_words', 'N/A'))],
                ['Sentences:', str(statistics.get('sentences', 'N/A'))],
                ['Avg Sentence Length:', str(statistics.get('avg_sentence_length', 'N/A'))],
                ['AI Keywords Found:', str(statistics.get('ai_keywords_count', 'N/A'))],
                ['Transition Words:', str(statistics.get('transition_words_count', 'N/A'))],
                ['Corporate Jargon:', str(statistics.get('corporate_jargon_count', 'N/A'))],
                ['Buzzwords:', str(statistics.get('buzzwords_count', 'N/A'))],
                ['Human Indicators:', str(statistics.get('human_indicators_count', 'N/A'))]
            ]
            
            table = Table(stats_data, colWidths=[2.5*inch, 1.5*inch])
            table.setStyle(self._get_standard_table_style())
            
            story.append(table)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            logger.error(f"Failed to add statistics section: {str(e)}")

    def _add_text_sample(self, story, analysis_result: TextAnalysisResult):
        """Add text sample section."""
        try:
            submission = getattr(analysis_result, 'submission', None)
            if submission and hasattr(submission, 'content'):
                story.append(Paragraph("Analyzed Text Sample", self.styles['SectionHeader']))
                
                # Safely get content
                content = getattr(submission, 'content', '')
                if not content:
                    content = "No content available"
                else:
                    # Truncate if too long
                    if len(content) > 500:
                        content = content[:500] + "... [truncated]"
                
                # Escape content for ReportLab
                content_escaped = html.escape(content)
                
                story.append(Paragraph(f'"{content_escaped}"', self.styles['BodyText']))
                story.append(Spacer(1, 20))
        except Exception as e:
            logger.error(f"Could not add text sample: {str(e)}")

    def _add_footer(self, story):
        """
        Add footer section.
        """
        try:
            story.append(Spacer(1, 30))
            footer_text = """
            <i>This report was generated by Detective AI - AI Content Detection System.<br/>
            For questions about this analysis, please contact our support team.</i>
            """
            story.append(Paragraph(footer_text, self.styles['BodyText']))
        except Exception as e:
            logger.error(f"Failed to add footer: {str(e)}")

    def _add_watermark(self, canvas, doc, text="Detective AI", font_size=40, alpha=0.1):
        """
        Draw a diagonal watermark on the page.
        """
        try:
            canvas.saveState()
            canvas.setFont("Helvetica-Bold", font_size)
            
            # Set fill alpha and color separately
            canvas.setFillAlpha(alpha)
            canvas.setFillColorRGB(0.85, 0.85, 0.85)
            
            width, height = A4
            canvas.translate(width / 2, height / 2)
            canvas.rotate(45)
            canvas.drawCentredString(0, 0, text)
            canvas.restoreState()
        except Exception as e:
            logger.error(f"Failed to add watermark: {str(e)}")

    def _add_page_number(self, canvas, doc):
        """
        Add page number at the bottom-right corner.
        """
        try:
            canvas.saveState()
            width, _ = A4
            page_num = canvas.getPageNumber()
            canvas.setFont("Helvetica", 9)
            canvas.setFillColorRGB(0, 0, 0)
            canvas.drawRightString(width - 2*cm, 1*cm, f"Page {page_num}")
            canvas.restoreState()
        except Exception as e:
            logger.error(f"Failed to add page number: {str(e)}")

    def _apply_canvas_elements(self, canvas, doc):
        """
        Apply all canvas-level elements like watermark and page numbers.
        """
        self._add_watermark(canvas, doc)
        self._add_page_number(canvas, doc)
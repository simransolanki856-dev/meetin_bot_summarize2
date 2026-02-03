from flask import Flask, render_template, request, jsonify, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import uuid
from config import Config
from utils.audio_processor import AudioProcessor
from utils.ai_summarizer import AISummarizer
from utils.google_meet_bot import GoogleMeetBot

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Database Models
class Meeting(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    meeting_type = db.Column(db.String(50), nullable=False)
    transcript = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    ai_output = db.Column(db.Text)  # JSON stored as text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'meeting_type': self.meeting_type,
            'transcript': self.transcript,
            'created_at': self.created_at.isoformat(),
            'ai_output': json.loads(self.ai_output) if self.ai_output else None
        }

# Initialize AI Summarizer
ai_summarizer = AISummarizer()

# Routes
@app.route('/')
def index():
    return render_template('create.html')

@app.route('/create', methods=['GET', 'POST'])
def create_meeting():
    if request.method == 'GET':
        return render_template('create.html')
    
    try:
        # Get form data
        title = request.form.get('title', 'Untitled Meeting')
        meeting_type = request.form.get('type', 'Team meeting')
        transcript = request.form.get('transcript', '')
        
        file_path = None
        transcript_text = transcript
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Extract transcript from audio/video
                if filename.lower().endswith(('.mp3', '.wav', '.mp4', '.m4a')):
                    processor = AudioProcessor()
                    transcript_text = processor.extract_transcript(file_path)
        
        # Generate summary using AI
        if transcript_text:
            ai_result = ai_summarizer.generate_summary(transcript_text, meeting_type)
        else:
            ai_result = {
                "summary": "No transcript provided.",
                "key_points": [],
                "decisions": [],
                "action_items": [],
                "agenda": []
            }
        
        # Save to database
        meeting = Meeting(
            title=title,
            meeting_type=meeting_type,
            transcript=transcript_text,
            file_path=file_path,
            ai_output=json.dumps(ai_result)
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'meeting_id': meeting.id,
            'result': ai_result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/meeting/<meeting_id>')
def view_meeting(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    return render_template('result.html', meeting=meeting.to_dict())

@app.route('/history')
def history():
    meetings = Meeting.query.order_by(Meeting.created_at.desc()).all()
    return render_template('history.html', meetings=meetings)

@app.route('/api/meetings', methods=['GET'])
def get_meetings():
    meetings = Meeting.query.order_by(Meeting.created_at.desc()).all()
    return jsonify([meeting.to_dict() for meeting in meetings])

@app.route('/api/meetings/<meeting_id>', methods=['GET'])
def get_meeting(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    return jsonify(meeting.to_dict())

@app.route('/api/meetings/<meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    # Delete associated file
    if meeting.file_path and os.path.exists(meeting.file_path):
        os.remove(meeting.file_path)
    
    db.session.delete(meeting)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/download/<meeting_id>/<format>')
def download_summary(meeting_id, format):
    meeting = Meeting.query.get_or_404(meeting_id)
    
    if format == 'txt':
        content = generate_text_summary(meeting)
        filename = f"{meeting.title.replace(' ', '_')}_{meeting.id[:8]}.txt"
        return send_file(
            content,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
    elif format == 'pdf':
        pdf_content = generate_pdf_summary(meeting)
        filename = f"{meeting.title.replace(' ', '_')}_{meeting.id[:8]}.pdf"
        return send_file(
            pdf_content,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    
    abort(400)

def generate_text_summary(meeting):
    """Generate text summary for download"""
    ai_data = json.loads(meeting.ai_output) if meeting.ai_output else {}
    
    text = f"Meeting Summary: {meeting.title}\n"
    text += f"Type: {meeting.meeting_type}\n"
    text += f"Date: {meeting.created_at}\n"
    text += "="*50 + "\n\n"
    
    text += "SUMMARY:\n"
    text += ai_data.get('summary', '') + "\n\n"
    
    text += "KEY POINTS:\n"
    for i, point in enumerate(ai_data.get('key_points', []), 1):
        text += f"{i}. {point}\n"
    text += "\n"
    
    text += "DECISIONS:\n"
    for i, decision in enumerate(ai_data.get('decisions', []), 1):
        text += f"{i}. {decision}\n"
    text += "\n"
    
    text += "ACTION ITEMS:\n"
    for i, action in enumerate(ai_data.get('action_items', []), 1):
        owner = action.get('owner', 'Unassigned')
        due_date = action.get('due_date', 'No due date')
        text += f"{i}. {action.get('task', '')} | Owner: {owner} | Due: {due_date}\n"
    text += "\n"
    
    text += "AGENDA BREAKDOWN:\n"
    for i, topic in enumerate(ai_data.get('agenda', []), 1):
        text += f"{i}. {topic.get('topic', '')}: {topic.get('summary', '')}\n"
    
    return text

def generate_pdf_summary(meeting):
    """Generate PDF summary using reportlab"""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    story.append(Paragraph(f"Meeting Summary: {meeting.title}", title_style))
    
    # Meeting Info
    info_style = styles["Normal"]
    story.append(Paragraph(f"<b>Type:</b> {meeting.meeting_type}", info_style))
    story.append(Paragraph(f"<b>Date:</b> {meeting.created_at}", info_style))
    story.append(Spacer(1, 20))
    
    ai_data = json.loads(meeting.ai_output) if meeting.ai_output else {}
    
    # Add sections
    sections = [
        ("SUMMARY", ai_data.get('summary', '')),
        ("KEY POINTS", '\n'.join([f"• {p}" for p in ai_data.get('key_points', [])])),
        ("DECISIONS", '\n'.join([f"• {d}" for d in ai_data.get('decisions', [])]))
    ]
    
    for section_title, content in sections:
        story.append(Paragraph(f"<b>{section_title}</b>", styles['Heading2']))
        story.append(Paragraph(content, info_style))
        story.append(Spacer(1, 15))
    
    # Action Items Table
    action_items = ai_data.get('action_items', [])
    if action_items:
        story.append(Paragraph("<b>ACTION ITEMS</b>", styles['Heading2']))
        data = [['Task', 'Owner', 'Due Date']]
        for item in action_items:
            data.append([
                item.get('task', ''),
                item.get('owner', 'Unassigned'),
                item.get('due_date', 'Not specified')
            ])
        
        table = Table(data, colWidths=[250, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

@app.route('/api/join-meet', methods=['POST'])
def join_google_meet():
    """Join a Google Meet and record/transcribe"""
    try:
        data = request.json
        meet_url = data.get('meet_url')
        title = data.get('title', 'Google Meet Recording')
        meeting_type = data.get('type', 'Team meeting')
        
        if not meet_url:
            return jsonify({'success': False, 'error': 'Meet URL required'}), 400
        
        # Initialize Google Meet Bot
        bot = GoogleMeetBot()
        
        # Join meeting and record
        transcript = bot.join_and_record(meet_url)
        
        if not transcript:
            return jsonify({'success': False, 'error': 'Failed to get transcript'}), 500
        
        # Generate summary
        ai_result = ai_summarizer.generate_summary(transcript, meeting_type)
        
        # Save to database
        meeting = Meeting(
            title=title,
            meeting_type=meeting_type,
            transcript=transcript,
            ai_output=json.dumps(ai_result)
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'meeting_id': meeting.id,
            'result': ai_result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
from app import app, db
from datetime import datetime
import json

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database initialized!")
        
        # Add sample data for testing
        add_sample_data()

def add_sample_data():
    from app import Meeting
    
    # Check if sample data already exists
    if Meeting.query.count() == 0:
        sample_meetings = [
            {
                'title': 'Q4 Planning Session',
                'meeting_type': 'Team meeting',
                'transcript': 'Team discussed Q4 goals and assigned tasks. John will handle the marketing campaign. Sarah will prepare the technical documentation. Budget approved for new hires.',
                'ai_output': json.dumps({
                    'summary': 'The team planned Q4 objectives, assigned responsibilities, and approved budget allocations.',
                    'key_points': [
                        'Q4 goals were finalized',
                        'Marketing campaign assigned to John',
                        'Technical documentation assigned to Sarah',
                        'Budget approved for 2 new hires'
                    ],
                    'decisions': [
                        'Approved Q4 roadmap',
                        'Hiring freeze lifted for two positions',
                        'Marketing budget increased by 15%'
                    ],
                    'action_items': [
                        {'task': 'Create marketing campaign', 'owner': 'John Doe', 'due_date': '2024-12-15'},
                        {'task': 'Prepare technical docs', 'owner': 'Sarah Smith', 'due_date': '2024-12-10'},
                        {'task': 'Post job openings', 'owner': 'HR Team', 'due_date': '2024-12-05'}
                    ],
                    'agenda': [
                        {'topic': 'Q4 Goals', 'summary': 'Discussed and finalized quarterly objectives'},
                        {'topic': 'Resource Allocation', 'summary': 'Assigned tasks and discussed team capacity'},
                        {'topic': 'Budget Review', 'summary': 'Reviewed and approved Q4 budget'}
                    ]
                })
            },
            {
                'title': 'Client Project Kickoff',
                'meeting_type': 'Client call',
                'transcript': 'Discussed project requirements with ABC Corp. Timeline set for 6 months. Weekly status meetings agreed upon. Final delivery by June 2024.',
                'ai_output': json.dumps({
                    'summary': 'Kickoff meeting with ABC Corp to establish project timeline and communication protocols.',
                    'key_points': [
                        'Project timeline: 6 months',
                        'Weekly status meetings scheduled',
                        'Final delivery date: June 30, 2024',
                        'Key stakeholders identified'
                    ],
                    'decisions': [
                        'Approved project scope',
                        'Agreed on communication cadence',
                        'Set up project management tools'
                    ],
                    'action_items': [
                        {'task': 'Send project charter', 'owner': 'Project Manager', 'due_date': '2024-01-15'},
                        {'task': 'Setup project repo', 'owner': 'Tech Lead', 'due_date': '2024-01-12'},
                        {'task': 'Schedule weekly sync', 'owner': 'Coordinator', 'due_date': '2024-01-10'}
                    ],
                    'agenda': [
                        {'topic': 'Project Overview', 'summary': 'Discussed project goals and deliverables'},
                        {'topic': 'Timeline', 'summary': 'Established 6-month project timeline'},
                        {'topic': 'Communication Plan', 'summary': 'Agreed on weekly status meetings'}
                    ]
                })
            }
        ]
        
        for meeting_data in sample_meetings:
            meeting = Meeting(
                title=meeting_data['title'],
                meeting_type=meeting_data['meeting_type'],
                transcript=meeting_data['transcript'],
                ai_output=meeting_data['ai_output']
            )
            db.session.add(meeting)
        
        db.session.commit()
        print("Sample data added!")

if __name__ == '__main__':
    init_database()
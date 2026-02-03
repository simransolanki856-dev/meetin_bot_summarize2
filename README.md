# Meeting Bot Summarizer Web App

A comprehensive web application for automatically summarizing meeting recordings and transcripts using AI. Features include file upload, Google Meet integration, and structured output generation.

## Features

- **File Upload**: Upload MP3, WAV, MP4 meeting recordings
- **Transcript Input**: Paste existing meeting transcripts
- **Google Meet Integration**: Bot joins meetings and captures discussions
- **AI-Powered Summarization**: Uses OpenAI GPT or Google Gemini
- **Structured Output**:
  - Meeting summary
  - Key discussion points
  - Decisions made
  - Action items with owners
  - Agenda/topic-wise breakdown
- **Export Options**: Download as TXT or PDF
- **Meeting History**: Searchable history with filtering
- **Responsive UI**: Mobile-friendly interface

## Tech Stack

- **Backend**: Python Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Database**: SQLite
- **AI Integration**: OpenAI API / Google Gemini API
- **Audio Processing**: Whisper, SpeechRecognition, pydub
- **PDF Generation**: ReportLab

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/meeting-bot-summarizer.git
   cd meeting-bot-summarizer
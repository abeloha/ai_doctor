# AI Personal Doctor for Nigerians

## Overview

The AI Personal Doctor is a healthcare chatbot designed to provide medical advice and assistance to Nigerians. It leverages Streamlit for the frontend, a Large Language Model (LLM) for AI-driven responses, and a MySQL database for storing user data. The system enables users to receive health-related insights, track symptoms, and get preliminary diagnoses.

## Features

- **AI-powered Medical Consultation**: Provides health-related insights based on user queries.
- **User Authentication**: Secure login and session management.
- **Chat System**: Interactive chat interface for seamless communication.
- **Session State Management**: Maintains user session and history.
- **MySQL Database**: Stores user interactions and relevant medical data.

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python with LLM integration
- **Database**: MySQL

## Project Structure

```
chat_app/
│── app.py          # Main entry point
│── auth.py         # Authentication logic
│── chat.py         # Chat logic
│── state.py        # Handles session state
```

## Installation

### Prerequisites

Ensure you have the following installed:

- Python 3.x
- MySQL Server

### Steps

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/ai-personal-doctor.git
   cd ai-personal-doctor/chat_app
   ```

2. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Set up MySQL Database:
   - Create a new database
   - Configure database connection in the project

4. Run the application:

   ```sh
   streamlit run app.py
   ```

## Usage

1. Open the Streamlit app in your browser.
2. Sign up or log in.
3. Start chatting with the AI Personal Doctor.
4. Get health advice and recommendations.

## Future Enhancements

- Integration with electronic medical records.
- Multi-language support for Nigerian dialects.
- Advanced AI diagnostics based on user medical history.

## Contributing

We welcome contributions! Please open an issue or submit a pull request.

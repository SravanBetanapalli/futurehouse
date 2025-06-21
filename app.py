from flask import Flask, request, jsonify, send_from_directory
from futurehouse_client import FutureHouseClient, JobNames
from futurehouse_client.models import TaskRequest
import re
import string
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load API Key from environment
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("No API_KEY set for Flask application. Please create a .env file with API_KEY=<your_key>.")

client = FutureHouseClient(api_key=API_KEY)

def clean_futurehouse_response(text: str) -> str:
    if not isinstance(text, str):
        return text
    # Remove non-printable/control characters
    text = ''.join(ch for ch in text if ch in string.printable)
    # Replace multiple spaces/newlines/tabs with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/ask_crow', methods=['POST'])
def ask_crow():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'error': 'Missing question'}), 400
    task_data = TaskRequest(
        name=JobNames.from_string("crow"),
        query=question,
    )
    task_responses = client.run_tasks_until_done(task_data)
    task_response = task_responses[0]
    cleaned_answer = clean_futurehouse_response(task_response.formatted_answer)
    return jsonify({
        'status': task_response.status,
        'answer': cleaned_answer
    })

@app.route('/ask_falcon', methods=['POST'])
def ask_falcon():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'error': 'Missing question'}), 400
    task_data = TaskRequest(
        name=JobNames.from_string("falcon"),
        query=question,
    )
    task_responses = client.run_tasks_until_done(task_data)
    task_response = task_responses[0]
    cleaned_answer = clean_futurehouse_response(task_response.formatted_answer)
    return jsonify({
        'status': task_response.status,
        'answer': cleaned_answer
    })

@app.route('/ask_phoenix', methods=['POST'])
def ask_phoenix():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'error': 'Missing question'}), 400
    task_data = TaskRequest(
        name=JobNames.from_string("phoenix"),
        query=question,
    )
    task_responses = client.run_tasks_until_done(task_data)
    task_response = task_responses[0]
    cleaned_answer = clean_futurehouse_response(task_response.answer)
    return jsonify({
        'status': task_response.status,
        'answer': cleaned_answer
    })

@app.route('/ask_owl', methods=['POST'])
def ask_owl():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'error': 'Missing question'}), 400
    task_data = TaskRequest(
        name=JobNames.from_string("owl"),
        query=question,
    )
    task_responses = client.run_tasks_until_done(task_data)
    task_response = task_responses[0]
    cleaned_answer = clean_futurehouse_response(task_response.formatted_answer)
    return jsonify({
        'status': task_response.status,
        'answer': cleaned_answer
    })

@app.route('/ask_multi', methods=['POST'])
def ask_multi():
    data = request.get_json()
    tasks = data.get('tasks')
    if not tasks or not isinstance(tasks, list):
        return jsonify({'error': 'Missing or invalid tasks list'}), 400

    results = []
    for task in tasks:
        agent = task.get('agent')
        question = task.get('question')
        if not agent or not question:
            results.append({'error': 'Missing agent or question', 'agent': agent, 'question': question})
            continue
        try:
            task_data = TaskRequest(
                name=JobNames.from_string(agent),
                query=question,
            )
            task_response = client.run_tasks_until_done(task_data)[0]
            # Use correct field for answer
            if agent.lower() == 'phoenix':
                answer = task_response.answer
            else:
                answer = getattr(task_response, 'formatted_answer', task_response.answer)
            cleaned_answer = clean_futurehouse_response(answer)
            results.append({
                'agent': agent,
                'status': task_response.status,
                'answer': cleaned_answer
            })
        except Exception as e:
            results.append({'agent': agent, 'error': str(e)})
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True)

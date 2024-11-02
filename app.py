import re
from flask import Flask, request, jsonify, render_template
import subprocess

app = Flask(__name__)

def clean_output(output):
    """Removes ANSI escape codes from the output."""
    return re.sub(r'\x1B\[[0-?9;]*[mK]', '', output)

def interact_with_model(prompt):
    command = ["ollama", "run", "llama3.2:latest", prompt]

    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
        output_lines = []
        try:
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    output_lines.append(output.strip())
            
            # Collect any remaining output
            remaining_output = process.stdout.read()
            if remaining_output:
                output_lines.append(remaining_output.strip())
        
        except Exception as e:
            # Clean the error message before returning
            return clean_output(f"An error occurred while processing: {str(e)}")
        
        _, error = process.communicate()
        if error:
            # Clean the error message before appending
            output_lines.append(clean_output(f"Error occurred: {error.strip()}"))
        
    # Clean the combined output before returning
    output_cleaned = clean_output("\n".join(output_lines))
    return output_cleaned

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/interact', methods=['POST'])
def interact():
    data = request.json
    prompt = data.get('prompt', '')
    if prompt:
        response = interact_with_model(prompt)
        return jsonify({'response': response})
    else:
        return jsonify({'error': 'No prompt provided'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)
    

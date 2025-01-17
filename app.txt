from flask import Flask, render_template, request, jsonify
from zoho_query import ZohoCRMQueryProcessor
import logging
from logging.handlers import RotatingFileHandler
import os

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Initialize Flask app
app = Flask(__name__)

# Configure logging
def setup_logging():
    # Set up file handler
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Configure app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    app.logger.info('Application startup')

@app.route('/')
def index():
    app.logger.info('Index page accessed')
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def process_query():
    try:
        data = request.json
        natural_query = data.get('query')
        
        if not natural_query:
            app.logger.warning('Empty query received')
            return jsonify({'status': 'error', 'message': 'No query provided'}), 400
            
        app.logger.info(f'Processing query: {natural_query}')
        
        # Create instance of ZohoCRMQueryProcessor and process the query
        processor = ZohoCRMQueryProcessor()
        result = processor.process_query(natural_query)
        
        # Add more detailed logging
        app.logger.info(f'Raw result from query_zoho_crm: {result}')
        
        if result.get('status') == 'error':
            app.logger.error(f'Zoho query failed: {result.get("message")}')
            return jsonify(result), 500
        
        app.logger.info(f'Query processed successfully with {len(result.get("results", {}).get("records", []))} records')
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f'Error processing query: {str(e)}', exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'Error processing query: {str(e)}'
        }), 500

if __name__ == '__main__':
    setup_logging()
    app.run(debug=True)
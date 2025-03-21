from flask import Flask, jsonify, request, send_from_directory, render_template
import logging
import json
import os
import threading

import archive_utils

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main template with like button injected"""
    return render_template('index.html')

@app.route('/archive')
def archive_page():
    """Serve the archive template"""
    return send_from_directory('templates', 'archive.html')

@app.route('/api/likes', methods=['GET'])
def get_likes():
    """API endpoint to get current like count"""
    page_id = request.args.get('pageId', default='default')
    count = archive_utils.get_like_count(page_id)
    return jsonify({"count": count})

@app.route('/api/archive', methods=['GET'])
def get_archive_json():
    """API endpoint to get portfolio archive"""
    archive = archive_utils.get_archive_list()
    return jsonify({"archive": archive})

@app.route('/api/likes', methods=['POST'])
def increment_likes():
    """API endpoint to increment like count"""
    print(request.json)
    page_id = request.json.get('pageId', 'default')
    count = archive_utils.get_like_count(page_id) + 1
    archive_utils.save_like_count(count, page_id)
    return jsonify({"count": count})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port, debug=True)
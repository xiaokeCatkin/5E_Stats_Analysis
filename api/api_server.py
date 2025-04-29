from flask import Flask, request, jsonify
import subprocess
import os
import sys
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import shutil

app = Flask(__name__)
CORS(app)  

@app.route('/api/fetch_stats', methods=['POST'])
def fetch_stats():
    try:
        data = request.get_json()
        # 获取所有需要的参数
        params = {
            'uuid': data.get('uuid'),
            'start_time': data.get('start_time', 1000000000),
            'end_time': data.get('end_time', 9999999999),
            'limit': data.get('limit', 3),
            'max_pages': data.get('max_pages', 3),
            'match_type': data.get('match_type', -1),
            'cs_type': data.get('cs_type', 0),
            'date': data.get('date', 0)
        }
        
        if not params['uuid']:
            return jsonify({'success': False, 'message': '缺少UUID参数'}), 400
        
        # 执行Python脚本并传递参数
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Get_Stats', 'main_script.py')
        
        # 构建命令行参数
        args = ['python', script_path]
        for key, value in params.items():
            args.extend([f'--{key}', str(value)])
            
        result = subprocess.run(
            args,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': '数据获取成功，已保存在stats_saved目录下',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'message': '脚本执行失败',
                'error': result.stderr
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)+'\n 可能是UUID错误，请检查UUID'
        }), 500

@app.route('/api/analyze_stats', methods=['POST'])
def analyze_stats():
    try:
        if 'statsFile' not in request.files or 'templateFile' not in request.files:
            return jsonify({'success': False, 'message': '缺少文件参数'}), 400
            
        stats_file = request.files['statsFile']
        template_file = request.files['templateFile']
        
        if stats_file.filename == '' or template_file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'}), 400
            
        # 创建临时目录保存上传的文件
        temp_dir = tempfile.mkdtemp()
        stats_path = os.path.join(temp_dir, secure_filename(stats_file.filename))
        template_path = os.path.join(temp_dir, secure_filename(template_file.filename))
        
        stats_file.save(stats_path)
        template_file.save(template_path)
        
        # 改为命令行调用
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'llm_analysis.py')
        args = ['python', script_path, '--data', stats_path, '--template', template_path]
        
        # 从请求中获取model_name参数，默认为gpt-4
        model_name = request.form.get('model_name', 'gpt-4')
        args.extend(['--model', model_name])
        
        result = subprocess.run(
            args,
            capture_output=True,
            text=True
        )
        
        # 清理临时文件
        shutil.rmtree(temp_dir)
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': '分析成功',
                'analysis': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'message': '分析失败',
                'error': result.stderr
            }), 500
            
    except Exception as e:
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=5000)
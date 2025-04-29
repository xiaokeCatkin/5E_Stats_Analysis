import json
import pandas as pd
from openai import OpenAI
from pathlib import Path
from datetime import datetime
import os
import argparse  # 新增导入

# PATH = os.path.dirname(os.path.dirname(__file__))
PATH = os.path.dirname(__file__)

class CSGOPerformanceAnalyzer:
    def __init__(self, model_name="gemini-2.5-pro-exp-03-25"):
        self.client = OpenAI()
        self.model_name = model_name

    def load_template(self, template_path):
        """加载大模型模板文件"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"未找到模板文件: {template_path}")

    def load_data(self, file_path):
        """加载战绩数据文件"""
        file_path = Path(file_path)
        if file_path.suffix == '.csv':
            return pd.read_csv(file_path)
        else:
            raise ValueError("仅支持CSV格式的战绩数据文件")

    def analyze_data(self, data, template, ):
        """使用大模型分析原始数据"""
        # 将数据转换为字符串格式
        data_str = data.to_string() if isinstance(data, pd.DataFrame) else str(data)
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": template},
                {"role": "user", "content": f"请根据以下比赛数据来生成点评:\n{data_str}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content

    def save_result(self, analysis_text):
        """保存分析结果"""
        os.makedirs('result', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"result/result_{timestamp}.txt"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(analysis_text)
        return output_path

    def save_html_result(self, analysis_text):
        """保存为HTML格式的分析结果"""
        os.makedirs('result', exist_ok=True)
        
        import re
        if re.search(r'```html', analysis_text):
            html_content = re.sub(r'```html', '', analysis_text)
        if re.search(r'```', analysis_text):
            html_content = re.sub(r'```', '', html_content)
        # 保存HTML文件
        output_path = f"result/result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return output_path

def main(model_name="gemini-2.5-pro-exp-03-25", 
    data_file=os.path.join(PATH, 'stats_saved\\csgo_report_matches.csv'), 
    template_file=os.path.join(PATH,'templates\\template_default.txt'),
    output_file=None):  # 新增output_file参数
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='CSGO战绩数据分析工具')
    parser.add_argument('--model', default=model_name, help='使用的模型名称')
    parser.add_argument('--data', default=data_file, help='战绩数据文件路径')
    parser.add_argument('--template', default=template_file, help='模板文件路径')
    parser.add_argument('--output', default=output_file, help='输出文件路径(可选)')
    args = parser.parse_args()

    analyzer = CSGOPerformanceAnalyzer(model_name=args.model)

    try:
        # 加载数据
        data = analyzer.load_data(args.data)
        template = analyzer.load_template(args.template)
        
        # 分析数据
        analysis = analyzer.analyze_data(data, template)
        
        # 保存结果
        output_path = f"result/result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        analyzer.save_html_result(analysis)  # 保存为HTML格式
        print(f"\n分析完成，结果已保存到: {output_path}")
        
        return analysis  # 返回分析结果
    except Exception as e:
        print(f"发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()
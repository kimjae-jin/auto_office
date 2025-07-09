# app/services/pdf_creator.py
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

def create_pdf_from_template(data: dict, template_name: str, output_filename: str):
    """템플릿과 데이터를 사용하여 PDF 파일을 생성합니다."""
    # 템플릿 폴더 경로 설정
    env = Environment(loader=FileSystemLoader('app/templates/'))
    template = env.get_template(template_name)
    
    # 데이터로 HTML 렌더링
    html_out = template.render(data)
    
    # PDF 생성
    # 프로젝트 폴더의 절대 경로를 기본 URL로 설정하여 이미지(직인) 경로 문제를 해결
    base_url = os.path.dirname(os.path.abspath(__file__))
    
    HTML(string=html_out, base_url=base_url).write_pdf(
        output_filename
    )
    print(f"   -> PDF 파일 생성 완료: {output_filename}")


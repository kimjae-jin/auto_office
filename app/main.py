from app.services.database import init_database, get_full_contract_details
from app.services.pdf_creator import create_pdf_from_template
import os

def generate_final_report(contract_id: int):
    print(f"--- [최종] 계약 ID {contract_id}의 착수신고서 생성을 시작합니다. ---")
    full_data = get_full_contract_details(contract_id)
    if not full_data:
        print(f"[오류] 계약 ID {contract_id}를 찾을 수 없습니다."); return

    output_dir = "생성된문서"
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"[최종착수계_v3] {full_data['project_name']}.pdf")
    
    print("PDF 생성을 시작합니다...")
    create_pdf_from_template(
        data=full_data,
        template_name="final_report_v2.html", # 이름은 v2이지만 내용은 최신입니다.
        output_filename=output_file
    )
    print(f"성공적으로 '{output_file}' 파일을 생성했습니다.")

if __name__ == '__main__':
    print("시스템 초기화: 데이터베이스 설정 중...")
    init_database()
    print("데이터베이스 준비 완료.\n")
    
    generate_final_report(contract_id=1)

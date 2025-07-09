from app.services.database import init_database, get_full_contract_details
from app.services.pdf_creator import create_pdf_from_template

def generate_full_commencement_report(contract_id: int):
    print(f"--- [고급] 계약 ID {contract_id}의 착수신고서 생성을 시작합니다. ---")
    
    # 1. DB에서 계약, 참여자, 공정표 등 모든 정보 가져오기
    full_data = get_full_contract_details(contract_id)
    if not full_data:
        print(f"[오류] 계약 ID {contract_id}를 찾을 수 없습니다.")
        return
    print("   -> DB에서 모든 관련 정보 조회 및 복호화 완료.")

    # 2. PDF 생성
    output_file = f"[착수신고서] {full_data['project_name']}.pdf"
    print("   -> PDF 파일 생성을 시작합니다...")
    create_pdf_from_template(
        data=full_data,
        template_name="commencement_report_advanced.html",
        output_filename=output_file
    )
    print(f"✅ 성공적으로 '{output_file}' 파일을 생성했습니다.")

if __name__ == '__main__':
    print("--- 시스템 초기화: 데이터베이스 설정 ---")
    init_database()
    print("--- 데이터베이스 준비 완료 ---\n")
    
    generate_full_commencement_report(contract_id=1)

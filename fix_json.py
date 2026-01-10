import json
import re

# 파일 이름이 정확한지 확인하세요
FILE_PATH = "database2.json"

def fix_json():
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        print("🔧 파일 수정을 시작합니다...")

        # 1. 마크다운 기호(```json 등) 제거
        content = re.sub(r"```json", "", content)
        content = re.sub(r"```", "", content)

        # 2. 중간에 끊긴 대괄호(] [)를 쉼표(,)로 연결
        # 예: ...}] [{...  ->  ...}, {...
        content = re.sub(r"\]\s*\[", ", ", content)

        # 3. 양끝 공백 제거
        content = content.strip()

        # 4. 맨 앞이 [ 로 시작하지 않으면 추가
        if not content.startswith("["):
            content = "[" + content
        
        # 5. 맨 뒤가 ] 로 끝나지 않으면 추가
        if not content.endswith("]"):
            content = content + "]"

        # 6. JSON 유효성 검사 (잘 고쳐졌는지 테스트)
        parsed_data = json.loads(content)
        print(f"✅ 성공! 총 {len(parsed_data)}개의 문제가 확인되었습니다.")

        # 7. 예쁘게 다시 저장
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            
        print("🎉 database2.json 파일이 정상적으로 복구되었습니다!")

    except Exception as e:
        print(f"❌ 수정 중 오류 발생: {e}")
        print("파일 내용을 직접 확인해보셔야 할 것 같습니다.")

if __name__ == "__main__":
    fix_json()
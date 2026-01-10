import json
import re
import os

FILE_PATH = "database2.json"

def fix_json_latex():
    if not os.path.exists(FILE_PATH):
        print(f"❌ '{FILE_PATH}' 파일이 없습니다.")
        return

    print("🔧 수학 기호(\\) 오류를 수정 중입니다...")

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 마크다운 기호 제거 (혹시 남아있다면)
    content = re.sub(r"```json", "", content)
    content = re.sub(r"```", "", content)

    # 2. 끊긴 대괄호 연결 (] [ -> ,)
    content = re.sub(r"\]\s*\[", ", ", content)

    # 3. 주요 수학 기호 역슬래시(\)를 두 개(\\)로 변경
    # \times -> \\times, \sigma -> \\sigma 등으로 치환
    # (이미 \\로 되어있는 건 건드리지 않음)
    
    latex_keywords = [
        "times", "sigma", "sqrt", "frac", "mu", "le", "ge", "ne", 
        "approx", "sum", "prod", "int", "alpha", "beta", "gamma", 
        "delta", "theta", "lambda", "pi", "rho", "phi", "omega"
    ]
    
    for word in latex_keywords:
        # (?<!\\)는 앞에 \가 없는 경우만 찾는다는 뜻 (이미 \\times면 무시)
        pattern = r'(?<!\\)\\' + word
        replacement = r'\\\\' + word
        content = re.sub(pattern, replacement, content)

    # 4. f' (미분 기호 등) 처리: \f는 폼피드(form feed)로 인식될 수 있음
    content = re.sub(r'(?<!\\)\\f', r'\\\\f', content)

    # 5. 양끝 공백 제거 및 대괄호 확인
    content = content.strip()
    if not content.startswith("["): content = "[" + content
    if not content.endswith("]"): content = content + "]"

    # 6. JSON 검증 및 저장
    try:
        data = json.loads(content)
        print(f"✅ 수리 완료! 총 {len(data)}개의 문제가 정상적으로 인식됩니다.")
        
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"🎉 '{FILE_PATH}' 파일이 완벽하게 저장되었습니다.")
        
    except json.JSONDecodeError as e:
        print("❌ 자동 수정 실패. 여전히 오류가 있습니다.")
        print(f"에러 메시지: {e}")
        # 에러 위치 주변 출력
        if hasattr(e, 'pos'):
            start = max(0, e.pos - 50)
            end = min(len(content), e.pos + 50)
            print(f"👉 문제 구간 미리보기: ...{content[start:end]}...")

if __name__ == "__main__":
    fix_json_latex()
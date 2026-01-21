import streamlit as st
import datetime
import io
import base64

# 라이브러리 체크
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    st.error("Pillow가 설치되지 않았습니다.")
    st.stop()

# -----------------------------------------------------------------------------
# 1. 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(page_title="우성어닝 견적 시스템", page_icon="⛺", layout="wide")

# 사장님 정보
MY_BUSINESS_NUM = "465-02-03270"        
MY_BANK_INFO = "기업은행 323-077581-01-014 (김우성)" 

# -----------------------------------------------------------------------------
# 2. 데이터 (단가표)
# -----------------------------------------------------------------------------
price_data = {
    2.4: {'spec': '2암', 'prices': [384000, 426000, 0, 0, 0, 0]},
    3.0: {'spec': '2암', 'prices': [396000, 450000, 504000, 558000, 0, 0]},
    3.6: {'spec': '2암', 'prices': [414000, 462000, 516000, 570000, 636000, 0]},
    4.0: {'spec': '2암', 'prices': [426000, 480000, 546000, 594000, 660000, 0]},
    4.2: {'spec': '2암', 'prices': [438000, 492000, 558000, 612000, 678000, 756000]},
    4.8: {'spec': '2암', 'prices': [450000, 504000, 570000, 636000, 702000, 780000]},
    5.0: {'spec': '2암', 'prices': [462000, 528000, 594000, 660000, 726000, 810000]},
    5.4: {'spec': '2암1서', 'prices': [516000, 582000, 648000, 714000, 780000, 876000]},
    6.0: {'spec': '3암1서', 'prices': [636000, 714000, 780000, 858000, 942000, 1032000]},
    6.6: {'spec': '3암1서', 'prices': [702000, 780000, 858000, 942000, 1020000, 1122000]},
    7.2: {'spec': '3암1서', 'prices': [726000, 810000, 888000, 978000, 1056000, 1164000]},
    7.8: {'spec': '3암1서', 'prices': [744000, 834000, 912000, 990000, 1086000, 1188000]},
    8.4: {'spec': '4암2서', 'prices': [942000, 1032000, 1122000, 1218000, 1308000, 1440000]},
    9.0: {'spec': '4암2서', 'prices': [978000, 1056000, 1152000, 1242000, 1350000, 1482000]},
    9.6: {'spec': '4암2서', 'prices': [990000, 1086000, 1176000, 1284000, 1386000, 1518000]},
    10.2: {'spec': '5암3서', 'prices': [1152000, 1254000, 1374000, 1482000, 1584000, 1734000]},
    10.8: {'spec': '5암3서', 'prices': [1218000, 1320000, 1440000, 1548000, 1650000, 1812000]},
    11.4: {'spec': '5암3서', 'prices': [1242000, 1362000, 1482000, 1584000, 1704000, 1866000]},
    12.0: {'spec': '5암3서', 'prices': [1254000, 1374000, 1494000, 1614000, 1734000, 1890000]},
    12.6: {'spec': '5암3서', 'prices': [1452000, 1572000, 1704000, 1824000, 1956000, 2142000]},
    13.2: {'spec': '5암3서', 'prices': [1482000, 1614000, 1746000, 1866000, 1998000, 2178000]},
    13.8: {'spec': '5암3서', 'prices': [1494000, 1626000, 1758000, 1890000, 2022000, 2208000]},
    14.4: {'spec': '6암4서', 'prices': [1572000, 1704000, 1848000, 1980000, 2112000, 2310000]},
    15.0: {'spec': '6암4서', 'prices': [1584000, 1734000, 1878000, 2010000, 2154000, 2340000]}
}
projection_map = {1.0: 0, 1.5: 1, 2.0: 2, 2.5: 3, 3.0: 4, 3.5: 5}

# -----------------------------------------------------------------------------
# 3. 사이드바 입력
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⛺ 견적 정보 입력")

    # 로고 업로드
    st.markdown("### 🏢 회사 로고")
    uploaded_logo = st.file_uploader("로고 이미지 업로드 (선택)", type=['png', 'jpg', 'jpeg'])

    st.markdown("---")
    
    st.markdown("### A. 기본 규격")
    customer_name = st.text_input("고객명 (상호)", value="고객님")
    col1, col2 = st.columns(2)
    width_input = col1.number_input("가로 길이 (m)", min_value=2.4, step=0.1, value=4.0)
    proj_input = col2.selectbox("돌출 길이 (m)", options=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5], index=1)

    st.markdown("### B. 원단 설정")
    fabric_type = st.radio("원단 종류", ["국산 (방수)", "수입 (어닝전용)"], horizontal=True)
    fabric_price = st.number_input("원단 추가금 (원)", value=0, step=10000)

    st.markdown("### C. 구동 방식")
    drive_type = st.radio("구동 방식", ["수동 (핸들)", "전동 (리모컨)"], horizontal=True)
    motor_price = st.number_input("모터/부속 가격 (원)", value=0, step=10000)

    st.markdown("### D. 기본 옵션")
    use_print = st.checkbox("레이스 인쇄 (로고)")
    print_price = st.number_input("인쇄비 (원)", value=0 if not use_print else 30000, step=5000, disabled=not use_print)
    use_guard = st.checkbox("물받이 추가")
    guard_price = st.number_input("물받이 가격 (원)", value=0 if not use_guard else 30000, step=5000, disabled=not use_guard)

    st.markdown("### E. 시공비 및 부자재")
    labor_price = st.number_input("기본 시공비 (원)", value=250000, step=10000)
    material_price = st.number_input("부자재비용 (원)", value=0, step=5000, help="앙카, 실리콘, 피스 등 부속 자재 비용")

    st.markdown("---")
    st.markdown("### F. 현장 특수 조건 (추가 비용)")
    
    use_remove = st.checkbox("기존 어닝 철거/폐기")
    remove_price = st.number_input("철거비용 (원)", value=0 if not use_remove else 50000, step=10000, disabled=not use_remove)

    use_ladder = st.checkbox("장비 사용 (스카이/사다리차)")
    ladder_price = st.number_input("장비 사용료 (원)", value=0 if not use_ladder else 150000, step=10000, disabled=not use_ladder)

    use_bracket = st.checkbox("특수 브라켓/판넬 보강")
    bracket_price = st.number_input("보강 자재비 (원)", value=0 if not use_bracket else 30000, step=5000, disabled=not use_bracket)

    use_pole = st.checkbox("보조 기둥 (잭서포트) 설치")
    pole_price = st.number_input("기둥 설치비 (원)", value=0 if not use_pole else 100000, step=10000, disabled=not use_pole)

    st.markdown("---")
    st.markdown("### G. 기타/특이사항")
    note_input = st.text_input("비고 (메모)", value="")

# -----------------------------------------------------------------------------
# 4. 계산 로직
# -----------------------------------------------------------------------------
target_len = None
sorted_lengths = sorted(price_data.keys())
for l in sorted_lengths:
    if l >= width_input:
        target_len = l
        break

if target_len is None:
    st.error(f"❌ 가로 {width_input}m는 단가표 초과 (최대 15m)")
    st.stop()

spec_info = price_data[target_len]['spec']
proj_idx = projection_map[proj_input]
base_price = price_data[target_len]['prices'][proj_idx]

if base_price == 0:
    st.error(f"❌ {target_len}m x {proj_input}m 규격은 제작 불가")
    st.stop()

# 모든 비용 합산
sub_total = (base_price + fabric_price + motor_price + print_price + guard_price + 
             labor_price + material_price + 
             remove_price + ladder_price + bracket_price + pole_price)
vat = int(sub_total * 0.1)
total_price = sub_total + vat
today_str = datetime.datetime.now().strftime("%Y-%m-%d")

# -----------------------------------------------------------------------------
# 5. HTML 화면 출력 (세로 타원 도장 CSS 구현)
# -----------------------------------------------------------------------------
logo_html = ""
if uploaded_logo is not None:
    image_bytes = uploaded_logo.getvalue()
    encoded = base64.b64encode(image_bytes).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded}" style="max-height: 80px; max-width: 200px; margin-right: 20px;">'

# 세로 타원형 도장 (CSS)
stamp_html = """
<div style="
    display: inline-block;
    border: 3px solid red;
    border-radius: 50%;
    width: 18px;
    height: 25px;
    text-align: center;
    line-height: 0.5;
    color: red;
    font-weight: bold;
    font-size: 9px;
    margin-left: 1px;
    vertical-align: middle;
    padding-top: 3px;
">
    김<br>우<br>성
</div>
"""

html_content = f"""
<div style="background-color: white; padding: 40px; border: 1px solid #ddd; box-shadow: 0 4px 6px rgba(0,0,0,0.1); color: #333; font-family: 'Malgun Gothic', sans-serif; max-width: 800px; margin: auto;">
<div style="border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
<div style="display: flex; align-items: center;">
{logo_html}
<div style="font-size: 32px; font-weight: bold;">견 적 서</div>
</div>
<div style="text-align: right; font-size: 14px; line-height: 1.5;">
<strong>우성어닝천막공사 (WOCS)</strong><br>
<div style="display: flex; align-items: center; justify-content: flex-end;">
    <span>대표: 김우성</span> {stamp_html}
</div>
| 010-4337-0582<br>
사업자번호: {MY_BUSINESS_NUM}<br>
전남 화순군 사평면 유마로 592<br>
<span style="color: blue; font-weight: bold;">계좌: {MY_BANK_INFO}</span>
</div>
</div>
<div style="margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
<strong>수신:</strong> {customer_name} 귀하 <span style="float:right;"><strong>날짜:</strong> {today_str}</span>
</div>
<div style="font-size: 16px;">
<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;">
<span>🏷️ <strong>어닝 ({target_len} x {proj_input})</strong> / {spec_info}</span>
<span style="font-weight:bold;">{base_price:,} 원</span>
</div>
"""

# 옵션 항목들
if fabric_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🧵 원단 추가 ({fabric_type})</span><span>+{fabric_price:,} 원</span></div>"""
if motor_price > 0 or drive_type == "전동 (리모컨)":
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>⚙️ 구동 방식 ({drive_type})</span><span>+{motor_price:,} 원</span></div>"""
if use_print and print_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🎨 레이스 인쇄</span><span>+{print_price:,} 원</span></div>"""
if use_guard and guard_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>💧 물받이 추가</span><span>+{guard_price:,} 원</span></div>"""

# 현장 특수 항목
if use_remove and remove_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🏗️ 철거 및 폐기</span><span>+{remove_price:,} 원</span></div>"""
if use_ladder and ladder_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🚛 장비 사용 (스카이/사다리)</span><span>+{ladder_price:,} 원</span></div>"""
if use_bracket and bracket_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🔧 특수 브라켓/보강</span><span>+{bracket_price:,} 원</span></div>"""
if use_pole and pole_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🏛️ 보조 기둥 (잭서포트)</span><span>+{pole_price:,} 원</span></div>"""

# 시공비 및 부자재
html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>👷 기본 시공비</span><span>+{labor_price:,} 원</span></div>"""

if material_price > 0:
    html_content += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee;"><span>🔩 부자재비용</span><span>+{material_price:,} 원</span></div>"""

html_content += f"""
</div>
<div style="margin-top: 40px; text-align: right;">
<div style="font-size: 16px; color: #555; margin-bottom: 5px;">공급가액: {sub_total:,} 원</div>
<div style="font-size: 16px; color: #555; margin-bottom: 10px;">부가세(VAT): {vat:,} 원</div>
<div style="font-size: 28px; font-weight: bold; color: #d9534f; border-top: 2px solid #333; padding-top: 15px; display: inline-block;">총 견적 금액: {total_price:,} 원</div>
</div>
<div style="margin-top: 30px; font-size: 14px; color: #555; border-top: 1px dashed #ccc; padding-top: 20px;">
{'<strong>※ 특이사항:</strong> ' + note_input + '<br>' if note_input else ''}
<strong>1. 견적 유효기간:</strong> 견적일로부터 10일<br>
<strong>2. 하자 보증기간:</strong> 납품일로부터 1년 (천재지변 및 사용자 과실 제외)
</div>
<br><br>
<div style="text-align:center; color:#888; font-size:13px;">귀하의 무궁한 발전을 기원합니다.</div>
</div>
"""

st.markdown(html_content, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. 이미지 저장 (폰트 문제 완벽 해결 버전)
# -----------------------------------------------------------------------------
def create_image():
    width, height = 800, 1400
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 폰트 로드 순서: 나눔고딕(서버) -> 맑은고딕(로컬) -> 기본(깨짐방지)
    font_L = None
    font_M = None
    font_S = None
    font_Bold = None
    font_Stamp = None

    fonts_to_try = ["NanumGothic.ttf", "malgun.ttf", "AppleGothic.ttf"]
    
    for font_name in fonts_to_try:
        try:
            font_L = ImageFont.truetype(font_name, 40)
            font_M = ImageFont.truetype(font_name, 25)
            font_S = ImageFont.truetype(font_name, 20)
            font_Bold = ImageFont.truetype(font_name, 25) # 볼드체 없으면 일반체로 대체
            font_Stamp = ImageFont.truetype(font_name, 18)
            break # 성공하면 반복문 탈출
        except:
            continue
            
    # 만약 폰트를 하나도 못 찾았다면 기본 폰트 사용 (한글 깨질 수 있음)
    if font_L is None:
        font_L = ImageFont.load_default()
        font_M = ImageFont.load_default()
        font_S = ImageFont.load_default()
        font_Bold = ImageFont.load_default()
        font_Stamp = ImageFont.load_default()

    # 로고
    if uploaded_logo is not None:
        try:
            logo_img = Image.open(uploaded_logo)
            aspect_ratio = logo_img.width / logo_img.height
            new_height = 80
            new_width = int(new_height * aspect_ratio)
            logo_img = logo_img.resize((new_width, new_height))
            img.paste(logo_img, (50, 40))
        except:
            pass

    # 제목 및 상단 정보
    draw.text((320, 50), "견  적  서", font=font_L, fill="black")
    draw.line((50, 130, 750, 130), fill="black", width=2)
    
    draw.text((450, 150), "우성어닝천막공사 (WOCS)", font=font_Bold, fill="black")
    draw.text((450, 190), "대표: 김우성", font=font_S, fill="black")

    # ★★★ 진짜 세로 타원 도장 (이미지용) ★★★
    stamp_x = 580
    stamp_y = 175
    stamp_w = 40
    stamp_h = 65
    
    draw.ellipse((stamp_x, stamp_y, stamp_x + stamp_w, stamp_y + stamp_h), outline="red", width=3)
    draw.text((stamp_x + 11, stamp_y + 5), "김", font=font_Stamp, fill="red")
    draw.text((stamp_x + 11, stamp_y + 23), "우", font=font_Stamp, fill="red")
    draw.text((stamp_x + 11, stamp_y + 41), "성", font=font_Stamp, fill="red")

    draw.text((450, 220), f"사업자번호: {MY_BUSINESS_NUM}", font=font_S, fill="black")
    draw.text((450, 250), "전남 화순군 사평면 유마로 592", font=font_S, fill="black")
    draw.text((450, 280), "Tel: 010-4337-0582", font=font_S, fill="black")
    draw.text((450, 310), f"{MY_BANK_INFO}", font=font_S, fill="blue")

    draw.text((50, 170), f"수신: {customer_name} 귀하", font=font_M, fill="black")
    draw.text((50, 210), f"날짜: {today_str}", font=font_M, fill="black")

    line_y = 360
    draw.line((50, line_y, 750, line_y), fill="gray", width=1)
    y = line_y + 30
    def draw_row(name, price):
        nonlocal y
        draw.text((50, y), name, font=font_M, fill="black")
        draw.text((750, y), f"{price:,} 원", font=font_M, fill="black", anchor="ra")
        y += 50

    draw_row(f"어닝 ({target_len}m x {proj_input}m) {spec_info}", base_price)
    if fabric_price > 0: draw_row(f"원단 추가 ({fabric_type})", fabric_price)
    if motor_price > 0 or drive_type == "전동 (리모컨)": draw_row(f"구동 방식 ({drive_type})", motor_price)
    if use_print and print_price > 0: draw_row("레이스 인쇄", print_price)
    if use_guard and guard_price > 0: draw_row("물받이 추가", guard_price)
    
    if use_remove and remove_price > 0: draw_row("철거 및 폐기", remove_price)
    if use_ladder and ladder_price > 0: draw_row("장비 사용 (스카이/사다리)", ladder_price)
    if use_bracket and bracket_price > 0: draw_row("특수 브라켓/보강", bracket_price)
    if use_pole and pole_price > 0: draw_row("보조 기둥 (잭서포트)", pole_price)
    
    draw_row("기본 시공비", labor_price)
    if material_price > 0: draw_row("부자재비용", material_price)

    draw.line((50, y+10, 750, y+10), fill="black", width=2)
    y += 40
    draw.text((400, y), "공급가액:", font=font_S, fill="gray")
    draw.text((750, y), f"{sub_total:,} 원", font=font_S, fill="gray", anchor="ra")
    y += 30
    draw.text((400, y), "부가세(VAT):", font=font_S, fill="gray")
    draw.text((750, y), f"{vat:,} 원", font=font_S, fill="gray", anchor="ra")
    y += 50
    draw.text((400, y), "총 견적 금액:", font=font_Bold, fill="red")
    draw.text((750, y), f"{total_price:,} 원", font=font_Bold, fill="red", anchor="ra")
    
    y += 70
    if note_input:
        draw.text((50, y), f"※ 특이사항: {note_input}", font=font_S, fill="black")
        y += 40
    draw.text((50, y), "1. 견적 유효기간: 견적일로부터 10일", font=font_S, fill="gray")
    y += 30
    draw.text((50, y), "2. 하자 보증기간: 납품일로부터 1년 (천재지변 및 사용자 과실 제외)", font=font_S, fill="gray")
    
    y += 50
    draw.line((50, y, 750, y), fill="gray", width=1)
    y += 20
    draw.text((50, y), "위 견적 내용을 확인하였으며, 이에 승인하고 계약을 체결합니다.", font=font_S, fill="black")
    y += 40
    draw.text((400, y), "주문 승인 (서명): __________________", font=font_M, fill="black")

    y += 60
    draw.text((250, y), "귀하의 무궁한 발전을 기원합니다.", font=font_S, fill="gray")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

st.write("")
st.write("")
col_dn1, col_dn2 = st.columns([4, 1])
with col_dn2:
    st.download_button("💾 견적서 이미지 저장", create_image(), f"견적서_{customer_name}_{today_str}.png", "image/png", use_container_width=True)

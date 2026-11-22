Python
import os
import requests
from datetime import datetime, timedelta

API_KEY = os.environ["DATA_API_KEY"]

def fetch_and_build_html():
    url = "http://apis.data.go.kr/B552555/lhLeaseNoticeInfo1/lhLeaseNoticeInfo1"
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y.%m.%d")
    today_str = datetime.now().strftime("%Y.%m.%d")
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y.%m.%d")
    
    regions = {"11": "서울", "41": "경기", "28": "인천"}
    all_items = []

    for code, region_name in regions.items():
        params = {
            "serviceKey": API_KEY,
            "PG_SZ": "50",
            "PAGE": "1",
            "CNP_CD": code,
            "PAN_NT_ST_DT": start_date
        }
        try:
            res = requests.get(url, params=params, timeout=15)
            data = res.json()
            items = data[1].get("dsList", []) if isinstance(data, list) and len(data) > 1 else []
            for item in items:
                item["REGION_NAME"] = region_name
                all_items.append(item)
        except Exception as e:
            print(f"[{region_name}] 조회 오류: {e}")

    all_items.sort(key=lambda x: x.get("PAN_NT_ST_DT", ""), reverse=True)

    rows_html = ""
    for item in all_items:
        region = item.get("REGION_NAME", "")
        notice_type = item.get("AIS_TP_CD_NM", "임대")
        title = item.get("PAN_NM", "제목 없음")
        post_date = item.get("PAN_NT_ST_DT", "")
        close_date = item.get("CLSG_DT", "")
        status = item.get("PAN_SS", "")
        link = item.get("DTL_URL", "https://apply.lh.or.kr")

        is_new = post_date in [today_str, yesterday_str]
        new_badge = '<span class="badge-new">NEW</span>' if is_new else ""
        region_class = "badge-seoul" if region == "서울" else ("badge-gyeonggi" if region == "경기" else "badge-incheon")

        rows_html += f"""
        <tr data-region="{region}">
            <td><span class="badge {region_class}">{region}</span></td>
            <td class="type">{notice_type}</td>
            <td class="title">{new_badge}<a href="{link}" target="_blank">{title}</a></td>
            <td class="date">{post_date}</td>
            <td class="date">{close_date}</td>
            <td class="status">{status}</td>
        </tr>
        """

    update_time = (datetime.utcnow() + timedelta(hours=9)).strftime("%Y년 %m월 %d일 %H:%M")

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>수도권 공공임대 공고 현황판</title>
    <style>
        body {{ font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif; background: #f4f6f9; color: #222; margin: 0; padding: 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; background: #fff; padding: 24px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); }}
        h1 {{ font-size: 22px; margin: 0 0 8px 0; }}
        .sub {{ color: #666; font-size: 13px; margin-bottom: 20px; }}
        .filters {{ margin-bottom: 16px; display: flex; gap: 8px; flex-wrap: wrap; }}
        .btn {{ padding: 8px 14px; border: 1px solid #ddd; background: #fff; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; }}
        .btn.active {{ background: #1a73e8; color: #fff; border-color: #1a73e8; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        th, td {{ padding: 12px 10px; border-bottom: 1px solid #eee; text-align: left; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #444; }}
        tr:hover {{ background: #f9fbff; }}
        .title a {{ color: #111; text-decoration: none; font-weight: 500; }}
        .title a:hover {{ text-decoration: underline; color: #1a73e8; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 700; color: #fff; }}
        .badge-seoul {{ background: #e53935; }}
        .badge-gyeonggi {{ background: #1e88e5; }}
        .badge-incheon {{ background: #00897b; }}
        .badge-new {{ background: #ff6d00; color: #fff; font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 4px; margin-right: 6px; }}
        .date {{ color: #666; white-space: nowrap; font-size: 13px; }}
        @media (max-width: 768px) {{
            th:nth-child(2), td:nth-child(2), th:nth-child(6), td:nth-child(6) {{ display: none; }}
            body {{ padding: 10px; }}
            .container {{ padding: 15px; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>🏠 서울·수도권 공공임대 공고 현황판</h1>
    <div class="sub">최근 30일 이내 공고 기준 | 마지막 자동 업데이트: <b>{update_time}</b></div>
    
    <div class="filters">
        <button class="btn active" onclick="filterRegion('ALL', this)">전체 ({len(all_items)})</button>
        <button class="btn" onclick="filterRegion('서울', this)">서울</button>
        <button class="btn" onclick="filterRegion('경기', this)">경기</button>
        <button class="btn" onclick="filterRegion('인천', this)">인천</button>
    </div>

    <table>
        <thead>
            <tr>
                <th width="65">지역</th>
                <th width="110">유형</th>
                <th>공고명 (클릭 시 상세페이지 이동)</th>
                <th width="95">공고일</th>
                <th width="95">마감일</th>
                <th width="80">상태</th>
            </tr>
        </thead>
        <tbody id="notice-body">
            {rows_html if rows_html else '<tr><td colspan="6" style="text-align:center; padding:30px;">조회된 공고가 없습니다.</td></tr>'}
        </tbody>
    </table>
</div>

<script>
function filterRegion(region, btn) {{
    document.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('#notice-body tr').forEach(row => {{
        if (region === 'ALL' || row.dataset.region === region) {{
            row.style.display = '';
        }} else {{
            row.style.display = 'none';
        }}
    }});
}}
</script>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"총 {len(all_items)}건의 공고로 index.html 생성 완료")

if __name__ == "__main__":
    fetch_and_build_html()

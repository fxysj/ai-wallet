import streamlit as st
import requests
import sseclient
import json
import html
import re
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="AI旅行规划助手", page_icon="🧳")
st.title("✈️ AI旅行计划助手")

# CSS样式
st.markdown("""
<style>
    .poster {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .section-title {
        color: #2c3e50;
        border-left: 4px solid #3498db;
        padding-left: 1rem;
        margin: 1.5rem 0 1rem;
        font-size: 1.4em;
    }
    .day-plan {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
        position: relative;
        animation: fadeIn 0.6s ease-out;
    }
    .day-plan::after {
        content: "";
        display: block;
        height: 3px;
        background: linear-gradient(90deg, #3498db, #9b59b6);
        border-radius: 2px;
        margin-top: 1rem;
    }
    .recommendation-card {
        background: white;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 0.5rem;
        flex: 0 0 280px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }
    .flex-container {
        display: flex;
        gap: 1.2rem;
        overflow-x: auto;
        padding-bottom: 1rem;
    }
    .map-container {
        height: 320px;
        background: #f1f3f5;
        border-radius: 10px;
        margin: 1.5rem 0;
        overflow: hidden;
    }
    .price-tag {
        color: #27ae60;
        font-weight: 700;
        font-size: 1.3em;
        margin: 0.8rem 0;
    }
    .transport-info {
        color: #6c757d;
        font-size: 0.92em;
        line-height: 1.4;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .location-info {
        color: #495057;
        font-size: 0.95em;
        margin: 0.4rem 0;
    }
    .day-plan h3 {
        color: #212529;
        margin: 0 0 0.8rem;
        font-size: 1.25em;
        font-weight: 600;
    }
    .day-plan p {
        color: #495057;
        line-height: 1.7;
        margin: 0;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

def clean_html(text):
    """清理HTML标签并转义特殊字符"""
    if not text:
        return ""
    cleaned = re.sub(r'<[^>]+>', '', str(text))
    return html.escape(cleaned)

# -- 界面输入 --
user_input = st.text_area("请输入你的旅行需求，例如：我想去三亚旅游5天", height=100)
user_id = st.text_input("用户ID（user_id）", value="user123")

# -- 初始化Session State --
if "pdf_text" not in st.session_state:
    st.session_state["pdf_text"] = ""

# -- 按钮生成旅行计划 --
if st.button("生成旅行计划") and user_input:
    with st.spinner("正在生成您的专属旅行计划..."):
        try:
            response = requests.post(
                "http://localhost:8000/api/plan/stream",
                json={"user_input": user_input, "user_id": user_id},
                stream=True,
            )
            client = sseclient.SSEClient(response)

            poster_placeholder = st.empty()
            poster_content = """
            <div class="poster">
                <h1 style="color: #2c3e50; text-align: center; margin: 1rem 0 2rem; font-size: 1.8em;">
                ✨ 您的专属旅行计划 ✨
                </h1>
            """

            # 用于生成PDF文本
            pdf_text = "✨ 您的专属旅行计划 ✨\n\n"

            data_cache = {
                "plan_trip": {"plan": {}},
                "recommend_hotel": {"hotels": []},
                "recommend_flight": {"flights": []},
                "generate_map": {"map": {}}
            }

            for event in client.events():
                if event.data.strip() == "[DONE]":
                    break

                try:
                    data = json.loads(event.data)
                except json.JSONDecodeError:
                    continue

                for key in data:
                    if key in data_cache:
                        if isinstance(data[key], dict):
                            data_cache[key].update(data[key])
                        elif isinstance(data[key], list):
                            data_cache[key].extend(data[key])

                current_content = poster_content

                # --- 行程计划 ---
                if data_cache["plan_trip"].get("plan"):
                    current_content += "<h2 class='section-title'>📅 每日行程安排</h2>"
                    pdf_text += "📅 每日行程安排\n"
                    for day, plan in data_cache["plan_trip"]["plan"].items():
                        safe_day = clean_html(day)
                        safe_plan = clean_html(plan).replace('\n', '<br>')
                        current_content += f"""
                        <div class="day-plan">
                            <h3>{safe_day}</h3>
                            <p>{safe_plan}</p>
                        </div>
                        """
                        pdf_text += f"\n{day}\n{plan}\n"

                # --- 酒店推荐 ---
                if data_cache["recommend_hotel"].get("hotels"):
                    current_content += "<h2 class='section-title'>🏨 推荐住宿</h2><div class='flex-container'>"
                    pdf_text += "\n🏨 推荐住宿\n"
                    for hotel in data_cache["recommend_hotel"]["hotels"]:
                        hotel_data = {
                            "name": clean_html(hotel.get("name", "")),
                            "location": clean_html(hotel.get("location", "")),
                            "price": clean_html(hotel.get("price", "")),
                            "transportation": clean_html(hotel.get("transportation", "")),
                            "address": clean_html(hotel.get("address", ""))
                        }
                        current_content += f"""
                        <div class="recommendation-card">
                            <h4>{hotel_data['name']}</h4>
                            <p class="location-info">📍 {hotel_data['location']}</p>
                            <p class="price-tag">€{hotel_data['price']}/晚</p>
                            <p class="transport-info">🚕 {hotel_data['transportation']}</p>
                            <p style="font-size:0.88em;color:#868e96;">{hotel_data['address']}</p>
                        </div>
                        """
                        pdf_text += f"- {hotel_data['name']}（{hotel_data['location']}）: €{hotel_data['price']}/晚\n"

                    current_content += "</div>"

                # --- 航班推荐 ---
                if data_cache["recommend_flight"].get("flights"):
                    current_content += "<h2 class='section-title'>✈️ 推荐航班</h2><div class='flex-container'>"
                    pdf_text += "\n✈️ 推荐航班\n"
                    for flight in data_cache["recommend_flight"]["flights"]:
                        flight_data = {
                            "airline": clean_html(flight.get("airline", "")),
                            "departure": clean_html(flight.get("departure", "")),
                            "arrival": clean_html(flight.get("arrival", "")),
                            "price": clean_html(flight.get("price", ""))
                        }
                        current_content += f"""
                        <div class="recommendation-card">
                            <h4>{flight_data['airline']}</h4>
                            <p class="transport-info">🛫 出发: {flight_data['departure']}</p>
                            <p class="transport-info">🛬 到达: {flight_data['arrival']}</p>
                            <p class="price-tag">￥{flight_data['price']}</p>
                        </div>
                        """
                        pdf_text += f"- {flight_data['airline']}：{flight_data['departure']} -> {flight_data['arrival']} ￥{flight_data['price']}\n"
                    current_content += "</div>"

                # --- 地图 ---
                if data_cache["generate_map"].get("map", {}).get("map_url"):
                    map_url = clean_html(data_cache["generate_map"]["map"]["map_url"])
                    current_content += f"""
                    <h2 class='section-title'>🗺️ 行程地图</h2>
                    <div class="map-container">
                        <img src="{map_url}" 
                             style="width:100%; height:100%; object-fit: cover;"
                             alt="行程地图">
                    </div>
                    """
                    pdf_text += "\n🗺️ 行程地图（查看网页显示）\n"

                poster_placeholder.markdown(current_content + "</div>", unsafe_allow_html=True)

            # --- 保存PDF内容到session ---
            st.session_state["pdf_text"] = pdf_text

        except Exception as e:
            st.error(f"生成过程中出现错误: {e}")

# -- 下载PDF功能 --
def generate_pdf(pdf_text):
    pdf = FPDF()
    pdf.add_page()

    # Font setup
    font_path = "DejaVuSans.ttf"  # Make sure this font file exists in the correct location
    if os.path.exists(font_path):
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.set_font('DejaVu', '', 13)
    else:
        pdf.set_font('Arial', '', 13)  # Default font if custom font doesn't exist


    # Split long text into manageable lines
    max_line_length = 100  # Adjust based on page width and font size
    lines = [pdf_text[i:i+max_line_length] for i in range(0, len(pdf_text), max_line_length)]



    # Add content to PDF
    for line in lines:
        pdf.multi_cell(0, 10, line)

    # Temporary file for storing PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)
        tmpfile.close()  # Ensure file is closed before returning
        return tmpfile.name

def download_pdf(file_path):
    # Streamlit download button logic
    with open(file_path, "rb") as f:
        st.download_button(
            label="点击这里下载",
            data=f,
            file_name="travel_plan.pdf",
            mime="application/pdf",
        )

    # Clean up temporary file
    os.unlink(file_path)

if st.session_state.get("pdf_text"):
    if st.button("下载PDF文件 📄"):
        # Generate the PDF file
        pdf_file_path = generate_pdf(st.session_state["pdf_text"])

        # Handle the download action
        download_pdf(pdf_file_path)

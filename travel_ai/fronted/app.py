import streamlit as st
import requests
import sseclient
import json

st.set_page_config(page_title="AI旅行规划助手", page_icon="🧳")
st.title("✈️ AI旅行计划助手")

# 自定义CSS样式
st.markdown("""
<style>
    .poster {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .section-title {
        color: #2c3e50;
        border-left: 4px solid #3498db;
        padding-left: 1rem;
        margin: 1.5rem 0;
    }
    .day-plan {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .recommendation-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem;
        flex: 1;
        min-width: 250px;
    }
    .flex-container {
        display: flex;
        gap: 1rem;
        overflow-x: auto;
        padding-bottom: 1rem;
    }
    .map-container {
        height: 300px;
        background: #e0e0e0;
        border-radius: 10px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .price-tag {
        color: #27ae60;
        font-weight: bold;
        font-size: 1.2em;
        margin: 0.5rem 0;
    }
    .transport-info {
        color: #7f8c8d;
        font-size: 0.9em;
    }
    .location-info {
        color: #34495e;
        margin: 0.3rem 0;
    }
</style>
""", unsafe_allow_html=True)

user_input = st.text_area("请输入你的旅行需求，例如：我想去三亚旅游5天", height=100)
user_id = st.text_input("用户ID（user_id）", value="user123")

if st.button("生成旅行计划") and user_input:
    with st.spinner("生成中，请稍候..."):
        response = requests.post(
            "http://localhost:8000/api/plan/stream",
            json={"user_input": user_input, "user_id": user_id},
            stream=True,
        )
        client = sseclient.SSEClient(response)

        poster_placeholder = st.empty()
        poster_content = """
        <div class="poster">
            <h1 style="color: #2c3e50; text-align: center; margin-bottom: 2rem;">✨ 北极光之旅专属计划 ✨</h1>
        """

        try:
            data_cache = {}
            for event in client.events():
                if event.data.strip() == "[DONE]":
                    break
                data = json.loads(event.data)

                # 更新数据缓存
                if isinstance(data, dict):
                    for key in data:
                        if key in data_cache:
                            data_cache[key].update(data[key])
                        else:
                            data_cache[key] = data[key]

                # 实时更新海报内容
                current_content = poster_content

                # 行程计划部分
                if 'plan_trip' in data_cache and 'plan' in data_cache['plan_trip']:
                    current_content += "<h2 class='section-title'>📅 每日行程安排</h2>"
                    for day, plan in data_cache['plan_trip']['plan'].items():
                        current_content += f"""
                        <div class="day-plan">
                            <h3>{day}</h3>
                            <p>{plan.replace('\n', '<br>')}</p>
                        </div>
                        """

                # 酒店推荐部分
                if 'recommend_hotel' in data_cache and 'hotels' in data_cache['recommend_hotel']:
                    current_content += "<h2 class='section-title'>🏨 推荐住宿</h2><div class='flex-container'>"
                    for hotel in data_cache['recommend_hotel']['hotels']:
                        current_content += f"""
                        <div class="recommendation-card">
                            <h4>{hotel.get('name', '')}</h4>
                            <p class="location-info">📍 {hotel.get('location', '')}</p>
                            <p class="price-tag">€{hotel.get('price', '')}/晚</p>
                            <p class="transport-info">🚕 {hotel.get('transportation', '')}</p>
                            <p style="font-size:0.9em;color:#95a5a6;">{hotel.get('address', '')}</p>
                        </div>
                        """
                    current_content += "</div>"

                # 航班推荐部分
                if 'recommend_flight' in data_cache and 'flights' in data_cache['recommend_flight']:
                    current_content += "<h2 class='section-title'>✈️ 推荐航班</h2><div class='flex-container'>"
                    for flight in data_cache['recommend_flight']['flights']:
                        current_content += f"""
                        <div class="recommendation-card">
                            <h4>{flight.get('airline', '')}</h4>
                            <p>🛫 出发: {flight.get('departure', '')}</p>
                            <p>🛬 到达: {flight.get('arrival', '')}</p>
                            <p class="price-tag">￥{flight.get('price', '')}</p>
                        </div>
                        """
                    current_content += "</div>"

                # 地图信息
                if 'generate_map' in data_cache and 'map' in data_cache['generate_map']:
                    current_content += f"""
                    <h2 class='section-title'>🗺️ 行程地图</h2>
                    <div class="map-container">
                        <img src="{data_cache['generate_map']['map'].get('map_url', '')}" 
                             style="max-width: 100%; height: 280px; border-radius: 8px; object-fit: cover;">
                    </div>
                    """

                # 最终渲染
                poster_placeholder.markdown(current_content + "</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"发生错误：{e}")
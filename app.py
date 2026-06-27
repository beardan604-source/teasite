import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import psycopg2
from psycopg2.extras import DictCursor

# ---- 网站标签页标题与图标 ----
st.set_page_config(page_title="夏有时-每日饮茶记录", page_icon="🍵", layout="wide")
st.title("🍵 夏有时 - 每日饮茶记录")

# 🔑 你的专属云端密码
DB_URI = "postgresql://postgres.byggrsuypisqxfvyrbsw:cukgoN-rijhy9-dipweq@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres"

def get_db_connection():
    # 连接到 Supabase 云端数据库
    conn = psycopg2.connect(DB_URI)
    return conn

def fetch_data(query):
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def convert_image_to_base64(uploaded_file):
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        return base64.b64encode(file_bytes).decode()
    return None

# ---- 侧边栏：数据录入 ----
st.sidebar.header("📥 存量与茶器入库")

with st.sidebar.expander("➕ 添置新茶叶（入茶仓）", expanded=True):
    with st.form("add_tea_form", clear_on_submit=True):
        tea_name = st.text_input("茶叶名称", placeholder="例如：西湖龙井")
        tea_cat = st.selectbox("茶类", ["绿茶", "红茶", "乌龙茶", "普洱生茶", "普洱熟茶", "白茶", "黑茶", "黄茶", "花茶"])
        tea_stock = st.number_input("购入重量 (克)", min_value=0.0, step=10.0, value=50.0)
        tea_brand = st.text_input("茶品牌", placeholder="如：大益 / 八马 / 自制山头茶")
        tea_img = st.file_uploader("上传茶叶/包装照片", type=["png", "jpg", "jpeg"])
        
        submit_tea = st.form_submit_button("确认入仓")
        if submit_tea and tea_name:
            img_b64 = convert_image_to_base64(tea_img)
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("INSERT INTO teas (name, category, stock_grams, location, image_base64) VALUES (%s, %s, %s, %s, %s)",
                            (tea_name, tea_cat, tea_stock, tea_brand, img_b64))
            conn.commit()
            conn.close()
            st.sidebar.success(f"✅ {tea_name} 已成功入仓！")
            st.rerun()

with st.sidebar.expander("➕ 添置新茶器（可传图）", expanded=True):
    with st.form("add_ware_form", clear_on_submit=True):
        ware_name = st.text_input("茶器名称", placeholder="例如：白瓷盖碗")
        ware_mat = st.text_input("材质", placeholder="例如：陶瓷")
        ware_cap = st.number_input("容量 (ml)", min_value=0, step=10, value=130)
        ware_img = st.file_uploader("上传茶器美照", type=["png", "jpg", "jpeg"])
        
        submit_ware = st.form_submit_button("确认添加")
        if submit_ware and ware_name:
            img_b64 = convert_image_to_base64(ware_img)
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("INSERT INTO teaware (name, material, capacity_ml, image_base64) VALUES (%s, %s, %s, %s)",
                            (ware_name, ware_mat, ware_cap, img_b64))
            conn.commit()
            conn.close()
            st.sidebar.success(f"✅ 茶器 {ware_name} 已建档！")
            st.rerun()

# ---- 主页面 ----
tab1, tab2 = st.tabs(["📝 每日喝茶打卡", "📦 查看茶仓与茶器"])

with tab1:
    st.subheader("记录今日茶席")
    df_teas = fetch_data("SELECT id, name FROM teas")
    df_ware = fetch_data("SELECT id, name FROM teaware")
    
    if df_teas.empty or df_ware.empty:
        st.info("💡 **新茶山开垦指南**：\n\n您的云端数据库目前是空的。请先在**左侧边栏**添加至少**一款茶叶**和**一个茶器**。添加成功后，这里就会立刻解锁“每日饮茶打卡表单”功能！")
    else:
        tea_options = {row['name']: row['id'] for _, row in df_teas.iterrows()}
        ware_options = {row['name']: row['id'] for _, row in df_ware.iterrows()}
        
        with st.form("log_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_tea = st.selectbox("今日冲泡茶叶", options=list(tea_options.keys()))
            with col2:
                selected_ware = st.selectbox("选用茶器", options=list(ware_options.keys()))
            with col3:
                log_date = st.date_input("饮茶日期", datetime.now())
                
            col4, col5, col6 = st.columns(3)
            with col4:
                water_temp = st.number_input("水温 (°C)", min_value=0, max_value=100, value=90)
            with col5:
                tea_weight = st.number_input("投茶量 (克)", min_value=0.0, step=0.1, value=5.0)
            with col6:
                rating = st.slider("茶汤评分", min_value=1, max_value=5, value=5)
                
            notes = st.text_area("品饮笔记")
            log_img = st.file_uploader("上传今日茶汤/叶底照片", type=["png", "jpg", "jpeg"])
            
            submit_log = st.form_submit_button("🍵 记录这泡茶")
            
            if submit_log:
                tea_id = int(tea_options[selected_tea])
                ware_id = int(ware_options[selected_ware])
                img_b64 = convert_image_to_base64(log_img)
                
                conn = get_db_connection()
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO logs (tea_id, teaware_id, water_temp, tea_weight, rating, notes, created_at, image_base64) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                 (tea_id, ware_id, water_temp, tea_weight, rating, notes, str(log_date), img_b64))
                    cur.execute("UPDATE teas SET stock_grams = GREATEST(0.0, stock_grams - %s) WHERE id = %s", (tea_weight, tea_id))
                conn.commit()
                conn.close()
                st.success(f"🎉 成功记录！已自动扣除 {tea_weight}g {selected_tea}。")
                st.balloons()
                st.rerun()

    st.write("---")
    st.subheader("📜 近期饮茶随笔")
    
    conn = get_db_connection()
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""
            SELECT l.id as log_id, l.created_at, t.name as tea_name, l.tea_id, l.tea_weight, w.name as ware_name, l.water_temp, l.rating, l.notes, l.image_base64
            FROM logs l JOIN teas t ON l.tea_id = t.id JOIN teaware w ON l.teaware_id = w.id ORDER BY l.id DESC LIMIT 10
        """)
        logs_data = cur.fetchall()
    conn.close()

    if logs_data:
        for row in logs_data:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### {row['created_at']} · {row['tea_name']}")
                    st.write(f"🍵 **茶器：** {row['ware_name']} | 🌡️ **水温：** {row['water_temp']}°C | ⚖️ **投茶：** {row['tea_weight']}g | ⭐ **评分：** {row['rating']}星")
                    st.write(f"✍️ **笔记：** {row['notes'] if row['notes'] else '未填写笔记'}")
                    
                    if st.button(f"🗑️ 删除此条记录", key=f"del_log_{row['log_id']}"):
                        conn = get_db_connection()
                        with conn.cursor() as cur:
                            cur.execute("DELETE FROM logs WHERE id = %s", (row['log_id'],))
                            cur.execute("UPDATE teas SET stock_grams = stock_grams + %s WHERE id = %s", (row['tea_weight'], row['tea_id']))
                        conn.commit()
                        conn.close()
                        st.toast("💥 记录已删除，已自动返还茶叶库存！")
                        st.rerun()
                with c2:
                    if row['image_base64']:
                        st.image(base64.b64decode(row['image_base64']), use_container_width=True)
                    else:
                        st.caption("📷 本次无照片")
    else:
        st.info("暂无饮茶记录，开始你的第一泡茶吧！")

with tab2:
    # 🚀 ---- 新增功能：茶仓数据大屏统计 ----
    conn = get_db_connection()
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT id, name, category, stock_grams, location, image_base64 FROM teas ORDER BY id DESC")
        teas_data = cur.fetchall()
        cur.execute("SELECT id, name, material, capacity_ml, image_base64 FROM teaware ORDER BY id DESC")
        wares_data = cur.fetchall()
    conn.close()

    # 🧮 计算统计数据
    total_tea_grams = sum([tea['stock_grams'] for tea in teas_data]) if teas_data else 0.0
    active_tea_types = sum([1 for tea in teas_data if tea['stock_grams'] > 0]) if teas_data else 0
    total_wares_count = len(wares_data) if wares_data else 0

    st.subheader("📊 夏有时 · 茶仓数据大屏")
    # 用精美的三列数字卡片展示总量
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric(label="⚖️ 茶仓茶叶总重", value=f"{total_tea_grams:.1f} 克")
    with m_col2:
        st.metric(label="🗂️ 现有茶叶品种（有存货）", value=f"{active_tea_types} 种")
    with m_col3:
        st.metric(label="🏺 收藏茶器总计", value=f"{total_wares_count} 件")
    
    st.write("---") # 分割线

    # 📦 下方原本的左右分栏：茶仓与茶器详情
    col_left, col_right = st.columns(2)
    
    # 📦 左侧：茶仓存量
    with col_left:
        st.subheader("📦 当前茶仓存量详情")
        if teas_data:
            for tea in teas_data:
                with st.container(border=True):
                    t_c1, t_c2 = st.columns([3, 1])
                    with t_c1:
                        st.markdown(f"#### {tea['name']}")
                        st.write(f"🗂️ **茶类：** {tea['category']} | ⚖️ **剩余库存：** {tea['stock_grams']}g")
                        st.write(f"🏷️ **茶品牌：** {tea['location'] if tea['location'] else '未知品牌'}")
                        
                        if st.button(f"🗑️ 销毁此茶档", key=f"del_tea_{tea['id']}"):
                            conn = get_db_connection()
                            with conn.cursor() as cur:
                                cur.execute("DELETE FROM teas WHERE id = %s", (tea['id'],))
                            conn.commit()
                            conn.close()
                            st.toast(f"💥 茶叶 {tea['name']} 已从茶仓移除。")
                            st.rerun()
                    with t_c2:
                        if tea['image_base64']:
                            st.image(base64.b64decode(tea['image_base64']), use_container_width=True)
                        else:
                            st.caption("📷 暂无照片")
        else:
            st.info("茶仓空空如也，快去左侧边栏存点好茶吧！")
            
    # 🏺 右侧：茶器档案
    with col_right:
        st.subheader("🏺 茶器档案详情")
        if wares_data:
            for ware in wares_data:
                with st.container(border=True):
                    w_c1, w_c2 = st.columns([3, 1])
                    with w_c1:
                        st.markdown(f"#### {ware['name']}")
                        st.write(f"🧪 **材质：** {ware['material']} | 📐 **容量：** {ware['capacity_ml']}ml")
                        
                        if st.button(f"🗑️ 销毁此茶器", key=f"del_ware_{ware['id']}"):
                            conn = get_db_connection()
                            with conn.cursor() as cur:
                                cur.execute("DELETE FROM teaware WHERE id = %s", (ware['id'],))
                            conn.commit()
                            conn.close()
                            st.toast(f"💥 茶器 {ware['name']} 已从档案移除。")
                            st.rerun()
                    with w_c2:
                        if ware['image_base64']:
                            st.image(base64.b64decode(ware['image_base64']), use_container_width=True)
                        else:
                            st.caption("📷 暂无照片")
        else:
            st.info("还没有添加茶器哦~")
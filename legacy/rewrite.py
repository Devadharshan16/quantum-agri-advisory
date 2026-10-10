import re
import sys

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Un-hide sidebar
code = code.replace('[data-testid="stSidebar"] { display: none !important; }', '')

# 2. Add Sidebar styling
sidebar_css = """
/* Gorgeous Sidebar */
[data-testid="stSidebar"] {
    background-color: rgba(5, 7, 12, 0.8) !important;
    backdrop-filter: blur(24px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}
[data-testid="stSidebar"] > div:first-child {
    background-color: transparent !important;
}
[data-testid="stSidebarNav"] { display: none !important; }

/* Incredible Hero Text Animation */
@keyframes textShine {
    0% { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
}
.quantum-title {
    font-size: 64px;
    font-weight: 800;
    letter-spacing: -2px;
    background: linear-gradient(90deg, #f4a853, #fbbf24, #4ade80, #f4a853);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: textShine 4s linear infinite;
    margin-bottom: 12px;
}
"""
code = code.replace('</style>', sidebar_css + '\n</style>')

# Replace inputs section to be in sidebar.
# The inputs section starts around "# ─── Inputs Section"
# I will use regex or string replace for the inputs block.

input_search = """# ─── Inputs Section (Glass Layout) ───────────────────────────────────────────"""
main_split = code.split(input_search)
if len(main_split) == 2:
    part1, part2 = main_split
    
    # We will build a totally new main section.
    
    # What was in part2? 
    # st.markdown(...)
    # in_c1, in_c2, in_c3 = st.columns(3)
    # ...
    # predict_clicked = st.button(...)
    # ...
    
    # We will reconstruct the layout cleanly.
    new_part2 = """
# ─── New Ultra Rich UI Layout ───────────────────────────────────────────

with st.sidebar:
    st.markdown(f"<div style='font-size:24px;color:#f0ece3;font-weight:800;margin-bottom:24px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.05);'>{t['soil_nutrients']}</div>", unsafe_allow_html=True)
    n     = synced_input(t["nitrogen"],   "N_val", float(FEATURE_RANGES["N"][0]), float(FEATURE_RANGES["N"][1]), 50.0, 1.0)
    p_val = synced_input(t["phosphorus"], "P_val", float(FEATURE_RANGES["P"][0]), float(FEATURE_RANGES["P"][1]), 50.0, 1.0)
    k     = synced_input(t["potassium"],  "K_val", float(FEATURE_RANGES["K"][0]), float(FEATURE_RANGES["K"][1]), 50.0, 1.0)
    ph    = synced_input(t["ph"], "ph_val", float(FEATURE_RANGES["ph"][0]), float(FEATURE_RANGES["ph"][1]), 6.5, 0.1)
    
    st.markdown(f"<div style='font-size:24px;color:#f0ece3;font-weight:800;margin-top:32px;margin-bottom:24px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.05);'>{t['climate_env']}</div>", unsafe_allow_html=True)
    temp  = synced_input(t["temperature"], "temp_val", float(FEATURE_RANGES["temperature"][0]), float(FEATURE_RANGES["temperature"][1]), 25.0, 0.5)
    humidity = synced_input(t["humidity"], "hum_val", float(FEATURE_RANGES["humidity"][0]), float(FEATURE_RANGES["humidity"][1]), 70.0, 1.0)
    rainfall = synced_input(t["rainfall"], "rain_val", float(FEATURE_RANGES["rainfall"][0]), float(FEATURE_RANGES["rainfall"][1]), 100.0, 5.0)

    st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
    predict_clicked = st.button(t["generate_btn"], use_container_width=True)
    st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)


# ─── MAIN REPORT VIEW ───
if not predict_clicked:
    # ─── Ultra Rich Hero ───
    html_hero = f\"\"\"
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:75vh;text-align:center;">
        <div style="font-family:'Plus Jakarta Sans',sans-serif;">
            <div class="quantum-title">{t['title']}</div>
            <div style="font-size:20px;color:#94a3b8;font-weight:400;max-width:600px;margin:0 auto;line-height:1.6;">
                {t['subtitle']}
            </div>
        </div>
        <div style="margin-top:60px;position:relative;">
            <div style="position:absolute;inset:0;background:radial-gradient(circle, rgba(244,168,83,0.3) 0%, transparent 70%);filter:blur(40px);width:300px;height:300px;left:-150px;top:-150px;z-index:0;"></div>
            <div style="position:relative;z-index:1;width:120px;height:120px;border-radius:50%;background:rgba(19, 31, 53, 0.4);border:1px solid rgba(255,255,255,0.1);backdrop-filter:blur(12px);display:flex;align-items:center;justify-content:center;box-shadow:0 0 40px rgba(244,168,83,0.2);">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#f4a853" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
                    <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
                </svg>
            </div>
        </div>
    </div>
    \"\"\"
    st.components.v1.html(html_hero, height=800, scrolling=False)
else:
    placeholder = st.empty()
    html_loading = f\"\"\"
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:50vh;font-family:'Plus Jakarta Sans',sans-serif;">
        <div style="width:48px;height:48px;border:4px solid rgba(244,168,83,0.2);border-top-color:#f4a853;border-radius:50%;animation:spin 1s linear infinite;"></div>
        <div style="margin-top:24px;font-size:18px;color:#f0ece3;font-weight:500;letter-spacing:1px;">{t['analyzing']}</div>
        <style>@keyframes spin {{ to {{ transform: rotate(360deg); }} }}</style>
    </div>
    \"\"\"
    placeholder.markdown(html_loading, unsafe_allow_html=True)

    import time
    start_time = time.time()
    
    import pandas as pd
    input_data = pd.DataFrame([[n, p_val, k, temp, humidity, ph, rainfall]],
                              columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
    
    result = predict_crops(pipeline, input_data)
    row = result.iloc[0]
    elapsed = int((time.time() - start_time) * 1000)
    placeholder.empty()

    crop         = row['predicted_crop']
    crop_display = CROP_TRANSLATIONS.get(crop.lower(), {{}}).get(lang, crop.title())
    cinfo        = CROP_CONDITIONS.get(crop.lower(), DEFAULT_CROP)
    
    from app import t_cond
    t_season = t_cond(cinfo['season'], lang)
    t_water = t_cond(cinfo['water'], lang)
    t_soil = t_cond(cinfo['soil'], lang)
    
    prob1        = float(row['top1_prob']) * 100
    import datetime
    now          = datetime.datetime.now().strftime("%H:%M:%S")

    def get_status_color(val, min_v, max_v):
        range_span = max_v - min_v
        if range_span == 0: return "#4ade80"
        rel = (val - min_v) / range_span
        if 0.2 < rel < 0.8: return "#4ade80"
        if 0.1 < rel <= 0.2 or 0.8 <= rel < 0.9: return "#f4a853"
        return "#ef4444"

    badges_html = ""
    optimal_params = []
    attention_params = []
    for feat_key, val in [("nitrogen", n), ("phosphorus", p_val), ("potassium", k), ("temperature", temp), ("humidity", humidity), ("ph", ph), ("rainfall", rainfall)]:
        feat_name = t[feat_key]
        key_feat = "N" if feat_key == "nitrogen" else "P" if feat_key == "phosphorus" else "K" if feat_key == "potassium" else feat_key
        lo, hi = FEATURE_RANGES[key_feat]
        c = get_status_color(val, lo, hi)
        
        if c == "#4ade80":
            optimal_params.append(feat_name.split('(')[0].strip())
        else:
            attention_params.append(feat_name.split('(')[0].strip())

        badges_html += f\"\"\"
        <div style="background:rgba(19, 31, 53, 0.4);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.05);
                    border-radius:12px;padding:16px;display:flex;flex-direction:column;align-items:center;
                    box-shadow:0 4px 15px rgba(0,0,0,0.1);transition:transform 0.2s;">
            <div style="width:8px;height:8px;border-radius:50%;background:{c};margin-bottom:12px;box-shadow:0 0 10px {c};"></div>
            <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;text-align:center;">{feat_name}</div>
            <div style="font-size:16px;color:#f0ece3;font-weight:700;">{val:.1f}</div>
        </div>
        \"\"\"

    html_hero = f\"\"\"
    <div style="font-family:'Plus Jakarta Sans',sans-serif;margin-bottom:40px;position:relative;">
        <div style="position:absolute;right:0;top:-20px;width:300px;height:300px;background:radial-gradient(circle, rgba(74,222,128,0.1) 0%, transparent 70%);filter:blur(40px);z-index:0;"></div>
        <div style="position:relative;z-index:1;">
            <div style="font-size:14px;color:#94a3b8;letter-spacing:4px;margin-bottom:16px;font-weight:600;text-transform:uppercase;">
                {t["field_report"]}
            </div>
            <div style="font-size:80px;font-weight:800;letter-spacing:-2px;color:#f0ece3;line-height:1;margin-bottom:32px;
                        text-shadow: 0 0 40px rgba(244,168,83,0.1);">
                {crop_display}
            </div>
            
            <div style="display:flex;gap:40px;border-top:1px solid rgba(255,255,255,0.05);padding-top:32px;">
                <div>
                    <div style="font-size:12px;color:#94a3b8;margin-bottom:8px;letter-spacing:2px;font-weight:600;">{t["confidence"]}</div>
                    <div style="font-size:28px;color:#4ade80;font-weight:800;text-shadow:0 0 15px rgba(74,222,128,0.3);">{prob1:.1f}%</div>
                </div>
                <div style="width:1px;background:rgba(255,255,255,0.05);"></div>
                <div>
                    <div style="font-size:12px;color:#94a3b8;margin-bottom:8px;letter-spacing:2px;font-weight:600;">{t["season"]}</div>
                    <div style="font-size:20px;color:#f0ece3;font-weight:600;margin-top:6px;">{t_season}</div>
                </div>
                <div style="width:1px;background:rgba(255,255,255,0.05);"></div>
                <div>
                    <div style="font-size:12px;color:#94a3b8;margin-bottom:8px;letter-spacing:2px;font-weight:600;">{t["water_need"]}</div>
                    <div style="font-size:20px;color:#f0ece3;font-weight:600;margin-top:6px;">{t_water}</div>
                </div>
                <div style="width:1px;background:rgba(255,255,255,0.05);"></div>
                <div>
                    <div style="font-size:12px;color:#94a3b8;margin-bottom:8px;letter-spacing:2px;font-weight:600;">{t["ideal_soil"]}</div>
                    <div style="font-size:20px;color:#f0ece3;font-weight:600;margin-top:6px;">{t_soil}</div>
                </div>
            </div>
        </div>
    </div>
    \"\"\"
    st.components.v1.html(html_hero, height=400, scrolling=False)

    html_badges_container = f\"\"\"
    <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:16px;margin-bottom:48px;font-family:'Plus Jakarta Sans',sans-serif;">
        {badges_html}
    </div>
    \"\"\"
    st.components.v1.html(html_badges_container, height=140, scrolling=False)

    col_rank, col_insights = st.columns(2)

    with col_rank:
        html_rank = f\"\"\"
        <div style="font-family:'Plus Jakarta Sans',sans-serif;
                    background:rgba(255,255,255,0.02); backdrop-filter:blur(16px);
                    padding:40px;height:100%;box-sizing:border-box;border-radius:24px;
                    border:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:14px;letter-spacing:3px;color:#f4a853;margin-bottom:40px;font-weight:700;text-transform:uppercase;">
                {t["alternative"]}
            </div>
            <div style="position:relative;padding-left:32px;">
                <div style="position:absolute;left:5px;top:16px;bottom:16px;width:1px;background:rgba(255,255,255,0.1);"></div>
        \"\"\"

        for i in range(1, 6):
            if f'top{i}' in row:
                c_name = row[f'top{i}']
                c_name_translated = CROP_TRANSLATIONS.get(c_name.lower(), {{}}).get(lang, c_name.title())
                c_prob = float(row[f'top{i}_prob']) * 100
                color = "#f4a853" if i == 1 else "#94a3b8"
                glow  = f"box-shadow:0 0 15px {color};" if i == 1 else ""
                
                html_rank += f\"\"\"
                <div style="position:relative;margin-bottom:32px;display:flex;align-items:center;">
                    <div style="position:absolute;left:-32px;width:10px;height:10px;border-radius:50%;background:{color};{glow}"></div>
                    <div style="font-size:14px;color:#94a3b8;width:40px;font-weight:600;">0{i}</div>
                    <div style="font-size:18px;color:#f0ece3;font-weight:600;width:160px;">{c_name_translated}</div>
                    <div style="font-size:18px;color:{color};font-weight:700;">{c_prob:.1f}%</div>
                </div>
                \"\"\"
        
        html_rank += "</div></div>"
        st.components.v1.html(html_rank, height=450, scrolling=False)

    with col_insights:
        optimal_str = "<br>".join([f"✓ {x}" for x in optimal_params]) if optimal_params else "None"
        attention_str = "<br>".join([f"⚠ {x}" for x in attention_params]) if attention_params else "None"
        
        html_insights = f\"\"\"
        <div style="font-family:'Plus Jakarta Sans',sans-serif;
                    background:rgba(255,255,255,0.02); backdrop-filter:blur(16px);
                    border:1px solid rgba(255,255,255,0.05);
                    border-radius:24px;padding:40px;height:100%;box-sizing:border-box;">
            <div style="font-size:14px;letter-spacing:3px;color:#f4a853;margin-bottom:40px;font-weight:700;text-transform:uppercase;">
                {t["insights"]}
            </div>
            
            <div style="margin-bottom:32px;background:rgba(74,222,128,0.05);padding:20px;border-radius:12px;border:1px solid rgba(74,222,128,0.1);">
                <div style="font-size:12px;color:#4ade80;font-weight:700;margin-bottom:12px;letter-spacing:1px;text-transform:uppercase;">{t['optimal']}</div>
                <div style="font-size:15px;color:#f0ece3;line-height:2;">{optimal_str}</div>
            </div>
            
            <div style="background:rgba(239,68,68,0.05);padding:20px;border-radius:12px;border:1px solid rgba(239,68,68,0.1);">
                <div style="font-size:12px;color:#ef4444;font-weight:700;margin-bottom:12px;letter-spacing:1px;text-transform:uppercase;">{t['attention']}</div>
                <div style="font-size:15px;color:#f0ece3;line-height:2;">{attention_str}</div>
            </div>
        </div>
        \"\"\"
        st.components.v1.html(html_insights, height=450, scrolling=False)

    # Gauges for N, P, K, pH
    st.markdown(f"<div style='margin-top:60px;margin-bottom:24px;font-size:22px;color:#f0ece3;font-weight:700;'>{t['soil_nutrients']}</div>", unsafe_allow_html=True)
    
    gc1, gc2, gc3, gc4 = st.columns(4)
    
    import plotly.graph_objects as go
    def create_gauge(val, title, min_v, max_v):
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = val,
            title = {{'text': title, 'font': {{'size': 14, 'color': '#94a3b8'}}}},
            number = {{'font': {{'size': 24, 'color': '#f0ece3'}}}},
            gauge = {{
                'axis': {{'range': [min_v, max_v], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.1)"}},
                'bar': {{'color': "#f4a853"}},
                'bgcolor': "rgba(255,255,255,0.02)",
                'borderwidth': 0,
                'steps': [
                    {{'range': [min_v, min_v + (max_v-min_v)*0.2], 'color': "rgba(239, 68, 68, 0.1)"}},
                    {{'range': [min_v + (max_v-min_v)*0.8, max_v], 'color': "rgba(239, 68, 68, 0.1)"}},
                ]
            }}
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=220, margin=dict(l=10, r=10, t=40, b=10))
        return fig
        
    with gc1: st.plotly_chart(create_gauge(n, t['nitrogen'].split('(')[0].strip(), float(FEATURE_RANGES["N"][0]), float(FEATURE_RANGES["N"][1])), use_container_width=True, config={{'displayModeBar': False}})
    with gc2: st.plotly_chart(create_gauge(p_val, t['phosphorus'].split('(')[0].strip(), float(FEATURE_RANGES["P"][0]), float(FEATURE_RANGES["P"][1])), use_container_width=True, config={{'displayModeBar': False}})
    with gc3: st.plotly_chart(create_gauge(k, t['potassium'].split('(')[0].strip(), float(FEATURE_RANGES["K"][0]), float(FEATURE_RANGES["K"][1])), use_container_width=True, config={{'displayModeBar': False}})
    with gc4: st.plotly_chart(create_gauge(ph, "pH", float(FEATURE_RANGES["ph"][0]), float(FEATURE_RANGES["ph"][1])), use_container_width=True, config={{'displayModeBar': False}})

    # Plotly Bar Chart for Top 5 Probabilities
    st.markdown(f"<div style='margin-top:60px;margin-bottom:24px;font-size:22px;color:#f0ece3;font-weight:700;'>{t['probability_dist']}</div>", unsafe_allow_html=True)
    
    crops_for_chart = []
    probs_for_chart = []
    for i in range(1, 6):
        if f'top{i}' in row:
            c_name = row[f'top{i}']
            c_name_t = CROP_TRANSLATIONS.get(c_name.lower(), {{}}).get(lang, c_name.title())
            c_prob = float(row[f'top{i}_prob']) * 100
            crops_for_chart.append(c_name_t)
            probs_for_chart.append(c_prob)

    crops_for_chart.reverse()
    probs_for_chart.reverse()

    fig = go.Figure(go.Bar(
        x=probs_for_chart,
        y=crops_for_chart,
        orientation='h',
        marker=dict(
            color=probs_for_chart,
            colorscale=[[0, '#f4a853'], [1, '#4ade80']]
        )
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans", color="#94a3b8", size=14),
        xaxis=dict(title=t["probability"], showgrid=True, gridcolor='rgba(255,255,255,0.05)', ticksuffix='%', range=[0, 100]),
        yaxis=dict(title="", showgrid=False),
        margin=dict(l=20, r=20, t=20, b=40),
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True, config={{'displayModeBar': False}})

    # Timestamp
    html_ts = f\"\"\"
    <div style="font-family:'Plus Jakarta Sans',sans-serif;text-align:center;font-size:12px;color:#64748b;
                margin-top:40px;letter-spacing:2px;padding-top:40px;border-top:1px solid rgba(255,255,255,0.05);text-transform:uppercase;">
        Generated at {now} &nbsp;·&nbsp; {elapsed}ms latency
    </div>
    \"\"\"
    st.components.v1.html(html_ts, height=100, scrolling=False)
"""
    code = part1 + new_part2

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Updated app.py successfully!")

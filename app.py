import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ページの設定
st.set_page_config(
    page_title="Eメールマーケティング最適化ダッシュボード", layout="wide"
)


# 2. データの読み込み
@st.cache_data
def load_data():
    df = pd.read_csv("kevin_hillstrom_for_app.csv")
    return df


df = load_data()

# 3. タイトルと概要
st.title("📧 Eメールマーケティング 最適セグメント探索ダッシュボード")
st.markdown("""
このダッシュボードは、Kevin Hillstromのデータセットを使用し、**「どの属性の顧客に、どのメール（Mens/Womens）を送れば最もコンバージョン（購入）率が高くなるか」**をシミュレーションするツールです。
左側のサイドバーから顧客の属性を絞り込み、セグメント別の効果を確認してください。
""")

# 4. サイドバー（フィルター機能）
st.sidebar.header("🎯 ターゲット顧客の絞り込み")

# 【修正】sorted() を使って順番を綺麗に並び替える
history_options = sorted(df["history_segment"].unique())
selected_history = st.sidebar.multiselect(
    "過去の購買金額ランク", options=history_options, default=history_options
)

# 【追加】新規/既存（newbie）のフィルター
newbie_options = sorted(df["newbie"].unique())
selected_newbie = st.sidebar.multiselect(
    "新規/既存 (Newbie)", options=newbie_options, default=newbie_options
)

# 【追加】地域（zip_code）のフィルター
zip_options = sorted(df["zip_code"].unique())
selected_zip = st.sidebar.multiselect(
    "地域 (Zip Code)", options=zip_options, default=zip_options
)

# データのフィルタリング（3つの条件を & で繋ぐ）
df_filtered = df[
    (df["history_segment"].isin(selected_history))
    & (df["newbie"].isin(selected_newbie))
    & (df["zip_code"].isin(selected_zip))
]

# 5. メイン画面のKPI表示
st.subheader("📊 選択されたセグメントの全体結果")

# エラーハンドリング：もし絞り込みすぎてデータが0件になった場合の処理
if len(df_filtered) == 0:
    st.warning(
        "⚠️ 選択された条件に一致する顧客がいません。フィルターの条件を緩めてください。"
    )
else:
    col1, col2 = st.columns(2)
    col1.metric("対象顧客数", f"{len(df_filtered):,} 人")
    overall_cvr = df_filtered["conversion"].mean() * 100
    col2.metric("全体の平均購入率 (CVR)", f"{overall_cvr:.2f} %")

    # 6. Plotlyを使った美しいグラフの描画
    st.subheader("✉️ 配信メール別の購入率（CVR）比較")

    cvr_by_segment = df_filtered.groupby("segment")["conversion"].mean().reset_index()
    cvr_by_segment["CVR (%)"] = cvr_by_segment["conversion"] * 100

    fig = px.bar(
        cvr_by_segment,
        x="segment",
        y="CVR (%)",
        color="segment",
        text="CVR (%)",
        title="メール種類別の効果（どのメールを送るべきか？）",
    )
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_layout(
        yaxis_range=[0, max(cvr_by_segment["CVR (%)"].max() * 1.2, 1.0)]
    )  # データが少ない時でもグラフの縦軸が崩れないよう調整

    st.plotly_chart(fig, use_container_width=True)

    # 7. 元データの確認
    with st.expander("詳細なデータテーブルを表示"):
        st.dataframe(df_filtered)

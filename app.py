import streamlit as st
import plotly.graph_objects as go
import numpy as np

def create_frustum_mesh(center_pos, top_radius, bottom_radius, height, n_segments=32):
    """
    指定された寸法のシンプルな円錐台の頂点と面データを生成する関数。
    
    Args:
        center_pos (list): 円錐台の底面の中心座標 [x, y, z]
        top_radius (float): 上面の半径
        bottom_radius (float): 下面の半径
        height (float): 高さ
        n_segments (int): 円周の分割数（多いほど滑らかになる）

    Returns:
        tuple: (頂点配列, 面配列)
    """
    # 円周上の点を計算するための角度
    theta = np.linspace(0, 2 * np.pi, n_segments, endpoint=False)
    
    # --- 頂点(Vertices)の計算 ---
    verts = []
    
    # 1. 下面の円周上の頂点 (Bottom circle)
    for i in range(n_segments):
        x = center_pos[0] + bottom_radius * np.cos(theta[i])
        y = center_pos[1] + bottom_radius * np.sin(theta[i])
        z = center_pos[2]
        verts.append([x, y, z])
        
    # 2. 上面の円周上の頂点 (Top circle)
    for i in range(n_segments):
        x = center_pos[0] + top_radius * np.cos(theta[i])
        y = center_pos[1] + top_radius * np.sin(theta[i])
        z = center_pos[2] + height
        verts.append([x, y, z])

    # 3. 下面の中心点 (Bottom center)
    verts.append([center_pos[0], center_pos[1], center_pos[2]])
    bottom_center_idx = len(verts) - 1
    
    # 4. 上面の中心点 (Top center)
    verts.append([center_pos[0], center_pos[1], center_pos[2] + height])
    top_center_idx = len(verts) - 1

    verts = np.array(verts)

    # --- 面(Faces)の計算 ---
    faces = []
    
    # 1. 側面の三角形の面
    for i in range(n_segments):
        next_i = (i + 1) % n_segments
        # 下の頂点(i) -> 上の頂点(i+n) -> 上の隣の頂点(next_i+n)
        faces.append([i, i + n_segments, next_i + n_segments])
        # 下の頂点(i) -> 下の隣の頂点(next_i) -> 上の隣の頂点(next_i+n)
        faces.append([i, next_i, next_i + n_segments])
        
    # 2. 下面のフタの三角形の面
    for i in range(n_segments):
        faces.append([i, (i + 1) % n_segments, bottom_center_idx])
        
    # 3. 上面のフタの三角形の面
    for i in range(n_segments):
        # 上面の頂点は n_segments から始まる
        p1 = i + n_segments
        p2 = ((i + 1) % n_segments) + n_segments
        faces.append([p1, p2, top_center_idx])

    return verts, np.array(faces)


# --- Streamlit アプリケーション ---
st.set_page_config(layout="centered", page_title="円錐台ビューア")
st.title("指定寸法の円錐台ビューア")

# --- ここで円錐台の寸法を指定します ---
top_diameter = 2.0      # 上面の直径 (m)
bottom_diameter = 1.0   # 下面の直径 (m)
height = 5.0            # 高さ (m)

# 直径から半径に変換
top_radius = top_diameter / 2.0
bottom_radius = bottom_diameter / 2.0

# 円錐台のメッシュデータを生成
# 底面の中心を原点 (0, 0, 0) に設定
center_position = [0, 0, 0]
vertices, faces = create_frustum_mesh(center_position, top_radius, bottom_radius, height)

# --- Plotly を使って3D描画 ---
fig = go.Figure(data=[
    go.Mesh3d(
        # x, y, z に頂点の各座標を渡す
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        # i, j, k に面の頂点インデックスを渡す
        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],
        color='lightblue', # 色
        opacity=0.9,       # 透明度
        name='円錐台'
    )
])

# グラフのレイアウト設定
fig.update_layout(
    title_text=f"上面直径:{top_diameter}m, 下面直径:{bottom_diameter}m, 高さ:{height}m",
    scene=dict(
        xaxis=dict(title='X (m)', range=[-5, 5]),
        yaxis=dict(title='Y (m)', range=[-5, 5]),
        zaxis=dict(title='Z (m)', range=[-1, 6]),
        aspectmode='data' # 縦横比をデータのスケールに合わせる
    ),
    margin=dict(l=0, r=0, b=0, t=40)
)

st.plotly_chart(fig, use_container_width=True)

# 寸法情報をテキストで表示
st.info(f"""
#### 指定された寸法
- **上面直径:** {top_diameter} m (半径: {top_radius} m)
- **下面直径:** {bottom_diameter} m (半径: {bottom_radius} m)
- **高さ:** {height} m
""")

st.code("""
# 寸法はここで変更できます
top_diameter = 2.0      # 上面の直径 (m)
bottom_diameter = 1.0   # 下面の直径 (m)
height = 5.0            # 高さ (m)
""", language="python")


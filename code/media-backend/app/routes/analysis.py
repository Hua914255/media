from fastapi import APIRouter, HTTPException
import json
import numpy as np
from pathlib import Path
from sklearn.decomposition import PCA

router = APIRouter()

@router.get("/all-data")
def get_analysis_data():
    """
    动态获取所有实验数据
    1. 扫描 data 目录下所有的 embeddings.json
    2. 合并数据 & 提取所有向量
    3. 实时运行 PCA 降维
    4. 返回带 (x,y) 坐标的完整数据
    """
    data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    merged_data = {
        "experiment_name": "Merged Analysis",
        "data": {}
    }
    
    if not data_dir.exists():
         raise HTTPException(status_code=404, detail="Data directory not found")

    # 1. 扫描并合并数据
    json_files = list(data_dir.glob("*.json"))
    
    for jf in json_files:
        if jf.name == "stories.json": continue
        try:
            with open(jf, "r", encoding="utf-8") as f:
                content = json.load(f)
                if "data" in content and isinstance(content["data"], dict):
                    merged_data["data"].update(content["data"])
        except Exception as e:
            print(f"⚠️ Failed to load {jf}: {e}")

    # 2. 准备 PCA 数据
    all_vectors = []
    # 记录映射关系: (story_id, round_idx)
    vector_map = [] 
    
    # 必须确保有数据才跑 PCA
    has_data = False
    
    for sid, story_obj in merged_data["data"].items():
        if "rounds" not in story_obj: continue
        
        for idx, turn in enumerate(story_obj["rounds"]):
            # 兼容：有的可能是 list，有的可能是 numpy 导出的 list
            emb = turn.get("embedding")
            if emb and len(emb) > 0:
                all_vectors.append(emb)
                vector_map.append((sid, idx))
                has_data = True
    
    # 3. 运行 PCA
    if has_data and len(all_vectors) > 2:
        try:
            # 降到 2 维
            pca = PCA(n_components=2)
            coords = pca.fit_transform(all_vectors)
            
            # --- 关键修改：保存模型以统一坐标系 ---
            import joblib
            # 保存到 media-backend/data/pca_model.pkl
            pca_save_path = data_dir / "pca_model.pkl"
            joblib.dump(pca, pca_save_path)
            print(f"✅ PCA Model updated and saved to: {pca_save_path}")
            
            # 4. 回填坐标
            for i, (x, y) in enumerate(coords):
                sid, ridx = vector_map[i]
                # 写入 merged_data
                merged_data["data"][sid]["rounds"][ridx]["x"] = round(float(x), 3)
                merged_data["data"][sid]["rounds"][ridx]["y"] = round(float(y), 3)
                
                # 可选：如果不想把巨大向量发给前端，可以在这里 pop 掉
                # merged_data["data"][sid]["rounds"][ridx].pop("embedding", None)
                
        except Exception as e:
            print(f"❌ PCA Analysis Failed: {e}")
    
    return merged_data

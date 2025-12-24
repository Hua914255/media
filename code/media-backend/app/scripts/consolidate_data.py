
import os
import json
import joblib
import numpy as np
from pathlib import Path

# 定义路径
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # media-backend
# media-backend -> code -> media -> lab -> data
DATA_ROOT = BASE_DIR.parent.parent.parent / "data"               # lab/data
PCA_MODEL_PATH = BASE_DIR / "app/data/pca_model.pkl"
OUTPUT_PATH = BASE_DIR / "app/data/analysis_dataset.json"

def load_pca():
    if not PCA_MODEL_PATH.exists():
        print(f"❌ PCA model not found at {PCA_MODEL_PATH}")
        return None
    print(f"✅ Loading PCA model from {PCA_MODEL_PATH}...")
    return joblib.load(PCA_MODEL_PATH)

def safe_float(v):
    try:
        return float(v)
    except:
        return 0.0

def process_exp1(pca):
    """处理实验1数据"""
    path = DATA_ROOT / "1/experiment_embeddings.json"
    if not path.exists():
        print(f"⚠️ Exp1 file not found: {path}")
        return []
        
    print(f"Processing Exp1: {path}")
    points = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for group_id, items in data.get("experiment_data", {}).items():
            # 原始句
            if "original_embedding" in items:
                emb = np.array(items["original_embedding"]).reshape(1, -1)
                xy = pca.transform(emb)[0]
                points.append({
                    "dataset": "Exp1",
                    "id": f"{group_id}_orig",
                    "text": items.get("original_sentence", "")[:50],
                    "x": safe_float(xy[0]),
                    "y": safe_float(xy[1]),
                    "type": "human_orig"
                })
            
            # 修改轮次
            for round_idx, r in enumerate(items.get("modification_rounds", [])):
                # 随机修改
                if "random_mod_embedding" in r:
                    emb = np.array(r["random_mod_embedding"]).reshape(1, -1)
                    xy = pca.transform(emb)[0]
                    points.append({
                        "dataset": "Exp1",
                        "id": f"{group_id}_r{round_idx}_rand",
                        "text": r.get("random_modification", "")[:50],
                        "x": safe_float(xy[0]),
                        "y": safe_float(xy[1]),
                        "type": "ai_noise"
                    })
                
                # 优化结果
                if "optimized_embedding" in r:
                    emb = np.array(r["optimized_embedding"]).reshape(1, -1)
                    xy = pca.transform(emb)[0]
                    points.append({
                        "dataset": "Exp1",
                        "id": f"{group_id}_r{round_idx}_opt",
                        "text": r.get("optimized_result", "")[:50],
                        "x": safe_float(xy[0]),
                        "y": safe_float(xy[1]),
                        "type": "human_opt"
                    })
    except Exception as e:
        print(f"❌ Error processing Exp1: {e}")
        
    return points

def process_exp2(pca):
    """处理实验2数据"""
    path = DATA_ROOT / "2/experiment_2a_data.json"
    if not path.exists():
        print(f"⚠️ Exp2 file not found: {path}")
        return []

    print(f"Processing Exp2: {path}")
    points = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for key, items in data.get("experiment_data", {}).items():
            # 这里 experiment_data 的结构可能是一层
            # 同样找 embedding
            if "original_embedding" in items:
                emb = np.array(items["original_embedding"]).reshape(1, -1)
                xy = pca.transform(emb)[0]
                points.append({
                    "dataset": "Exp2",
                    "id": f"{key}_orig",
                    "text": items.get("original_sentence", "")[:50],
                    "x": safe_float(xy[0]),
                    "y": safe_float(xy[1]),
                    "type": "human_orig"
                })

            for round_idx, r in enumerate(items.get("modification_rounds", [])):
                if "selected_embedding" in r:
                    emb = np.array(r["selected_embedding"]).reshape(1, -1)
                    xy = pca.transform(emb)[0]
                    points.append({
                        "dataset": "Exp2",
                        "id": f"{key}_r{round_idx}_sel",
                        "text": r.get("selected_result", "")[:50],
                        "x": safe_float(xy[0]),
                        "y": safe_float(xy[1]),
                        "type": "human_select"
                    })
    except Exception as e:
        print(f"❌ Error processing Exp2: {e}")
        
    return points

def process_exp4(pca):
    """处理实验4数据"""
    # 实验4有两个 json: experiment_4a_data.json 和 experiment_4b_data(AI).json
    files = ["4/experiment_4a_data.json", "4/experiment_4b_data(AI).json"]
    points = []
    
    for fname in files:
        path = DATA_ROOT / fname
        if not path.exists():
            continue
            
        print(f"Processing Exp4: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Exp4 结构差异: root key可能是 "data" 或 "experiment_data"
            content = data.get("data") or data.get("experiment_data", {})
            
            for key, items in content.items():
                if "original_embedding" in items:
                    emb = np.array(items["original_embedding"]).reshape(1, -1)
                    xy = pca.transform(emb)[0]
                    points.append({
                        "dataset": "Exp4",
                        "id": f"{key}_orig",
                        "text": items.get("original_sentence") or items.get("original", "")[:50],
                        "x": safe_float(xy[0]),
                        "y": safe_float(xy[1]),
                        "type": "seed"
                    })
                    
                # Rounds 可能叫 rounds, modification_rounds, generations
                rounds = items.get("rounds") or items.get("modification_rounds") or items.get("generations") or []
                
                for round_idx, r in enumerate(rounds):
                    # 检查里面的字段 (4a/4b 混合)
                    # 4a: cross_embedding, mutated_embedding
                    # 4b: child_embedding, selected_embedding, etc.
                    keys_to_check = [
                        "cross_embedding", "mutated_embedding", "child_embedding", "selected_embedding", 
                        "random_mod_embedding", "optimized_embedding"
                    ]
                    
                    for k in keys_to_check:
                         if k in r:
                            emb = np.array(r[k]).reshape(1, -1)
                            xy = pca.transform(emb)[0]
                            # 尝试找对应的文本
                            txt_key = k.replace("_embedding", "_result") # e.g. cross_result
                            if txt_key not in r:
                                txt_key = "text" # fallback
                                
                            points.append({
                                "dataset": "Exp4",
                                "id": f"{key}_r{round_idx}_{k.split('_')[0]}",
                                "text": str(r.get(txt_key, r.get("text", "")))[:50],
                                "x": safe_float(xy[0]),
                                "y": safe_float(xy[1]),
                                "type": "evolution"
                            })

        except Exception as e:
            print(f"❌ Error processing Exp4 {fname}: {e}")
            
    return points

def main():
    pca = load_pca()
    if not pca:
        return

    all_points = []
    all_points.extend(process_exp1(pca))
    all_points.extend(process_exp2(pca))
    all_points.extend(process_exp4(pca))

    print(f"Total points collected: {len(all_points)}")
    
    # Save
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_points, f, ensure_ascii=False, separators=(',', ':'))
    
    print(f"🎉 Saved analysis dataset to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()

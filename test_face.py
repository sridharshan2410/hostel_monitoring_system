from insightface.app import FaceAnalysis

app = FaceAnalysis(name="buffalo_l")

app.prepare(ctx_id=-1)

print("InsightFace Working Successfully")
frontend:
npm run dev

backend:
uvicorn app.main:app --reload  

docker qdrant:
ocker run -p 6333:6333 qdrant/qdrant

docker:
docker run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"
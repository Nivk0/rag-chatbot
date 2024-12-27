frontend:
cd frontend
npm install
npm run dev

backend:
cd backend
uvicorn app.main:app --reload  

docker qdrant:
cd backend
ocker run -p 6333:6333 qdrant/qdrant

docker:
root:
docker run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"

Remember to replace open AI key with actual key in config.py in backend folder. (This will be later replaced to LLAMA2 when I get access to make it on-prem

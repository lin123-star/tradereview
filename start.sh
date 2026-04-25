#!/bin/bash
# TradeReview Pro 启动脚本

echo "=== TradeReview Pro ==="

# 启动后端
echo "[1/2] 启动后端 FastAPI..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "后端已启动 PID=$BACKEND_PID → http://localhost:8000"
echo "API文档 → http://localhost:8000/docs"

# 启动前端
echo "[2/2] 启动前端 Vite..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "前端已启动 PID=$FRONTEND_PID → http://localhost:5173"

echo ""
echo "✅ 启动完成"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "   接口文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

wait

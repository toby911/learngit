from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

app = FastAPI()

# 定义基本身份验证模式
security = HTTPBasic()

# 在这里设置您的静态文件目录
BASE_DOCS_DIR = "static"

# 定义一个权限检查函数
async def check_credentials(request: Request):
    credentials = None
    try:
        # 从请求中提取凭据
        credentials = await security(request)
    except HTTPException as e:
        pass

    if credentials and credentials.username == "user" and credentials.password == "password":
        return True
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")

# 定义一个中间件来处理静态文件请求
class StaticFilesAuthorizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/static"):
            try:
                # 在访问静态文件之前检查权限
                await check_credentials(request)
            except HTTPException as e:
                return Response(status_code=e.status_code, content=e.detail)
        return await call_next(request)

# 将中间件添加到应用程序中
app.add_middleware(StaticFilesAuthorizationMiddleware)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=BASE_DOCS_DIR), name="static")

# 示例路由
@app.get("/")
def read_root():
    return {"Hello": "World"}

# 受保护的 API 接口示例
@app.get("/protected")
async def protected_api(permissions: bool = Depends(check_credentials)):
    return {"message": "You have access to this protected API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

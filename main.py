from contextlib import asynccontextmanager
import time
from prometheus_fastapi_instrumentator import Instrumentator, metrics

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis
from sqladmin import Admin

from admin.auth import authentication_backend
from admin.views import BookingsAdmin, UserAdmin
from booking.router import router as router_bookings
from config import settings
from database import engine
from hotels.router import router as router_hotels
from hotels.rooms.router import router as router_rooms
from images.router import router as router_images
from importer.router import router as router_import
from logger import logger
from pages.router import router as router_pages
from users.router import router_auth, router_users
import sentry_sdk
from fastapi_versioning import VersionedFastAPI, version

app = FastAPI(
    title="Бронирование Отелей",
    version="0.1.0",
    root_path="/api",
)

if settings.MODE != "TEST":
    sentry_sdk.init(
        dsn="https://d8267cf85de3b7eec783f6b8dda567a1@o4507346394939392.ingest.de.sentry.io/4507346398871632",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
    )






# Включение основных роутеров
app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_bookings)
app.include_router(router_import)


# Включение дополнительных роутеров
app.include_router(router_images)



# Подключение CORS, чтобы запросы к API могли приходить из браузера
origins = [
    # 3000 - порт, на котором работает фронтенд на React.js
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin",
                   "Authorization"],
)


# Замена устаревших @app.on_event("startup") и @app.on_event("shutdown")
# в единую функцию lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # при запуске
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield
    # при выключении




app.include_router(router_pages)

if settings.MODE == "TEST":
    # При тестировании через pytest, необходимо подключать Redis, чтобы кэширование работало.
    # Иначе декоратор @cache из библиотеки fastapi-cache ломает выполнение кэшируемых эндпоинтов.
    # Из этого следует вывод, что сторонние решения порой ломают наш код, и это бывает проблематично поправить.
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")


app = VersionedFastAPI(app,
    version_format='{major}',
    prefix_format='/v{major}',
   # description='Greet users with a nice message',
   # middleware=[
    #    Middleware(SessionMiddleware, secret_key='mysecretkey')
    #]
)


instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app).expose(app)

# Подключение админки
admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UserAdmin)
admin.add_view(BookingsAdmin)

app.mount("/static", StaticFiles(directory="static"), "static")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # При подключении Prometheus + Grafana подобный лог не требуется
    logger.info("Request handling time", extra={
        "process_time": round(process_time, 4)
    })
    return response



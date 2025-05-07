# app/const/APPServiceContext.py

class AppServiceContext:
    _app = None

    def __init__(self, app):
        AppServiceContext._app = app  # 静态注册

    @staticmethod
    def get_app():
        if AppServiceContext._app is None:
            raise ValueError("AppServiceContext not initialized with an app.")
        return AppServiceContext._app

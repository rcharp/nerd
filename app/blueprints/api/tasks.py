from app.app import create_celery_app

celery = create_celery_app()


@celery.task()
def new_task():
    return

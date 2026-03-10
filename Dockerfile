FROM public.ecr.aws/lambda/python:3.10

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install --no-cache-dir -r requirements.txt

COPY app ${LAMBDA_TASK_ROOT}/app

CMD ["app.main.handler"]
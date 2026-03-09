FROM public.ecr.aws/lambda/python:3.10

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ${LAMBDA_TASK_ROOT}/app/

CMD ["app.main.handler"]
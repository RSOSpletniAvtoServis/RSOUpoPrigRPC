FROM mangart1995/rsosceleton:latest

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy app code
COPY . ./app

EXPOSE 50051

CMD ["python", "upoprigrpc.py"]
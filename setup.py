from setuptools import find_packages, setup

setup(
    name="mcp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.109.2",
        "uvicorn>=0.27.1",
        "streamlit>=1.31.1",
        "langchain>=0.1.9",
        "langchain-openai>=0.0.8",
        "papermill>=2.4.0",
        "jupyter>=1.0.0",
        "nbformat>=5.10.0",
        "psycopg2-binary>=2.9.9",
        "redis>=5.0.1",
        "python-dotenv>=1.0.1",
        "pydantic>=2.6.1",
        "python-multipart>=0.0.9",
    ],
    python_requires=">=3.8",
)

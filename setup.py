from setuptools import setup

setup(
    name="ai-habit-rewriter",
    version="1.0.0",
    description="AI-powered tool to convert goals into SMART habit plans",
    author="AI Habit Rewriter",
    packages=["."],
    install_requires=[
        "gradio>=4.0.0,<6.0.0",
        "transformers>=4.20.0,<5.0.0",
        "torch>=1.12.0,<3.0.0",
        "fpdf>=1.7.0,<3.0.0",
    ],
    python_requires=">=3.8",
) 
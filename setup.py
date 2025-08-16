from setuptools import setup

setup(
    name="ai-habit-rewriter",
    version="1.0.0",
    description="AI-powered tool to convert goals into SMART habit plans",
    author="AI Habit Rewriter",
    packages=["."],
    install_requires=[
        "gradio>=5.0.0",
        "transformers>=4.0.0",
        "torch>=1.0.0",
        "fpdf>=1.7.0",
    ],
    python_requires=">=3.8",
) 
# AI Habit Rewriter (SMART)

An AI-powered web application that converts vague goals into SMART (Specific, Measurable, Achievable, Relevant, Time-bound) habit plans using machine learning.

## 🚀 Features

- **AI-Powered Generation**: Uses Flan-T5-Large model to generate personalized habit plans
- **Three Variations**: Get V1 (simple), V2 (alternative), and V3 (creative) approaches for each goal
- **Interactive Interface**: Clean Gradio web interface for easy interaction
- **PDF Export**: Download your generated habit plans as PDF files
- **Editable Output**: Modify and customize generated habits before exporting

## 📋 Prerequisites

- Python 3.8 or higher
- Conda (recommended) or pip
- At least 4GB RAM (for AI model loading)

## 🛠️ Installation

### Option 1: Using Conda (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Yildirimm/ai-habit-rewriter.git
   cd ai-habit-rewriter
   ```

2. **Create and activate conda environment:**
   ```bash
   conda env create -f environment.yml
   conda activate ai-habit-rewriter
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

### Option 2: Using pip

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Yildirimm/ai-habit-rewriter.git
   cd ai-habit-rewriter
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

## 🎯 Usage

1. **Enter your goal** in the text field (e.g., "I want to lose weight")
2. **Click "Generate My Habits (3 Variants)"** to create three different approaches
3. **Switch between V1, V2, and V3** to see different habit strategies
4. **Edit the content** if needed in the output area
5. **Export as PDF** to save your habit plan

## 📁 Project Structure

```
ai-habit-rewriter/
├── app.py              # Main Gradio web application
├── utils.py            # AI processing and PDF export functions
├── prompts.py          # AI prompts and variation styles
├── requirements.txt    # Python dependencies
├── environment.yml     # Conda environment
├── setup.py           # Package setup
└── README.md          # This file
```

## 🔧 Configuration

The application uses the **Flan-T5-Large** model by default. You can modify the model in `utils.py`:

```python
MODEL_ID = "google/flan-t5-large"  # Change this to use a different model
```

## 🚨 Troubleshooting

### Common Issues:

1. **Model loading fails:**
   - Ensure you have at least 4GB RAM available
   - Try using a smaller model like `google/flan-t5-base`

2. **Dependencies not found:**
   - Make sure you're in the correct conda environment
   - Run `pip install -r requirements.txt` again

3. **Gradio interface not loading:**
   - Check if port 7860 is available
   - The app will automatically find an available port

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Gradio** for the web interface
- **Hugging Face Transformers** for the AI models
- **Flan-T5** model for habit generation

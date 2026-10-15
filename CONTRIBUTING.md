# Contributing Guidelines

Thank you for your interest in contributing to **Flappy Bird Using Hand Gestures**!  
We welcome improvements, bug reports, feature requests, and code contributions.

---

## 🛠️ Development Setup

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/jonkolp/Handy-Bird.git
   cd Handy-Bird
   ```

2. **Python Environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\Activate.ps1
   # macOS/Linux:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Unity Editor**:
   - Open the project directory with **Unity 2021.3 LTS** or newer.
   - Load [`Assets/Assignment.unity`](Assets/Assignment.unity).

---

## 🔄 Contribution Workflow

1. **Branching**:
   Create a descriptive branch for your work:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Coding Standards**:
   - **Python ([`MP.py`](MP.py))**: Follow **PEP 8** style guidelines. Keep functions modular, type-hinted where appropriate, and documented with docstrings.
   - **C# ([`Assets/Bird.cs`](Assets/Bird.cs))**: Follow standard Unity C# conventions:
     - PascalCase for methods and classes.
     - camelCase for local variables and private fields.
     - Use `[SerializeField]` with private fields for inspector exposure.
     - Provide `[Tooltip]` and `[Header]` for editor clarity.

3. **Testing**:
   - Run `python -m py_compile MP.py` to ensure Python code is syntactically sound.
   - Test camera and hand tracking across varying light conditions.
   - Test Unity gameplay in Editor Play mode to verify physics responsiveness and network reconnect behavior.

4. **Commit Messages**:
   Use clear, conventional commit messages:
   - `feat: add procedural pipe spawning system`
   - `fix: resolve socket reconnect timeout on scene reload`
   - `docs: update setup steps for macOS`

5. **Submitting a Pull Request**:
   - Push your branch to GitHub.
   - Open a PR against the `master` / `main` branch.
   - Describe what changed and reference any relevant issues or items from [**ROADMAP.md**](ROADMAP.md).

---

## 💡 Where to Start?

Check out our [**ROADMAP.md**](ROADMAP.md) for prioritized features seeking contributions:
- Transitioning socket communication to UDP.
- Procedural obstacle generation & object pooling.
- Retro sound effects and background music.
- Multi-gesture input (pinch, thumbs up).

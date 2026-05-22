"""Pre-checks locales para `arkanum check <N> --dry-run`.

Cada módulo `qNN.py` expone una función `checks(quest)` que devuelve una
lista de `PreCheckResult`. El runner los descubre por número de quest y los
ejecuta sin invocar Gemini.
"""

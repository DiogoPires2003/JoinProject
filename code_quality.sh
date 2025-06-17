#!/bin/bash

echo "🔍 1. Complejidad ciclomática (radon)"
radon cc . -a -nc

echo -e "\n📉 2. Índice de mantenibilidad (radon)"
radon mi . -nc

echo -e "\n⚠️ 3. Estilo y errores de código (flake8)"
flake8 .

echo -e "\n🛡️ 4. Análisis de seguridad (bandit)"
bandit -r .

echo -e "\n🧪 5. Cobertura de pruebas (coverage)"
coverage run -m pytest && coverage report

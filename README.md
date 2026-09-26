# CHASSI - CRM (MVP)

> **Sistema de Priorização e Gestão de Chamados Operacionais**

O **CHASSI - CRM** é uma aplicação web desenvolvida para otimizar e padronizar o recebimento, triagem e priorização de solicitações operacionais enviadas às equipas de Engenharia e Produto. A solução utiliza o cálculo automatizado da matriz **Score RICE** ($RICE = \frac{\text{Alcance} \times \text{Impacto} \times \text{Confiança}}{\text{Esforço}}$) para eliminar ambiguidades e orientar a tomada de decisão com base no valor de negócio.

---

## 📌 Funcionalidades Principais

- **Autenticação Segura:** Controlo de acesso de utilizadores (solicitantes e analistas) utilizando tokens JWT e hashing de palavras-passe com `bcrypt`.
- **Registo de Chamados com Cálculo RICE:** Formulário estruturado para submissão de solicitações com cálculo automático do Score RICE em tempo real.
- **Quadro de Backlog Priorizado (Kanban):** Exibição de chamados ordenados do maior para o menor Score RICE.
- **Gestão do Ciclo de Vida:** Atualização do estado dos chamados (*Pendente*, *Em Andamento*, *Concluído*).
- **Acessibilidade Inclusiva (WCAG 2.1 AA):** Navegação por teclado, alto contraste e sinalização dupla de estado (cor, texto e ícone).

---

## 🛠️ Tecnologias Utilizadas

### **Backend**
- **Linguagem:** Python 3.11+
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Autenticação:** PyJWT, Passlib (bcrypt)
- **Validação de Dados:** Pydantic

### **Frontend**
- **Interface:** HTML5, JavaScript (ES6+), Tailwind CSS

### **Banco de Dados**
- **SGBD:** SQLite (ambiente de desenvolvimento/MVP)

---

## 🚀 Como Executar o Projeto Localmente

### **Pré-requisitos**
- Python 3.11 ou superior instalado
- Git instalado

### **Passos para Instalação**

1. **Clonar o repositório:**
   ```bash
   git clone [https://github.com/SEU-USUARIO/NOME-DO-SEU-REPOSITORIO.git](https://github.com/SEU-USUARIO/NOME-DO-SEU-REPOSITORIO.git)
   cd NOME-DO-SEU-REPOSITORIO

# Hollow Mooni

**Plataforma / Souls‑like 2D feito em Python, principalmente a biblioteca Pygame**

---

## Descrição do Projeto

Hollow Mooni é um jogo 2D de ação e aventura inspirado em *Hollow Knight* e outros títulos do gênero. Você controla **Mooni**, um antigo rei de um reino próspero, o qual veio a perecer diante de uma maldição que obrigou seu povo a defender eternamente um rei que não existe mais. Dessa forma, Mooni retorna em outra forma para libertar seu povo da maldição. O projeto foi desenvolvido para a disciplina de Desenvolvimento de Software (Insper) e tem como objetivos estudar:

* Estruturação de projetos em Pygame
* Sistema de salas e transições («room system»)
* Gerenciamento de ondas de inimigos («wave manager»)
* Lógica de IA básica (patrulha, perseguição, ataques)
* Organização de recursos (sprites, sons, mapas) e créditos de licença livre

---

## Autores e respectivos usuários no git
João Henrique Mattar  @joaoham                      
Henrique Benclowicz   @broadercrane22                
Henrique Abreu        @betokique031     

---

## Requisitos

* **Python 3.10+** (testado na versão 3.11)
* **Pygame >= 2.5.0**

Instale as dependências com:

```bash
pip install -r requirements.txt
```

 Obs: Se preferir, crie um ambiente virtual com `python -m venv .venv` e ative‑o antes de instalar os pacotes.

---

## Como Executar

O ponto de entrada do jogo é o arquivo **`main.py`** na raiz do projeto.

```bash
python main.py
```

Se tudo estiver configurado corretamente, uma janela 1280×720 será aberta com a tela inicial. Pressione **Enter** para começar e divirta‑se!

---

## Controles Padrão

| Tecla      | Ação                     |
| ---------- | ------------------------ |
| **A / D**  | Movimento ← / →          |
| **Espaço** | Pular                    |
| **Q**      | Ataque *Thrust*          |
| **R**      | Ataque *Smash*           |
| **Esc**    | Pausar / Sair            |


---

## Estrutura de Pastas (resumo)

```
HollowMooni/
├─ assets/
│  ├─ enemies/
│  │  ├─ knight/
│  │  ├─ skeleton/
│  │  └─ ...
│  ├─ player/
│  └─ sounds/
├─ core/
│  ├─ player.py
│  ├─ knight_boss.py
│  ├─ room_manager.py
│  └─ ...
├─ README.md
└─ main.py  ← arquivo a executar
```

---

## Créditos de Arte & Animações (Personagem / Autor / Link)

Todo o conteúdo de sprites foi obtido em *itch.io* sob licenças permissivas para uso em projetos pessoais/educacionais:

Esqueletos / Jesse M. / https://jesse-m.itch.io/skeleton-pack

NightBorne / CreativeKind / https://creativekind.itch.io/nightborne-warrior

Knight / Szadi Art / https://szadiart.itch.io/2d-soulslike-character

Bringer of Death / Clembod / https://clembod.itch.io/bringer-of-death-free

Little Mooni / Jess Hiyoo / https://jesshiyoo.itch.io/llittle-mooni


Todos os direitos permanecem com seus respectivos autores.

---

## Vídeo com gameplay (não foi possivel gravar com audio)

https://youtu.be/uvt5rGRDp54
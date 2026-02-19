import time
import random
import streamlit as st

st.set_page_config(page_title="Calcul Mental", layout="centered")

# =========================
#  STATE
# =========================
def init_state():
    defaults = {
        "started": False,
        "countdown": 3,
        "a": 0,
        "b": 0,
        "op": "+",
        "correct": 0,
        "score": 0,
        "mistakes": 0,
        "total": 10,
        "index": 0,
        "difficulty": "facile",
        "mode": "mix",
        "last_feedback": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# =========================
#  HELPERS
# =========================
def ranges(d):
    if d == "facile":
        return 1, 10
    if d == "moyen":
        return 5, 30
    return 10, 60

def pick_op(m):
    if m == "add":
        return "+"
    if m == "sub":
        return "-"
    if m == "mul":
        return "*"
    return random.choice(["+", "-", "*"])

def compute(a, b, op):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    return a * b

def new_question():
    lo, hi = ranges(st.session_state.difficulty)
    a = random.randint(lo, hi)
    b = random.randint(lo, hi)
    op = pick_op(st.session_state.mode)

    # éviter les négatifs en facile/moyen
    if op == "-" and st.session_state.difficulty != "difficile" and b > a:
        a, b = b, a

    st.session_state.a = a
    st.session_state.b = b
    st.session_state.op = op
    st.session_state.correct = compute(a, b, op)

def reset_game():
    st.session_state.started = True
    st.session_state.countdown = 3
    st.session_state.score = 0
    st.session_state.mistakes = 0
    st.session_state.index = 0
    st.session_state.last_feedback = ""
    new_question()

def stop_game():
    st.session_state.started = False
    st.session_state.countdown = 3
    st.session_state.last_feedback = "🛑 Partie arrêtée."

# =========================
#  UI
# =========================
st.title("🧠 Calcul Mental (version site)")

# Bouton STOP en haut à droite (simulé avec colonnes)
top_left, top_right = st.columns([7, 3])
with top_right:
    if st.button("↗ STOP", use_container_width=True):
        stop_game()
        st.rerun()

st.caption("Choisis tes réglages puis lance une partie.")

col1, col2 = st.columns(2)
with col1:
    st.session_state.difficulty = st.selectbox(
        "Difficulté",
        ["facile", "moyen", "difficile"],
        index=["facile", "moyen", "difficile"].index(st.session_state.difficulty),
    )
with col2:
    st.session_state.mode = st.selectbox(
        "Opérations",
        ["add", "sub", "mul", "mix"],
        index=["add", "sub", "mul", "mix"].index(st.session_state.mode),
        format_func=lambda x: {"add": "Addition", "sub": "Soustraction", "mul": "Multiplication", "mix": "Mix"}[x],
    )

st.session_state.total = st.slider("Nombre de questions", 5, 50, st.session_state.total)

btn1, btn2 = st.columns(2)
with btn1:
    if st.button("▶ Démarrer", use_container_width=True):
        reset_game()
        st.rerun()

with btn2:
    # bouton EXIT rouge (ferme pas Windows mais stoppe l'app côté “site”)
    if st.button("⛔ EXIT", use_container_width=True):
        st.session_state.started = False
        st.session_state.last_feedback = "⛔ Exit."
        st.stop()

st.divider()

# Feedback
if st.session_state.last_feedback:
    st.info(st.session_state.last_feedback)

# =========================
#  GAME
# =========================
if not st.session_state.started:
    st.warning("En attente… Clique sur **Démarrer**.")
else:
    # Countdown 3..2..1..GO!
    if st.session_state.countdown > 0:
        st.markdown(f"<h1 style='text-align:center;'>{st.session_state.countdown}</h1>", unsafe_allow_html=True)
        time.sleep(1)
        st.session_state.countdown -= 1
        st.rerun()

    elif st.session_state.countdown == 0:
        st.markdown("<h1 style='text-align:center; color:orange;'>GO!</h1>", unsafe_allow_html=True)
        time.sleep(0.6)
        st.session_state.countdown -= 1
        st.rerun()

    else:
        st.subheader(f"Question {st.session_state.index + 1} / {st.session_state.total}")

        st.markdown(
            f"<h2 style='text-align:center;'>{st.session_state.a} {st.session_state.op} {st.session_state.b} = ?</h2>",
            unsafe_allow_html=True,
        )

        answer = st.text_input("Ta réponse", key="answer_input")

        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            if st.button("✅ Valider", use_container_width=True):
                try:
                    ok = int(answer) == st.session_state.correct
                except Exception:
                    ok = False

                if ok:
                    st.session_state.score += 1
                    st.session_state.last_feedback = "✅ Bien joué !"
                else:
                    st.session_state.mistakes += 1
                    st.session_state.last_feedback = f"❌ Faux ! Réponse : {st.session_state.correct}"

                st.session_state.index += 1
                st.session_state.answer_input = ""

                if st.session_state.index >= st.session_state.total:
                    st.session_state.started = False
                    st.session_state.last_feedback = f"🎉 Terminé ! Score: {st.session_state.score} | Erreurs: {st.session_state.mistakes}"
                else:
                    new_question()

                time.sleep(0.6)
                st.rerun()

        with c2:
            st.metric("Score", st.session_state.score)

        with c3:
            st.metric("Erreurs", st.session_state.mistakes)
